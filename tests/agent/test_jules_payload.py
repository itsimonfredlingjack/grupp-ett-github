"""Tests for scripts/jules_payload.py."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

SCRIPT_PATH = Path("scripts/jules_payload.py")

spec = importlib.util.spec_from_file_location("jules_payload", SCRIPT_PATH)
assert spec is not None
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def _run(cmd: list[str], cwd: Path) -> None:
    subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)


def _init_git_repo(tmp_path: Path) -> None:
    _run(["git", "init"], cwd=tmp_path)
    _run(["git", "config", "user.email", "tests@example.com"], cwd=tmp_path)
    _run(["git", "config", "user.name", "Test User"], cwd=tmp_path)


def test_mask_line_redacts_sensitive_values() -> None:
    line = "Authorization: Bearer abcdefghijklmnop"
    assert "[REDACTED]" in module.mask_line(line)


def test_is_excluded_path_filters_vendor_and_binaries() -> None:
    assert module.is_excluded_path("vendor/pkg/file.py")
    assert module.is_excluded_path("assets/logo.png")
    assert not module.is_excluded_path("src/sejfa/core/admin_auth.py")


def test_build_compact_diff_prefers_larger_files(tmp_path: Path, monkeypatch) -> None:
    _init_git_repo(tmp_path)

    small = tmp_path / "small.py"
    large = tmp_path / "large.py"
    initial_large = "\n".join([f"value_{i} = {i}" for i in range(20)]) + "\n"
    changed_large = "\n".join([f"value_{i} = {i + 1}" for i in range(20)]) + "\n"

    small.write_text("x = 1\n", encoding="utf-8")
    large.write_text(initial_large, encoding="utf-8")

    _run(["git", "add", "."], cwd=tmp_path)
    _run(["git", "commit", "-m", "initial"], cwd=tmp_path)
    base_sha = subprocess.check_output(
        ["git", "rev-parse", "HEAD"],
        cwd=tmp_path,
        text=True,
    ).strip()

    small.write_text("x = 2\n", encoding="utf-8")
    large.write_text(changed_large, encoding="utf-8")
    _run(["git", "add", "."], cwd=tmp_path)
    _run(["git", "commit", "-m", "change"], cwd=tmp_path)
    head_sha = subprocess.check_output(
        ["git", "rev-parse", "HEAD"],
        cwd=tmp_path,
        text=True,
    ).strip()

    monkeypatch.chdir(tmp_path)
    budget = module.ProfileBudget(
        max_diff_chars=4000,
        max_log_lines=50,
        max_context_chars=2000,
        max_files=1,
        max_hunks_per_file=5,
        max_error_snippets=5,
    )

    diff, patch_index, files_changed_count = module.build_compact_diff(
        base_sha=base_sha,
        head_sha=head_sha,
        budget=budget,
    )

    assert files_changed_count == 2
    assert patch_index[0]["path"] == "large.py"
    assert "FILE: large.py" in diff


def test_trim_context_limits_payload_size() -> None:
    context = {
        "compact_diff": "A" * 1000,
        "error_snippets": ["B" * 200, "C" * 200],
    }

    trimmed = module.trim_context(context, max_chars=280)
    serialized = module.json.dumps(trimmed, ensure_ascii=True, separators=(",", ":"))

    assert len(serialized) <= 280
