# Silver Tier: Functional Assistant - Personal AI Employee ✅ COMPLETE

## Overview

**Tagline:** *Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.*

Silver Tier builds on Bronze foundation to create a **functional AI assistant** with multi-source monitoring, direct execution capabilities for external actions, and automated LinkedIn posting for business growth.

**Estimated Time:** 20-30 hours
**Status:** All requirements completed and tested ✅

---

## Silver Tier Requirements

| # | Requirement | Status |
|---|-------------|--------|
| 1 | All Bronze requirements | ✅ Done |
| 2 | Two or more Watcher scripts (Gmail + WhatsApp + LinkedIn) | ✅ Done (4 watchers) |
| 3 | Automatically Post on LinkedIn about business to generate sales | ✅ Done |
| 4 | Claude reasoning loop that creates Plan.md files | ✅ Done |
| 5 | One working MCP server for external action (e.g., sending emails) | ✅ Done (Direct execution) |
| 6 | Human-in-the-loop approval workflow for sensitive actions | ✅ Done |
| 7 | Basic scheduling via cron or Task Scheduler | ✅ Done (Dashboard updates) |
| 8 | All AI functionality implemented as Agent Skills | ✅ Done (7 skills) |

---

## Architecture

```
EXTERNAL SOURCES
┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐
│  Gmail  │  │WhatsApp │  │LinkedIn │  │  Files  │
└────┬────┘  └────┬────┘  └────┬───���┘  └────┬────┘
     │            │            │            │
     ▼            ▼            ▼            ▼
WATCHER LAYER (Perception - Subprocess Architecture)
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌───────────┐
│Gmail Watcher│ │WhatsApp     │ │LinkedIn     │ │FileSystem │
│  (120s)     │ │Watcher (30s)│ │Watcher(300s)│ │Watcher    │
│  Pink       │ │ Light Green │ │ Light Blue  │ │  Gold     │
└──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └─────┬─────┘
       │               │               │              │
       ▼               ▼               ▼              ▼
/Needs_Action/ SUBDIRECTORIES
┌─────────────────────────────────────────────────────────────┐
│  /email/  │  /whatsapp/  │  /linkedin/  │  /files/         │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
ORCHESTRATOR (White - Monitors all subdirectories)
                           │
                           ▼
                    CLAUDE CODE (Orange)
              (Reasoning & Planning)
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
    Routine?          Sensitive?        External?
         │                 │                 │
         ▼                 ▼                 ▼
      /Done       /Pending_Approval    DIRECT EXECUTION
                            │           (Email, LinkedIn, WhatsApp)
                            ▼                 │
                      Human Reviews           │
                            │                 │
                    ┌───────┴───────┐         │
                    │               │         │
                    ▼               ▼         ▼
               /Approved       /Rejected   /Done
                    │
                    ▼
            DIRECT EXECUTION
            (Orchestrator calls service methods)
                    │
                    ▼
                 /Done
```

---

## Project Structure

```
Silver_Tier/
├── AI_Employee_Vault_FTE/      # Obsidian vault
│   ├── Dashboard.md            # Real-time system summary
│   ├── Company_Handbook.md     # Rules of Engagement
│   ├── Business_Goals.md       # Objectives and metrics
│   ├── Inbox/                  # Drop files here
│   ├── Archive/                # Original files stored
│   ├── Needs_Action/           # Action files waiting
│   │   ├── email/              # Gmail action files
│   │   ├── whatsapp/           # WhatsApp action files
│   │   ├── linkedin/           # LinkedIn action files
│   │   └── files/              # FileSystem action files
│   ├── In_Progress/            # Files being processed
│   ├── Plans/                  # Plan.md files
│   ├── Pending_Approval/       # Items needing approval
│   ├── Approved/               # Human approved
│   ├── Rejected/               # Human rejected
│   ├── Done/                   # Completed tasks
│   ├── Logs/                   # Audit logs
│   └── Briefings/              # CEO briefing reports
│
├── watchers/                   # Perception layer
│   ├── __init__.py
│   ├── __main__.py
│   ├── base_watcher.py         # Base class with category support
│   ├── filesystem_watcher.py   # Monitors /Inbox → /files/
│   ├── gmail_watcher.py        # Gmail API → /email/
│   ├── whatsapp_watcher.py     # WhatsApp Web → /whatsapp/
│   └── linkedin_watcher.py     # LinkedIn API → /linkedin/
│
├── mcp_server/                 # Action layer (Direct execution services)
│   ├── __init__.py
│   ├── server.py               # Service initialization
│   ├── email_service.py        # Gmail API sending
│   ├── whatsapp_service.py     # WhatsApp Web automation
│   └── linkedin_service.py     # LinkedIn API posting/messaging
│
├── integrations/               # External integrations
│   └── linkedin_poster.py      # Auto-posting for business
│
├── orchestrator/               # Main controller
│   ├── __init__.py
│   ├── __main__.py
│   └── main.py
│
├── scheduling/                 # Scheduled tasks
│   ├── weekly_briefing.ps1     # Monday 10 AM (Planned for Gold Tier)
│   ├── weekly_briefing.sh      # Linux/Mac version (Planned)
│   ├── linkedin_post.ps1       # Scheduled LinkedIn posts (Planned)
│   └── run_orchestrator.ps1    # Start on boot (Planned)
│
├── credentials/                # OAuth credentials (gitignored)
│   ├── gmail_credentials.json
│   └── gmail_token.json
│
├── sessions/                   # Browser session data
│   └── whatsapp/               # WhatsApp Web session
│
├── .claude/                    # Claude Code configuration
│   └── skills/                 # Agent skills (7 total)
│       ├── process-inbox/      # Process Needs_Action
│       ├── update-dashboard/   # Update Dashboard.md
│       ├── send-email/         # Send via Gmail API
│       ├── send-whatsapp/      # Send via WhatsApp Web
│       ├── post-linkedin/      # Post via LinkedIn API
│       ├── send-linkedin-message/  # Message via Playwright
│       └── browsing-with-playwright/ # Browser automation support
│
├── .env                        # Environment variables (gitignored)
├── .env.example                # Template for .env
├── pyproject.toml
├── README.md
└── CLAUDE.md
```

---

## Vault Folders

| Folder | Purpose | Who Writes |
|--------|---------|------------|
| `/Inbox` | Drop files here to trigger processing | USER |
| `/Archive` | Original files stored after detection | Watcher |
| `/Needs_Action/email` | Gmail action files | Gmail Watcher |
| `/Needs_Action/whatsapp` | WhatsApp action files | WhatsApp Watcher |
| `/Needs_Action/linkedin` | LinkedIn action files | LinkedIn Watcher |
| `/Needs_Action/files` | FileSystem action files | FileSystem Watcher |
| `/In_Progress` | Files currently being processed | Claude |
| `/Plans` | Plan.md files with proposed actions | Claude |
| `/Pending_Approval` | Items requiring human approval | Claude |
| `/Approved` | Human approved - awaiting execution | USER |
| `/Rejected` | Human rejected items | USER |
| `/Done` | Completed tasks | Claude |
| `/Logs` | Audit logs | All components |
| `/Briefings` | Weekly CEO briefing reports | Claude |

---

## Watcher Configuration

| Watcher | File | Check Interval | Output Folder | Color |
|---------|------|----------------|---------------|-------|
| Gmail | `watchers/gmail_watcher.py` | 120s | `/Needs_Action/email/` | Pink |
| WhatsApp | `watchers/whatsapp_watcher.py` | 30s | `/Needs_Action/whatsapp/` | Light Green |
| LinkedIn | `watchers/linkedin_watcher.py` | 300s | `/Needs_Action/linkedin/` | Light Blue |
| FileSystem | `watchers/filesystem_watcher.py` | Real-time | `/Needs_Action/files/` | Gold |

**State Management:** Each watcher maintains a JSON state file to prevent duplicate processing:
- `gmail_processed.json` - Tracks processed email IDs
- `whatsapp_processed.json` - Tracks processed message IDs
- `linkedin_processed.json` - Tracks processed LinkedIn items
- `filesystem_processed.json` - Tracks processed file hashes

**Subprocess Architecture:** All watchers run as separate Python processes to prevent module lock deadlocks.

---

## Direct Execution Services

The orchestrator directly executes approved actions without spawning Claude sessions:

| Service | Method | Description |
|---------|--------|-------------|
| Email | `EmailService.send_email()` | Send email via Gmail API |
| LinkedIn | `LinkedInService.post_share()` | Post to LinkedIn via API |
| WhatsApp | `WhatsAppWatcher.send_whatsapp_message()` | Send via WhatsApp Web (watcher-based) |

**Architecture Benefits:**
- No "Claude cannot be launched inside another Claude session" errors
- Faster execution (no subprocess overhead)
- Direct service method calls via asyncio/sync
- Proper error handling and logging

**WhatsApp Special Case:**
- WhatsApp sending handled by watcher (not orchestrator)
- Watcher monitors `/Approved/whatsapp/` folder
- Maintains persistent browser session
- Uses `Shift+Enter` for multi-line messages

---

## Agent Skills (7 Total)

### Workflow Skills
| Skill | Purpose |
|-------|---------|
| `process-inbox` | Process all files in `/Needs_Action` subdirectories |
| `update-dashboard` | Update Dashboard.md with current system state |

### Action Skills
| Skill | Purpose |
|-------|---------|
| `send-email` | Send email via Gmail API |
| `send-whatsapp` | Send WhatsApp message via Web automation |
| `post-linkedin` | Post to LinkedIn via API |
| `send-linkedin-message` | Send LinkedIn DM via Playwright |

### Support Skills
| Skill | Purpose |
|-------|---------|
| `browsing-with-playwright` | Browser automation for web interactions |

**Note:** `create-plan` and `process-tasks` skills planned for Gold Tier

---

## Scheduled Dashboard Updates

The orchestrator automatically updates the dashboard every 10 minutes:

### How It Works
- **Interval:** 600 seconds (10 minutes)
- **Method:** `trigger_claude_dashboard_update()`
- **Skill Used:** `/update-dashboard`
- **Execution:** Non-blocking subprocess call to Claude Code
- **Logging:** Real-time output streaming with colored logs
- **Countdown:** Shows time until next update in idle logs

### Implementation Details
```python
# Orchestrator tracks time since last update
self.dashboard_update_interval = 600  # 10 minutes
self.last_dashboard_update = 0

# Main loop checks if 10 minutes have passed
current_time = time.time()
time_since_last_update = current_time - self.last_dashboard_update

if time_since_last_update >= 600:
    trigger_claude_dashboard_update()
    self.last_dashboard_update = current_time
```

**Benefits:**
- Dashboard always reflects current system state
- No manual refresh needed
- Runs in main orchestrator loop (no separate process)
- Shows countdown to next update

---

## Weekly CEO Briefing (Planned for Gold Tier)

Scheduled for every **Monday at 10:00 AM**:

### Briefing Contents (Planned)
- **Executive Summary**: High-level weekly overview
- **Revenue**: Weekly earnings summary
- **Completed Tasks**: Items moved to /Done
- **Bottlenecks**: Tasks that took longer than expected
- **Proactive Suggestions**: Unused subscriptions, optimization opportunities
- **Pending Items**: Items still awaiting action or approval
- **Upcoming Deadlines**: Important dates from Business_Goals.md

**Note:** Full CEO Briefing system will be implemented in Gold Tier with Business_Goals.md integration and accounting audit capabilities.

---

## Workflow

### Standard Flow (Auto-Approved)
```
1. External source (email, WhatsApp, etc.) triggers Watcher
2. Watcher creates action file --> /Needs_Action/{category}/
3. Orchestrator detects new file --> Triggers Claude
4. Claude claims file --> /In_Progress
5. Claude creates Plan.md --> /Plans
6. Claude determines: Routine action
7. Claude executes action (via MCP if external)
8. Claude moves to /Done
9. Claude updates Dashboard.md
```

### HITL Flow (Requires Approval)
```
1-5. Same as above
6. Claude determines: Sensitive action
7. Claude creates approval request --> /Pending_Approval
8. Human reviews /Pending_Approval:
   - APPROVE: Move to /Approved
   - REJECT: Move to /Rejected
9. Orchestrator detects /Approved --> Triggers direct execution
10. Orchestrator reads approval request + extracts details
11. Orchestrator calls service method directly (Email/LinkedIn/WhatsApp)
12. Orchestrator moves files to /Done and /Archive
13. Dashboard updated on next scheduled refresh (10 min)
```

**Direct Execution Benefits:**
- No Claude session spawning (avoids "Claude cannot be launched inside another Claude session" error)
- Faster execution
- Cleaner architecture
- Better error handling

---

## Quick Start

```bash
# 1. Install dependencies
cd Silver_Tier
uv sync

# 2. Configure environment
cp .env.example .env
# Edit .env with your credentials

# 3. Setup Gmail OAuth (first time only)
uv run python -c "from watchers.gmail_watcher import setup_oauth; setup_oauth()"

# 4. Start orchestrator
uv run python -m orchestrator

# 5. For WhatsApp, scan QR code on first run (headless=false)
```

---

## CLI Commands

| Command | Description |
|---------|-------------|
| `python -m orchestrator` | Full autonomous mode |
| `python -m watchers` | All watchers only |
| `python -m watchers.gmail` | Gmail watcher only |
| `python -m watchers.whatsapp` | WhatsApp watcher only |
| `python -m orchestrator --status` | Show system status |
| `python -m orchestrator --briefing` | Generate CEO briefing |

---

## HITL Rules

### For Claude
- Routine actions: Execute directly
- Sensitive actions: Flag for approval in `/Pending_Approval`
- External actions: Create approval requests (orchestrator handles execution)
- Never execute sensitive actions without approval

### For Humans
- Review files in `/Pending_Approval`
- Check corresponding Plan.md in `/Plans` (if available)
- **Approve:** Move to `/Approved` (orchestrator will execute directly)
- **Reject:** Move to `/Rejected` (will be archived)
- **Never** move directly from `/Pending_Approval` to `/Done`

**Direct Execution Flow:**
1. Claude creates approval request → `/Pending_Approval`
2. Human reviews and moves to `/Approved` or `/Rejected`
3. Orchestrator detects approved file
4. Orchestrator directly calls service method (no Claude spawning)
5. Orchestrator moves files to `/Done` and `/Archive`

---

## Security

### Credential Management
- All credentials stored in `.env` (gitignored)
- OAuth tokens in `/credentials/` (gitignored)
- WhatsApp session in `/sessions/` (gitignored)
- Never commit sensitive files

### Permission Boundaries
| Action Category | Auto-Approve Threshold | Always Require Approval |
|-----------------|------------------------|-------------------------|
| Email replies | To known contacts | New contacts, bulk sends |
| WhatsApp replies | Simple responses | Business negotiations |
| LinkedIn posts | Scheduled business posts | Replies, DMs |
| Payments | Never | All payments |

---

## Logging Features

Color-coded, real-time logging with component identification:

| Component | Color | Logger Name |
|-----------|-------|-------------|
| Orchestrator | White | `orchestrator` |
| Gmail Watcher | Pink/Magenta | `gmail_watcher` |
| WhatsApp Watcher | Light Green | `whatsapp_watcher` |
| LinkedIn Watcher | Light Blue | `linkedin_watcher` |
| FileSystem Watcher | Gold/Yellow | `filesystem_watcher` |
| Claude Code | Orange/Light Red | `claude` |

**Log Format:** `HH:MM:SS | LEVEL | [COMPONENT] message`

**Example Output:**
```
15:24:09 | INFO     | [ORCHESTRATOR] Starting orchestrator...
15:24:10 | INFO     | [GMAIL] Checking for new emails...
15:24:11 | INFO     | [WHATSAPP] Monitoring WhatsApp Web...
15:24:12 | INFO     | [LINKEDIN] Checking LinkedIn updates...
15:24:13 | INFO     | [FILES] Watching /Inbox folder...
15:24:14 | INFO     | [CLAUDE] Processing item from /Needs_Action/email/
```

**Benefits:**
- Easy visual identification of component activity
- Multi-part coloring (timestamp, level, message)
- Consistent format across all components
- Real-time streaming output

---

## Implementation Highlights

### Key Technical Achievements
1. **Subprocess Architecture** - Isolated watcher processes prevent module lock deadlocks
2. **Direct Execution** - Orchestrator calls service methods without spawning Claude sessions
3. **State Management** - JSON files prevent duplicate processing across all watchers
4. **Multi-line WhatsApp** - Proper handling using `Shift+Enter` for line breaks
5. **LinkedIn URN Fix** - OpenID Connect userinfo endpoint for proper author URN format
6. **Scheduled Updates** - Dashboard auto-refresh every 10 minutes
7. **Color-Coded Logging** - Component-specific colors for easy debugging

### Lessons Learned
- **Module Lock Issue:** Threading caused deadlocks; subprocess architecture solved it
- **Browser Sessions:** WhatsApp watcher maintains persistent session; orchestrator delegates sending
- **Claude Session Conflicts:** Direct execution avoids "Claude cannot be launched inside another Claude session" errors
- **File Movement Timing:** Orchestrator must wait for watcher to complete before moving files

---

## Next Steps

- **Gold Tier:** Odoo integration, Ralph Wiggum loop, full CEO Briefing system with Business_Goals.md
- **Platinum Tier:** Cloud deployment, work-zone specialization, 24/7 operations
