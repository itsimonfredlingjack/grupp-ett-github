# Deployment Guide - grupp-ett-github

> **CRITICAL**: This document preserves deployment context across Claude Code session compactions.

## Production Environment

**Live URL:** https://gruppett.fredlingautomation.dev
**Infrastructure:** Cloudflare Tunnel → Flask App (localhost:5000)
**Server:** Local development machine (not cloud-hosted)

---

## Cloudflare Tunnel Configuration

### Overview

This project uses **Cloudflare Tunnel** (cloudflared) to expose the local Flask application to the internet via a secure tunnel. The production URL is NOT served from a cloud provider - it tunnels directly to localhost:5000 on the development machine.

### Tunnel Details

| Property | Value |
|----------|-------|
| **Tunnel ID** | `62457ea9-f9a2-4391-a904-f2e061920674` |
| **Config File** | `/home/aidev/.cloudflared/config-gruppett.yml` |
| **Hostname** | `gruppett.fredlingautomation.dev` |
| **Local Service** | `http://localhost:5000` |
| **Credentials** | `/home/aidev/.cloudflared/62457ea9-f9a2-4391-a904-f2e061920674.json` |

### Configuration File

Location: `/home/aidev/.cloudflared/config-gruppett.yml`

```yaml
tunnel: 62457ea9-f9a2-4391-a904-f2e061920674
credentials-file: /home/aidev/.cloudflared/62457ea9-f9a2-4391-a904-f2e061920674.json

ingress:
  - hostname: gruppett.fredlingautomation.dev
    service: http://localhost:5000
  - service: http_status:404
```

---

## Starting the Application

### Full Startup Sequence

```bash
# 1. Navigate to project
cd /home/aidev/grupp-ett-github

# 2. Activate virtual environment
source venv/bin/activate

# 3. Start Flask app (if not running)
python3 app.py &

# 4. Start Cloudflare Tunnel (if not running)
nohup /home/aidev/.local/bin/cloudflared tunnel \
  --config /home/aidev/.cloudflared/config-gruppett.yml \
  run 62457ea9-f9a2-4391-a904-f2e061920674 \
  > /tmp/cloudflared-gruppett.log 2>&1 &
```

### Quick Health Check

```bash
# Check if Flask is running
ps aux | grep "python3 app.py" | grep -v grep

# Check if tunnel is running
ps aux | grep "62457ea9-f9a2-4391-a904-f2e061920674" | grep -v grep

# Test local endpoint
curl http://localhost:5000/hello

# Test production URL
curl https://gruppett.fredlingautomation.dev/hello
```

---

## Troubleshooting

### Error 1033: Cloudflare Tunnel Error

**Symptom:** Visiting https://gruppett.fredlingautomation.dev shows "Error 1033 - Cloudflare Tunnel error"

**Cause:** The cloudflared tunnel process is not running or cannot reach localhost:5000

**Solution:**

1. **Check if Flask is running:**
   ```bash
   ps aux | grep "python3 app.py" | grep -v grep
   ```
   If not running, start it:
   ```bash
   cd /home/aidev/grupp-ett-github && python3 app.py &
   ```

2. **Check if tunnel is running:**
   ```bash
   ps aux | grep "62457ea9-f9a2-4391-a904-f2e061920674" | grep -v grep
   ```
   If not running, start it:
   ```bash
   nohup /home/aidev/.local/bin/cloudflared tunnel \
     --config /home/aidev/.cloudflared/config-gruppett.yml \
     run 62457ea9-f9a2-4391-a904-f2e061920674 \
     > /tmp/cloudflared-gruppett.log 2>&1 &
   ```

3. **Check tunnel logs:**
   ```bash
   tail -50 /tmp/cloudflared-gruppett.log
   ```
   Look for:
   - ✅ `Registered tunnel connection` - tunnel connected to Cloudflare
   - ❌ Connection errors - network or config issues

4. **Verify local service is responding:**
   ```bash
   curl http://localhost:5000/hello
   ```
   If this fails, Flask is not running or crashed.

### Other Cloudflare Tunnels Running

The server runs multiple tunnels for different projects:

```bash
# List all running tunnels
ps aux | grep cloudflared | grep -v grep
```

Expected tunnels:
- **gruppett** (62457ea9...) → localhost:5000 → gruppett.fredlingautomation.dev
- **github-mcp** (fd38a550...) → localhost:8005 → git.fredlingautomation.dev
- **simonsagentic** (0aaa6c91...) → localhost:8004 → simonsagentic.fredlingautomation.dev

**IMPORTANT:** Do NOT kill all cloudflared processes - only restart the specific tunnel that's broken.

### Tunnel Won't Start

If `cloudflared` command fails:

1. **Check cloudflared is installed:**
   ```bash
   which cloudflared
   # Should output: /home/aidev/.local/bin/cloudflared
   ```

2. **Check credentials file exists:**
   ```bash
   ls -la /home/aidev/.cloudflared/62457ea9-f9a2-4391-a904-f2e061920674.json
   ```

3. **Test tunnel manually (foreground):**
   ```bash
   /home/aidev/.local/bin/cloudflared tunnel \
     --config /home/aidev/.cloudflared/config-gruppett.yml \
     run 62457ea9-f9a2-4391-a904-f2e061920674
   ```
   Press Ctrl+C to stop, then restart in background.

---

## Deployment Workflow

### Deploying Code Changes

**There is NO separate deployment step!** Changes pushed to `main` branch are immediately live because:

1. The Flask app runs from the local working directory (`/home/aidev/grupp-ett-github`)
2. Cloudflare Tunnel forwards traffic to `localhost:5000`
3. When you `git pull` or `git merge`, the code updates on disk
4. Flask serves the updated files immediately

### Applying Changes

```bash
# 1. Merge changes to main
git checkout main
git pull origin main
git merge feature/your-branch
git push origin main

# 2. Restart Flask (if needed for code changes)
pkill -f "python3 app.py"
python3 app.py &

# 3. Verify
curl https://gruppett.fredlingautomation.dev/hello
```

**Static files** (like `static/monitor.html`) are served directly - no restart needed!

### Rolling Back

```bash
# 1. Revert to previous commit
git checkout main
git reset --hard HEAD~1  # or specific commit hash
git push origin main --force

# 2. Restart Flask
pkill -f "python3 app.py"
python3 app.py &
```

---

## Monitoring

### Check Application Status

```bash
# Flask process
ps aux | grep "python3 app.py" | grep -v grep

# Tunnel process
ps aux | grep "62457ea9-f9a2-4391-a904-f2e061920674" | grep -v grep

# Flask logs (if running in foreground)
tail -f /var/log/gruppett/flask.log  # if configured

# Tunnel logs
tail -f /tmp/cloudflared-gruppett.log
```

### Test Endpoints

```bash
# Health check
curl https://gruppett.fredlingautomation.dev/hello

# Monitor dashboard
curl https://gruppett.fredlingautomation.dev/static/monitor.html

# API endpoint
curl https://gruppett.fredlingautomation.dev/api/monitor/state
```

---

## Important Notes for Claude Code

> **Context Preservation:** When this session is compacted, remember:
>
> 1. **gruppett.fredlingautomation.dev is NOT localhost** - it's tunneled via Cloudflare
> 2. **Error 1033 = tunnel down** - check cloudflared process, NOT Flask
> 3. **No separate deploy step** - `git pull` + Flask restart = live changes
> 4. **Multiple tunnels run** - don't kill all cloudflared processes
> 5. **Tunnel config:** `/home/aidev/.cloudflared/config-gruppett.yml`
> 6. **Tunnel ID:** `62457ea9-f9a2-4391-a904-f2e061920674`

### Common Compaction Pitfalls

❌ **Wrong:** "The site is at localhost:5000"
✅ **Right:** "Production is at https://gruppett.fredlingautomation.dev (tunneled from localhost:5000)"

❌ **Wrong:** "Error 1033 means Flask crashed"
✅ **Right:** "Error 1033 means cloudflared tunnel is down, start it with the command above"

❌ **Wrong:** "Deploy by pushing to GitHub and waiting for CI/CD"
✅ **Right:** "Merge to main, git pull on server, restart Flask (no CI/CD deployment)"

---

## Security Considerations

- Cloudflare Tunnel credentials are in `~/.cloudflared/*.json` - **DO NOT commit these**
- Tunnel provides DDoS protection and hides the origin server IP
- All traffic is encrypted via Cloudflare's network
- No port forwarding or firewall rules needed on the local machine

---

**Last Updated:** 2026-02-06
**Maintained by:** AI Development Team
**Related Docs:** `docs/CURRENT_TASK.md`, `docs/jules-playbook.md`
