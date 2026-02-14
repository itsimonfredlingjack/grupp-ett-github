#!/usr/bin/env python3
"""Parse Jules review findings and create standalone Jira tickets.

One-way async push: Jules → Jira. No AI-to-AI conversation.
Jira acts as firewall — Claude picks up tickets via normal Ralph Loop
without knowing Jules created them.

KEY DESIGN: Tickets are standalone Tasks, NOT sub-tasks. This avoids
the race condition where parent ticket is already Done when Jules
finishes its async review. The origin PR/ticket is referenced in
the description only.

Uses only stdlib + local jira_client. No pip install needed in CI.

Environment variables:
    JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN — Jira credentials
    HEAD_REF — Branch name (e.g., feature/GE-35-description)
    JULES_REVIEW_BODY — Full Jules review comment body (from previous step)
    PR_NUMBER — PR number for logging
"""

from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

# Allow importing jira_client from src/
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.sejfa.integrations.jira_client import (
    JiraAPIError,
    JiraClient,
    JiraConfig,
)

MAX_TASKS = 3
SEVERITY_PATTERN = re.compile(
    r"\[(?P<severity>HIGH|MEDIUM|LOW|CRITICAL)\]\s+"
    r"(?P<location>\S+)"
    r"\s*[—–-]\s*"
    r"(?P<description>.+)",
    re.IGNORECASE,
)
TICKET_KEY_PATTERN = re.compile(r"([A-Z]+-\d+)")


@dataclass
class Finding:
    """A single parsed Jules review finding."""

    severity: str
    location: str
    description: str

    @property
    def summary(self) -> str:
        """Generate Jira-friendly summary (max 255 chars)."""
        return f"[Jules/{self.severity}] {self.location}: {self.description}"[:255]

    def body(self, origin_key: str | None = None, pr_number: str = "") -> str:
        """Generate description body for Jira ticket.

        Args:
            origin_key: Original Jira ticket key (e.g., GE-35)
            pr_number: PR number that triggered the review
        """
        lines = [
            f"Severity: {self.severity}",
            f"Location: {self.location}",
            f"Description: {self.description}",
            "",
            "Source: Automated Jules code review",
        ]
        if origin_key or pr_number:
            lines.append("")
            lines.append("Origin:")
            if origin_key:
                lines.append(f"  Ticket: {origin_key}")
            if pr_number:
                lines.append(f"  PR: #{pr_number}")
        return "\n".join(lines)


def _log(msg: str, level: str = "notice") -> None:
    print(f"::{level}::{msg}" if level != "notice" else msg, flush=True)


def parse_findings(review_body: str) -> list[Finding]:
    """Extract structured findings from Jules review text.

    Looks for lines matching: [SEVERITY] file:line — description
    """
    findings: list[Finding] = []

    for line in review_body.splitlines():
        line = line.strip()
        if not line:
            continue

        match = SEVERITY_PATTERN.search(line)
        if match:
            findings.append(
                Finding(
                    severity=match.group("severity").upper(),
                    location=match.group("location").strip(),
                    description=match.group("description").strip(),
                )
            )

    return findings


def extract_parent_key(head_ref: str) -> str | None:
    """Extract Jira ticket key from branch name.

    Examples:
        feature/GE-35-add-auth -> GE-35
        fix/GE-102-bug -> GE-102
        GE-50-description -> GE-50
    """
    match = TICKET_KEY_PATTERN.search(head_ref)
    return match.group(1) if match else None


def extract_project_key(parent_key: str) -> str:
    """Extract project key from issue key. GE-35 -> GE."""
    return parent_key.split("-")[0]


def create_tasks(
    client: JiraClient,
    origin_key: str,
    findings: list[Finding],
    pr_number: str = "",
) -> list[str]:
    """Create standalone Jira Tasks for HIGH severity findings.

    Standalone Tasks (not Sub-tasks) avoid the race condition where
    the parent ticket is already Done when Jules finishes its async
    review. The origin ticket is referenced in the description only.

    Args:
        client: Configured JiraClient
        origin_key: Origin issue key for reference (e.g., GE-35)
        findings: List of parsed findings
        pr_number: PR number for origin reference

    Returns:
        List of created issue keys
    """
    project_key = extract_project_key(origin_key)
    high_findings = [f for f in findings if f.severity in ("HIGH", "CRITICAL")]

    if not high_findings:
        _log("No HIGH/CRITICAL findings — skipping task creation")
        return []

    to_create = high_findings[:MAX_TASKS]
    if len(high_findings) > MAX_TASKS:
        _log(f"Found {len(high_findings)} HIGH findings, capping at {MAX_TASKS} tasks")

    created_keys: list[str] = []

    for finding in to_create:
        try:
            issue = client.create_issue(
                project_key=project_key,
                summary=finding.summary,
                description=finding.body(origin_key, pr_number),
                issue_type="Task",
                labels=["jules-review", "automated"],
            )
            created_keys.append(issue.key)
            _log(f"Created {issue.key}: {finding.summary[:80]}")
        except JiraAPIError as exc:
            _log(f"Failed to create task: {exc}", "warning")

    return created_keys


def add_low_findings_as_comment(
    client: JiraClient,
    parent_key: str,
    findings: list[Finding],
) -> bool:
    """Add LOW/MEDIUM findings as a comment on the parent ticket."""
    low_medium = [f for f in findings if f.severity in ("LOW", "MEDIUM")]

    if not low_medium:
        return False

    lines = ["Jules review — lower-severity findings:\n"]
    for f in low_medium:
        lines.append(f"• [{f.severity}] {f.location} — {f.description}")

    try:
        client.add_comment(parent_key, "\n".join(lines))
        _log(f"Added {len(low_medium)} LOW/MEDIUM findings as comment on {parent_key}")
        return True
    except JiraAPIError as exc:
        _log(f"Failed to add comment: {exc}", "warning")
        return False


def main() -> int:
    head_ref = os.environ.get("HEAD_REF", "").strip()
    review_body = os.environ.get("JULES_REVIEW_BODY", "").strip()
    pr_number = os.environ.get("PR_NUMBER", "")

    if not review_body:
        _log("JULES_REVIEW_BODY is empty — nothing to process")
        return 0

    parent_key = extract_parent_key(head_ref)
    if not parent_key:
        _log(
            f"Could not extract ticket key from branch '{head_ref}'. "
            "Expected format: feature/GE-XXX-description"
        )
        return 0

    _log(f"Processing Jules findings for {parent_key} (PR #{pr_number})")

    # Parse findings
    findings = parse_findings(review_body)
    if not findings:
        _log("No structured findings found in Jules review")
        return 0

    high_count = sum(1 for f in findings if f.severity in ("HIGH", "CRITICAL"))
    low_count = sum(1 for f in findings if f.severity in ("LOW", "MEDIUM"))
    _log(
        f"Found {len(findings)} findings: "
        f"{high_count} HIGH/CRITICAL, {low_count} LOW/MEDIUM"
    )

    # Initialize Jira client
    try:
        config = JiraConfig.from_env()
        client = JiraClient(config)
    except ValueError as exc:
        _log(f"Jira config error: {exc}", "error")
        return 1

    # Create standalone tasks for HIGH severity
    created = create_tasks(client, parent_key, findings, pr_number)
    if created:
        _log(f"Created {len(created)} tasks: {', '.join(created)}")

    # Add LOW/MEDIUM as comment
    add_low_findings_as_comment(client, parent_key, findings)

    # Write output for downstream steps
    github_output = os.environ.get("GITHUB_OUTPUT", "")
    if github_output:
        with open(github_output, "a") as f:
            f.write(f"tasks_created={len(created)}\n")
            f.write(f"task_keys={','.join(created)}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
