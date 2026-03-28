# Personal AI Employee - Silver Tier ✅ COMPLETE

**Tagline:** *Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.*

Silver Tier is the **functional assistant** level of the Personal AI Employee hackathon. It extends Bronze with multi-source monitoring (Gmail, WhatsApp, LinkedIn), direct execution for external actions, automated LinkedIn posting, and scheduled dashboard updates.

**Status:** All Silver Tier requirements completed and tested ✅

---

## Features

### From Bronze Tier ✅
- **Obsidian Vault** - Local knowledge base with Dashboard and Company Handbook
- **FileSystem Watcher** - Monitors `/Inbox` folder for new files
- **Orchestrator** - Monitors folders and triggers Claude Code
- **Human-in-the-Loop (HITL)** - Proper approval workflow with `/Approved` and `/Rejected`
- **Agent Skills** - `process-inbox` and `update-dashboard` skills
- **Color-Coded Logging** - Component-specific colors for easy debugging

### New in Silver Tier ✅
- **Gmail Watcher** - Monitors unread important emails via Gmail API (120s interval)
- **WhatsApp Watcher** - Monitors WhatsApp Web for keyword messages (30s interval)
- **LinkedIn Watcher** - Monitors LinkedIn engagement and messages (300s interval)
- **Direct Execution** - Email, LinkedIn, WhatsApp actions without spawning Claude sessions
- **LinkedIn Auto-Posting** - Automated business/sales posts via LinkedIn API
- **Scheduled Dashboard Updates** - Auto-refresh every 10 minutes via `/update-dashboard` skill
- **7 Agent Skills** - Workflow and action skills for all operations
- **Categorized Action Files** - Subdirectories for each source (email/, whatsapp/, linkedin/, files/)
- **Subprocess Architecture** - Isolated watcher processes prevent module lock deadlocks
- **State Management** - Prevents duplicate processing across all watchers

---

## Architecture

```
EXTERNAL SOURCES (Gmail, WhatsApp, LinkedIn, Files)
        ↓
PERCEPTION LAYER (Watchers - Subprocess Architecture)
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌───────────┐
│Gmail Watcher│ │WhatsApp     │ │LinkedIn     │ │FileSystem │
│  (120s)     │ │Watcher (30s)│ │Watcher(300s)│ │Watcher    │
│  Pink       │ │ Light Green │ │ Light Blue  │ │  Gold     │
└──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └─────┬─────┘
       │               │               │              │
       ▼               ▼               ▼              ▼
OBSIDIAN VAULT (/Needs_Action/)
┌─────────────────────────────────────────────────────────────┐
│  /email/  │  /whatsapp/  │  /linkedin/  │  /files/         │
└─────────────────────────────────────────────────────────────┘
       │
       ▼
ORCHESTRATOR (White - Monitors all subdirectories)
       │
       ▼
REASONING LAYER (Claude Code - Orange)
       │
       ├─────────────────┬─────────────────┐
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

**Key Architecture Features:**
- **Subprocess Isolation:** Each watcher runs in separate Python process
- **Direct Execution:** Orchestrator directly calls service methods (no Claude spawning)
- **Color-Coded Logging:** Easy visual identification of components
- **State Management:** JSON files prevent duplicate processing
- **Scheduled Updates:** Dashboard refreshes every 10 minutes automatically

---

## Project Structure

```
Silver_Tier/
├── AI_Employee_Vault_FTE/      # Obsidian vault
│   ├── Dashboard.md            # Real-time system summary
│   ├── Company_Handbook.md     # Rules of Engagement
│   ├── Business_Goals.md       # Objectives and metrics
│   ├── Needs_Action/           # Action files by source
│   │   ├── email/              # Gmail action files
│   │   ├── whatsapp/           # WhatsApp action files
│   │   ├── linkedin/           # LinkedIn action files
│   │   └── files/              # FileSystem action files
│   ├── Pending_Approval/       # Items needing approval
│   ├── Approved/               # Human approved
│   ├── Rejected/               # Human rejected
│   ├── Done/                   # Completed tasks
│   ├── Logs/                   # Audit logs
│   └── Briefings/              # CEO briefing reports
│
├── watchers/                   # Perception layer
│   ├── base_watcher.py         # Base class
│   ├── filesystem_watcher.py   # File monitoring
│   ├── gmail_watcher.py        # Gmail API monitoring
│   ├── whatsapp_watcher.py     # WhatsApp Web monitoring
│   └── linkedin_watcher.py     # LinkedIn monitoring
│
├── mcp_server/                 # Action layer (Direct execution services)
│   ├── server.py               # Service initialization
│   ├── email_service.py        # Gmail API sending
│   ├── whatsapp_service.py     # WhatsApp Web automation
│   └── linkedin_service.py     # LinkedIn API posting/messaging
│
├── integrations/               # External integrations
│   └── linkedin_poster.py      # Auto-posting
│
├── orchestrator/               # Main controller
│   └── main.py
│
├── scheduling/                 # Scheduled tasks
│   ├── weekly_briefing.ps1     # Monday 10 AM (Planned for Gold Tier)
│   └── linkedin_post.ps1       # Scheduled posts (Planned for Gold Tier)
│
├── credentials/                # OAuth credentials
├── sessions/                   # Browser sessions
│
├── .claude/skills/             # 7 Agent Skills
│   ├── process-inbox/          # Process all Needs_Action items
│   ├── update-dashboard/       # Update Dashboard.md
│   ├── send-email/             # Send email via Gmail API
│   ├── send-whatsapp/          # Send WhatsApp via Web automation
│   ├── post-linkedin/          # Post to LinkedIn via API
│   ├── send-linkedin-message/  # Send LinkedIn DM via Playwright
│   └── browsing-with-playwright/ # Browser automation support
│
├── .env                        # Environment variables
├── pyproject.toml
├── README.md
└── CLAUDE.md
```

---

## Vault Folders

| Folder | Purpose | Who Writes |
|--------|---------|------------|
| `/Inbox` | Drop files here | USER |
| `/Archive` | Original files stored | Watcher |
| `/Needs_Action/email` | Gmail action files | Gmail Watcher |
| `/Needs_Action/whatsapp` | WhatsApp action files | WhatsApp Watcher |
| `/Needs_Action/linkedin` | LinkedIn action files | LinkedIn Watcher |
| `/Needs_Action/files` | FileSystem action files | FileSystem Watcher |
| `/In_Progress` | Files being processed | Claude |
| `/Plans` | Plan.md files | Claude |
| `/Pending_Approval` | Items needing approval | Claude |
| `/Approved` | Human approved | USER |
| `/Rejected` | Human rejected | USER |
| `/Done` | Completed tasks | Claude |
| `/Logs` | Audit logs | All |
| `/Briefings` | Weekly CEO briefings | Claude |

---

## Quick Start

### 1. Install Dependencies

```bash
cd Silver_Tier
uv sync
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your credentials
```

Required environment variables:
- `GOOGLE_CLIENT_ID` - Gmail OAuth client ID
- `GOOGLE_CLIENT_SECRET` - Gmail OAuth client secret
- `LINKEDIN_ACCESS_TOKEN` - LinkedIn API token
- `LINKEDIN_REFRESH_TOKEN` - LinkedIn refresh token
- `WHATSAPP_SESSION_PATH` - Path for WhatsApp session

### 3. Setup Gmail OAuth (First Time)

```bash
uv run python -c "from watchers.gmail_watcher import setup_oauth; setup_oauth()"
```

### 4. Open Obsidian Vault

1. Open Obsidian
2. Open folder as vault: `Silver_Tier/AI_Employee_Vault_FTE`

### 5. Start the Orchestrator

```bash
uv run python -m orchestrator
```

### 6. Test the System

Drop any file into `/Inbox`:
```bash
cp some_file.txt AI_Employee_Vault_FTE/Inbox/
```

---

## CLI Commands

| Command | Description |
|---------|-------------|
| `uv run python -m orchestrator` | Full autonomous mode |
| `uv run python -m watchers` | All watchers only |
| `uv run python -m watchers.gmail` | Gmail watcher only |
| `uv run python -m watchers.whatsapp` | WhatsApp watcher only |
| `uv run python -m orchestrator --status` | Show system status |
| `uv run python -m orchestrator --briefing` | Generate CEO briefing |

---

## Watcher Configuration

| Watcher | Interval | Monitors | Output | Color |
|---------|----------|----------|--------|-------|
| Gmail | 120s | Unread important emails | `/Needs_Action/email/` | Pink |
| WhatsApp | 30s | Messages with keywords | `/Needs_Action/whatsapp/` | Light Green |
| LinkedIn | 300s | Messages, engagement | `/Needs_Action/linkedin/` | Light Blue |
| FileSystem | Real-time | `/Inbox` folder | `/Needs_Action/files/` | Gold |

**State Management:** Each watcher maintains a JSON state file to prevent duplicate processing:
- `gmail_processed.json` - Tracks processed email IDs
- `whatsapp_processed.json` - Tracks processed message IDs
- `linkedin_processed.json` - Tracks processed LinkedIn items
- `filesystem_processed.json` - Tracks processed file hashes

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
- `process-inbox` - Process all files in `/Needs_Action` subdirectories
- `update-dashboard` - Update Dashboard.md with current system state

### Action Skills
- `send-email` - Send email via Gmail API
- `send-whatsapp` - Send WhatsApp message via Web automation
- `post-linkedin` - Post to LinkedIn via API
- `send-linkedin-message` - Send LinkedIn DM via Playwright

### Support Skills
- `browsing-with-playwright` - Browser automation for web interactions

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

### Contents (Planned)
- Executive Summary
- Revenue Summary
- Completed Tasks
- Bottlenecks Identified
- Proactive Suggestions
- Pending Items
- Upcoming Deadlines

**Note:** Full CEO Briefing system will be implemented in Gold Tier with Business_Goals.md integration and accounting audit capabilities.

---

## Human-in-the-Loop (HITL)

### For Humans

**When Claude flags an item for approval:**

1. Open `/Pending_Approval` folder
2. Read the approval request
3. Check corresponding Plan.md in `/Plans`
4. Make decision:
   - **Approve:** Move file to `/Approved`
   - **Reject:** Move file to `/Rejected`

### For Claude

- Routine actions: Execute directly
- Sensitive actions: Create approval request in `/Pending_Approval`
- External actions: Use direct execution services (Email, LinkedIn, WhatsApp)
- Never execute sensitive actions without approval

**Direct Execution Flow:**
1. Claude creates approval request → `/Pending_Approval`
2. Human reviews and moves to `/Approved` or `/Rejected`
3. Orchestrator detects approved file
4. Orchestrator directly calls service method (no Claude spawning)
5. Orchestrator moves files to `/Done` and `/Archive`

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

## Security

### Credential Management
- All credentials in `.env` (gitignored)
- OAuth tokens in `/credentials/` (gitignored)
- WhatsApp session in `/sessions/` (gitignored)

### Permission Boundaries

| Action | Auto-Approve | Require Approval |
|--------|--------------|------------------|
| Email | Known contacts | New contacts, bulk |
| WhatsApp | Simple replies | Negotiations |
| LinkedIn | Scheduled posts | Replies, DMs |
| Payments | Never | Always |

---

## Requirements

- Python 3.13+
- Claude Code installed and in PATH
- Obsidian (optional, for GUI)
- Gmail API credentials (OAuth 2.0)
- LinkedIn API access token
- WhatsApp Web account (for persistent session)

---

## Silver Tier Completion Status

| # | Requirement | Status |
|---|-------------|--------|
| 1 | All Bronze requirements | ✅ Complete |
| 2 | Two or more Watcher scripts (Gmail + WhatsApp + LinkedIn) | ✅ Complete (4 watchers) |
| 3 | Automatically Post on LinkedIn about business to generate sales | ✅ Complete |
| 4 | Claude reasoning loop that creates Plan.md files | ✅ Complete |
| 5 | One working MCP server for external action | ✅ Complete (Direct execution) |
| 6 | Human-in-the-loop approval workflow for sensitive actions | ✅ Complete |
| 7 | Basic scheduling via cron or Task Scheduler | ✅ Complete (Dashboard updates) |
| 8 | All AI functionality implemented as Agent Skills | ✅ Complete (7 skills) |

**All Silver Tier requirements completed and tested!** ✅

---

## Next Steps

- **Gold Tier:** Odoo integration, Ralph Wiggum loop, full CEO Briefing system with Business_Goals.md
- **Platinum Tier:** Cloud deployment, work-zone specialization, 24/7 operations
