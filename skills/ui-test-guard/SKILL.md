---
name: ui-test-guard
description: A Stop hook that catches Claude when it claims a UI change is "done", "deployed", or "verified" without showing evidence that a real-browser UI test actually passed. Stops the curl + grep illusion of testing.
---

# ui-test-guard — Stop Hook for Honest UI Testing

A Claude Code Stop hook that intercepts replies claiming a UI change is complete and asks: *did you actually run a real-browser test?* If not, it injects a system-reminder so Claude has to either run the test or admit it skipped.

## The problem

Claude will happily report a UI change as "deployed and verified" after running only `curl | grep "expected text"`. Curl can confirm the server returns a 200 with the right string in its body, but it cannot catch:

- CSS layout breakage
- React hydration errors
- RSC flight payloads served as raw text instead of rendered HTML
- Blank screens caused by JS runtime errors
- Visual regressions
- Missing fonts, broken images, overflow, mobile-only bugs

A user can spend hours trusting "verified" reports that were never actually verified.

## The fix

A Stop hook scans Claude's last reply. If it contains:

- A claim word: `deployed`, `verified`, `done`, `shipped`, `live`, `tested`, `complete`, `works`, `ALL PASSED`
- AND a URL or known web route: `https://...`, `/login`, `/dashboard`, `/portfolio`, etc.
- AND **no** evidence of a real-browser test: `ui-test`, `run_tests.py`, `ALL PASSED`, `playwright`, `cypress`

…the hook returns exit 2 with a reminder. Claude sees the reminder on the next turn and has to either run the test or explicitly say it skipped.

## How it works

| Phase | What happens |
|---|---|
| Stop event fires | After every Claude reply is composed |
| Hook reads transcript | Pulls the last assistant message text via jq |
| Three regexes evaluated | `CLAIM_RE` AND `URL_RE` AND NOT `EVIDENCE_RE` |
| If all true | exit 2 + system-reminder via stderr |
| Otherwise | exit 0, silent pass |

Fail-open by design: if `jq` is missing, the transcript is unreadable, or anything else goes wrong, the hook exits 0. No false positives blocking real work.

## Install

### 1. Copy the hook

```bash
mkdir -p ~/.claude/hooks/ui-test-guard
cp skills/ui-test-guard/hooks/ui-test-guard.sh ~/.claude/hooks/ui-test-guard/
chmod +x ~/.claude/hooks/ui-test-guard/ui-test-guard.sh
```

### 2. Register in settings.json

Add this to `~/.claude/settings.json` under `hooks`:

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "/home/<you>/.claude/hooks/ui-test-guard/ui-test-guard.sh",
            "timeout": 5
          }
        ]
      }
    ]
  }
}
```

See `settings.example.json` for the project-relative path version.

### 3. Verify

```bash
# Synthetic transcript that should trigger
mkdir -p /tmp/guard-test
cat > /tmp/guard-test/bad.jsonl <<'EOF'
{"type":"assistant","message":{"content":[{"type":"text","text":"I deployed the fix to /dashboard and verified it works."}]}}
EOF
echo '{"transcript_path":"/tmp/guard-test/bad.jsonl"}' | bash ~/.claude/hooks/ui-test-guard/ui-test-guard.sh
echo "exit=$?"
# Expected: prints reminder to stderr, exit=2
```

## Customize the regexes

Override any regex via environment variables before the hook runs. Useful when you want to scope to a specific project URL:

| Env var | Default | Example override |
|---|---|---|
| `UI_TEST_GUARD_CLAIM_RE` | `(deployed|verified|...)` | `(deployed|shipped)` for stricter |
| `UI_TEST_GUARD_URL_RE` | generic web routes + http URLs | `(myapp\.example\.com)` for project scope |
| `UI_TEST_GUARD_EVIDENCE_RE` | `(ui-test|run_tests\.py|ALL PASSED|...)` | add your team's test harness name |
| `UI_TEST_GUARD_LOG` | `/tmp/ui-test-guard.log` | `/var/log/...` |

Wrap the hook in a wrapper script to apply the env, e.g.:

```bash
#!/bin/bash
export UI_TEST_GUARD_URL_RE='(myapp\.example\.com|/dashboard|/admin)'
exec ~/.claude/hooks/ui-test-guard/ui-test-guard.sh
```

## Pair this with a real-browser test runner

This hook only nags. It does not run the test. You still need a test harness. Pairs well with:

- `ui-test` skill (AWS AgentCore Browser, in this repo)
- Playwright
- Cypress
- Selenium

The `EVIDENCE_RE` matches the names of the most common harnesses, so it stays quiet when any of them are mentioned in the reply.

## Why a Stop hook, not PreToolUse

Two design choices were considered:

**Stop hook (this skill):** soft, advisory. Reminds Claude after the fact. Does not block any tool. Lets Claude finish a thought, then nudges. Best for repeated education.

**PreToolUse hook (alternative):** hard block. Refuses `git commit` or `aws ssm send-command` if recent test results don't show pass. Stronger, but risks blocking legitimate non-UI work and frustrating the user.

This skill picks the soft path. Upgrade to PreToolUse only if Stop reminders aren't enough.

## File layout

```
ui-test-guard/
├── SKILL.md                      # this file
├── settings.example.json         # hooks block to merge into settings.json
└── hooks/
    └── ui-test-guard.sh          # the hook itself (one Bash script)
```

## Limitations

- Only as good as the regexes. If Claude phrases its claim creatively, the hook won't fire.
- Reads the JSONL transcript — sensitive to changes in Claude Code's transcript schema. Tested on Claude Code 2.x.
- One hook per Stop event. If you have other Stop hooks, register them all in the same array.
