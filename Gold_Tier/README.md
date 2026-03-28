# Personal AI Employee - Gold Tier 🚀

**Tagline:** *Autonomous AI Employee with Full Business Integration*

Gold Tier is the **autonomous employee** level of the Personal AI Employee hackathon. It extends Silver Tier with Odoo accounting integration, Facebook business integration, weekly CEO briefings, Ralph Wiggum loop for multi-step tasks, and comprehensive audit logging.

**Status:** ✅ Gold Tier Implementation Complete

---

## Features

### From Silver Tier ✅
- All Silver Tier features (Gmail, WhatsApp, LinkedIn watchers)
- Direct execution services
- 7 agent skills
- HITL approval workflow
- Scheduled dashboard updates

### New in Gold Tier 🆕
- **Odoo Accounting Integration** - Docker Compose setup with Odoo 19 + PostgreSQL
- **Facebook Business Integration** - Page posting, messaging, auto-posting via Graph API
- **LinkedIn Auto-Posting** - 7 templates, scheduled posting, post history tracking
- **Multiple MCP Servers** - Separate MCP servers for different domains (Odoo, Facebook)
- **Weekly CEO Briefing** - Automated business audit with revenue tracking
- **Ralph Wiggum Loop** - Autonomous multi-step task completion (max 5 iterations)
- **Audit Logging** - Comprehensive JSON logging of all actions
- **Error Recovery** - Graceful degradation with retry logic & circuit breaker
- **14+ MCP Tools** - Invoice creation, payment recording, financial reports, social posting
- **6 Watchers** - Gmail, WhatsApp, LinkedIn, Facebook, FileSystem, Odoo
- **13 Agent Skills** - Workflow, action, Odoo, and social media skills

---

## Architecture

```
EXTERNAL SOURCES (Gmail, WhatsApp, LinkedIn, Facebook, Odoo)
        ↓
PERCEPTION LAYER (Watchers - Subprocess Architecture)
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌───────────┐ ┌─────────┐ ┌─────────┐
│Gmail Watcher│ │WhatsApp     │ │LinkedIn     │ │Facebook   │ │FileSystem│ │ Odoo    │
│  (701s)     │ │Watcher (571s)│ │Watcher(839s)│ │Watcher    │ │Watcher  │ │ Watcher │
│  Pink       │ │ Light Green │ │ Light Blue  │ │  Cyan     │ │  Gold   │ │ Purple  │
└──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └──────┬────┘ └────┬────┘ └────┬────┘
       │               │               │               │           │           │
       ▼               ▼               ▼               ▼           ▼           ▼
OBSIDIAN VAULT (/Needs_Action/)
┌─────────────────────────────────────────────────────────────────────────────────┐
│  /email/  │  /whatsapp/  │  /linkedin/  │  /facebook/  │  /files/  │  /odoo/   │
└─────────────────────────────────────────────────────────────────────────────────┘
                             │
                             ▼
                    ORCHESTRATOR (White)
                    Check Interval: 180s (default)
                             │
                             ▼
              CLAUDE CODE + MCP TOOLS (Gold Tier)
              Ralph Wiggum Loop: Max 5 iterations
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
  Email/WhatsApp      LinkedIn/Facebook      Odoo Accounting
  (existing)          (Gold Tier)            (Gold Tier)
        │                    │                    │
        ▼                    ▼                    ▼
   /Done/{category}/   /Done/{category}/   /Done/{category}/
```

**Key Architecture Features:**
- **Subprocess Isolation:** Each watcher runs in separate Python process
- **Direct Execution:** Orchestrator directly calls service methods (no Claude spawning)
- **Color-Coded Logging:** Easy visual identification of components
- **State Management:** JSON files prevent duplicate processing
- **Scheduled Updates:** Dashboard refreshes every 20 minutes automatically
- **Ralph Wiggum Loop:** Autonomous multi-step task completion

---

## Project Structure

```
Gold_Tier/
├── AI_Employee_Vault_FTE/      # Obsidian vault
│   ├── Dashboard.md            # Real-time system summary
│   ├── Company_Handbook.md     # Rules of Engagement
│   ├── Business_Goals.md       # Objectives and metrics
│   ├── Needs_Action/           # Action files by source
│   │   ├── email/              # Gmail action files
│   │   ├── whatsapp/           # WhatsApp action files
│   │   ├── linkedin/           # LinkedIn action files
│   │   ├── facebook/           # Facebook action files
│   │   ├── files/              # FileSystem action files
│   │   └── odoo/               # Odoo action files
│   ├── In_Progress/            # Files being processed
│   ├── Plans/                  # Plan.md files
│   ├── Pending_Approval/       # Items needing approval
│   ├── Approved/               # Human approved
│   ├── Rejected/               # Human rejected
│   ├── Done/                   # Completed tasks
│   ├── Logs/                   # Audit logs
│   ├── Briefings/              # CEO briefing reports
│   ├── LinkedIn_Posts/         # LinkedIn post history
│   └── Facebook_Posts/         # Facebook post history
│
├── watchers/                   # Perception layer (6 watchers)
│   ├── base_watcher.py         # Base class
│   ├── filesystem_watcher.py   # File monitoring (real-time)
│   ├── gmail_watcher.py        # Gmail API (701s)
│   ├── whatsapp_watcher.py     # WhatsApp Web (571s)
│   ├── linkedin_watcher.py     # LinkedIn (839s)
│   └── facebook_watcher.py     # Facebook (659s)
│
├── mcp_server/                 # Action layer (Direct execution services)
│   ├── server.py               # Main MCP server (14 tools)
│   ├── odoo_mcp.py             # Odoo MCP server (4 tools)
│   ├── email_service.py        # Gmail API sending
│   ├── whatsapp_service.py     # WhatsApp Web automation
│   ├── linkedin_service.py     # LinkedIn API posting/messaging
│   ├── facebook_service.py     # Facebook Graph API
│   └── odoo_service.py         # Odoo XML-RPC
│
├── integrations/               # Auto-posting modules
│   ├── linkedin_poster.py      # LinkedIn auto-poster (7 templates)
│   └── facebook_poster.py      # Facebook auto-poster (7 templates)
│
├── orchestrator/               # Main controller
│   ├── main.py                 # Orchestrator with Ralph Wiggum
│   ├── __init__.py
│   └── __main__.py
│
├── ralph_wiggum/               # Autonomous task completion
│   ├── stop_hook.py            # Intercept Claude exit
│   └── task_tracker.py         # Track completion state
│
├── audit/                      # Audit logging & error recovery
│   ├── logger.py               # JSON audit logging
│   ├── retry.py                # Retry with exponential backoff
│   ├── circuit_breaker.py      # Prevent repeated failures
│   └── health.py               # Service health checks
│
├── scheduling/                 # Scheduled tasks
│   ├── weekly_briefing.ps1     # Windows: Monday 10 AM
│   ├── weekly_briefing.sh      # Linux/Mac: Monday 10 AM
│   ├── linkedin_post.ps1       # LinkedIn scheduled posting
│   ├── facebook_post.ps1       # Facebook scheduled posting
│   ├── setup_task_scheduler.ps1 # Windows Task Scheduler setup
│   └── setup_cron.sh           # Linux/Mac cron setup
│
├── odoo/                       # Odoo Docker setup
│   ├── docker-compose.yml      # Odoo 19 + PostgreSQL
│   ├── README.md               # Setup instructions
│   └── setup.bat               # Windows setup script
│
├── tests/                      # Test files (22 tests)
│   ├── test_services.py        # Test all services
│   ├── test_whatsapp_only.py   # WhatsApp test
│   ├── test_email_only.py      # Email test
│   ├── test_linkedin_only.py   # LinkedIn test
│   ├── test_facebook_only.py   # Facebook test
│   ├── test_whatsapp_standalone.py  # WhatsApp standalone
│   ├── test_social_media.py    # LinkedIn + Facebook
│   ├── test_odoo_connection.py # Odoo connection test
│   ├── test_ralph_wiggum.py    # Ralph Wiggum loop test
│   └── ... (14 more test files)
│
├── .claude/                    # Claude Code configuration
│   ├── skills/                 # 13 Agent Skills
│   │   ├── process-inbox/      # Process Needs_Action items
│   │   ├── update-dashboard/   # Update Dashboard.md
│   │   ├── generate-briefing/  # Generate CEO briefing
│   │   ├── send-email/         # Send email via Gmail
│   │   ├── send-whatsapp/      # Send WhatsApp message
│   │   ├── post-linkedin/      # Post to LinkedIn
│   │   ├── send-linkedin-message/  # Send LinkedIn DM
│   │   ├── post-facebook/      # Post to Facebook
│   │   ├── send-facebook-message/  # Send Facebook message
│   │   ├── create-invoice/     # Create Odoo invoice
│   │   ├── record-payment/     # Record Odoo payment
│   │   ├── get-financial-report/ # Get Odoo financials
│   │   └── browsing-with-playwright/ # Browser automation
│   └── settings.json           # MCP server config
│
├── credentials/                # OAuth credentials (gitignored)
│   ├── gmail_credentials.json  # Gmail OAuth
│   └── gmail_token.json        # Gmail OAuth token
├── sessions/                   # Browser sessions (gitignored)
│   └── whatsapp/               # WhatsApp Web session
├── .watcher_state/             # Watcher state files
│   ├── gmail_processed.json
│   ├── whatsapp_processed.json
│   ├── linkedin_processed.json
│   └── facebook_processed.json
├── .env                        # Environment variables (gitignored)
├── .env.example                # Environment template
├── pyproject.toml              # Python dependencies
├── README.md                   # This file
└── CLAUDE.md                   # Silver Tier docs
```

---

## Quick Start

### 1. Install Dependencies

```bash
cd Gold_Tier
uv sync
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your credentials
```

**Required Environment Variables:**

```ini
# Gmail API
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
GMAIL_CREDENTIALS_PATH=./credentials/gmail_credentials.json

# WhatsApp Web
WHATSAPP_SESSION_PATH=./sessions/whatsapp
WHATSAPP_HEADLESS=false

# LinkedIn API
LINKEDIN_ACCESS_TOKEN=your_token
LINKEDIN_REFRESH_TOKEN=your_refresh_token
LINKEDIN_ORG_ID=your_organization_id

# Facebook Graph API
FACEBOOK_APP_ID=your_app_id
FACEBOOK_APP_SECRET=your_app_secret
FACEBOOK_ACCESS_TOKEN=your_page_token
FACEBOOK_PAGE_ID=your_page_id

# Odoo Accounting
ODOO_URL=http://localhost:8069
ODOO_DB=odoo_db
ODOO_USERNAME=admin
ODOO_PASSWORD=admin
```

### 3. Setup Gmail OAuth (First Time)

```bash
uv run python -c "from watchers.gmail_watcher import setup_oauth; setup_oauth()"
```

### 4. Setup Odoo (Optional - For Accounting)

```bash
cd odoo
docker-compose up -d
# Wait for Odoo to start, then access http://localhost:8069
# Login: admin / admin
```

### 5. Open Obsidian Vault

1. Open Obsidian
2. Open folder as vault: `Gold_Tier/AI_Employee_Vault_FTE`

### 6. Start the Orchestrator

```bash
uv run python -m orchestrator
```

---

## CLI Commands

### Orchestrator Commands

| Command | Description |
|---------|-------------|
| `uv run python -m orchestrator` | Start full autonomous mode (180s interval) |
| `uv run python -m orchestrator --check-interval 60` | Start with 60s check interval |
| `uv run python -m orchestrator --status` | Show system status |
| `uv run python -m orchestrator --briefing` | Generate Weekly CEO Briefing |
| `uv run python -m orchestrator --vault-path ./AI_Employee_Vault_FTE` | Custom vault path |

### Watcher Commands

| Command | Description |
|---------|-------------|
| `uv run python -m watchers` | Start ALL watchers (default) |
| `uv run python -m watchers --watcher file` | FileSystem watcher only |
| `uv run python -m watchers --watcher gmail` | Gmail watcher only |
| `uv run python -m watchers --watcher whatsapp` | WhatsApp watcher only |
| `uv run python -m watchers --watcher linkedin` | LinkedIn watcher only |
| `uv run python -m watchers --watcher facebook` | Facebook watcher only |
| `uv run python -m watchers --vault-path ./AI_Employee_Vault_FTE` | Custom vault path |
| `uv run python -m watchers.gmail --check-interval 300` | Custom check interval |
| `uv run python -m watchers.gmail --setup-oauth` | Setup Gmail OAuth |

### MCP Server Commands

| Command | Description |
|---------|-------------|
| `uv run python -m mcp_server` | Start main MCP server (stdio) |
| `uv run python -m mcp_server --check` | Check service availability |
| `uv run python -m mcp_server.odoo_mcp` | Start Odoo MCP server |

### Testing Commands

| Command | Description |
|---------|-------------|
| `uv run python tests/test_services.py` | Test all messaging services |
| `uv run python tests/test_whatsapp_only.py` | Test WhatsApp only |
| `uv run python tests/test_email_only.py` | Test Email only |
| `uv run python tests/test_linkedin_only.py` | Test LinkedIn only |
| `uv run python tests/test_facebook_only.py` | Test Facebook only |
| `uv run python tests/test_whatsapp_standalone.py` | WhatsApp standalone test |

### LinkedIn Auto-Posting Commands

| Command | Description |
|---------|-------------|
| `uv run python -m integrations.linkedin_poster --post "Your text"` | Direct post |
| `uv run python -m integrations.linkedin_poster --template weekly_update` | Use template |
| `uv run python -m integrations.linkedin_poster --list-templates` | List 7 templates |
| `uv run python -m integrations.linkedin_poster --history` | Show post history |
| `uv run python -m integrations.linkedin_poster --suggest sales` | Content ideas |
| `uv run python -m integrations.linkedin_poster --template milestone --milestone "1000 followers"` | Template with args |

**Available Templates:**
- `product_launch` - New product/service announcement
- `milestone` - Company milestone celebration
- `tip` - Industry tip or advice
- `industry_news` - Commentary on industry news
- `team_announcement` - Team updates/hiring
- `customer_success` - Customer success story
- `weekly_update` - Weekly progress summary

### Facebook Auto-Posting Commands

| Command | Description |
|---------|-------------|
| `uv run python -m integrations.facebook_poster --post "Your text"` | Direct post |
| `uv run python -m integrations.facebook_poster --template weekly_update` | Use template |
| `uv run python -m integrations.facebook_poster --list-templates` | List templates |
| `uv run python -m integrations.facebook_poster --history` | Show post history |

**Available Templates:**
- `product_launch` - New product/service announcement
- `milestone` - Company milestone celebration
- `tip` - Industry tip or advice
- `industry_news` - Commentary on industry news
- `team_announcement` - Team updates/hiring
- `customer_success` - Customer success story
- `weekly_update` - Weekly progress summary

### Scheduling Commands

| Command | Description |
|---------|-------------|
| `uv run python -m orchestrator --briefing` | Generate CEO briefing now |
| `powershell -ExecutionPolicy Bypass -File scheduling/weekly_briefing.ps1` | Run weekly briefing (Windows) |
| `bash scheduling/weekly_briefing.sh` | Run weekly briefing (Linux/Mac) |
| `powershell -ExecutionPolicy Bypass -File scheduling/linkedin_post.ps1 -Template "weekly_update"` | LinkedIn scheduled post |
| `powershell -ExecutionPolicy Bypass -File scheduling/facebook_post.ps1 -Template "milestone"` | Facebook scheduled post |
| `powershell -ExecutionPolicy Bypass -File scheduling/setup_task_scheduler.ps1 -Install` | Setup Windows Task Scheduler |
| `bash scheduling/setup_cron.sh install` | Setup cron jobs (Linux/Mac) |

**Schedule Examples:**

| Platform | Schedule | Command |
|----------|----------|---------|
| **LinkedIn** | Mon & Thu 9 AM | `.\scheduling\linkedin_post.ps1 -Template "weekly_update"` |
| **Facebook** | Tue & Fri 10 AM | `.\scheduling\facebook_post.ps1 -Template "customer_success"` |
| **CEO Briefing** | Monday 10 AM | `.\scheduling\weekly_briefing.ps1` |

### Odoo Commands

| Command | Description |
|---------|-------------|
| `cd odoo && docker-compose up -d` | Start Odoo + PostgreSQL |
| `cd odoo && docker-compose down` | Stop Odoo |
| `cd odoo && docker-compose logs -f` | View Odoo logs |
| `cd odoo && docker-compose ps` | Check Odoo status |
| `uv run python -c "from mcp_server.odoo_service import OdooService; s = OdooService(); print(s._connect())"` | Test Odoo connection |

---

## Watcher Configuration

| Watcher | Interval | Monitors | Output Folder | Color |
|---------|----------|----------|---------------|-------|
| **FileSystem** | Real-time | `/Inbox/` folder | `/Needs_Action/files/` | Gold |
| **Gmail** | 701s (~12 min) | Unread emails | `/Needs_Action/email/` | Pink |
| **WhatsApp** | 571s (~9.5 min) | Keyword messages | `/Needs_Action/whatsapp/` | Light Green |
| **LinkedIn** | 839s (~14 min) | Messages, engagement | `/Needs_Action/linkedin/` | Light Blue |
| **Facebook** | 659s (~11 min) | Messages, comments | `/Needs_Action/facebook/` | Cyan |
| **Odoo** | N/A | Manual/Event-based | `/Needs_Action/odoo/` | Purple |

**State Management:** Each watcher maintains a JSON state file in `.watcher_state/`:
- `gmail_processed.json` - Tracks processed email IDs
- `whatsapp_processed.json` - Tracks message counts per chat
- `linkedin_processed.json` - Tracks processed LinkedIn items
- `filesystem_processed.json` - Tracks processed file hashes
- `facebook_processed.json` - Tracks processed Facebook items

---

## Agent Skills (13 Total)

### Workflow Skills
| Skill | Purpose |
|-------|---------|
| `process-inbox` | Process all files in `/Needs_Action/<category>/` |
| `update-dashboard` | Update Dashboard.md with current state |
| `generate-briefing` | Generate Weekly CEO Briefing |

### Action Skills
| Skill | Purpose | MCP Tool |
|-------|---------|----------|
| `send-email` | Send email via Gmail API | `mcp__ai-employee__send_email` |
| `send-whatsapp` | Send WhatsApp message | `mcp__ai-employee__send_whatsapp` |
| `post-linkedin` | Post to LinkedIn | `mcp__ai-employee__post_linkedin` |
| `send-linkedin-message` | Send LinkedIn DM | `mcp__ai-employee__send_linkedin_message` |
| `post-facebook` | Post to Facebook Page | `mcp__ai-employee__post_facebook` |
| `send-facebook-message` | Send Facebook message | `mcp__ai-employee__send_facebook_message` |

### Odoo Skills
| Skill | Purpose | MCP Tool |
|-------|---------|----------|
| `create-invoice` | Create customer invoice | `mcp__ai-employee__create_invoice` |
| `record-payment` | Record payment | `mcp__ai-employee__record_payment` |
| `get-financial-report` | Get financial report | `mcp__ai-employee__get_financial_report` |

### Support Skills
| Skill | Purpose |
|-------|---------|
| `browsing-with-playwright` | Browser automation |

---

## MCP Tools (14 Total)

### Email Tools
- `send_email(to, subject, body, cc, bcc, html)` - Send email
- `create_email_draft(to, subject, body)` - Create draft
- `search_emails(query)` - Search Gmail

### WhatsApp Tools
- `send_whatsapp(contact, message)` - Send WhatsApp message

### LinkedIn Tools
- `post_linkedin(text, visibility)` - Post to LinkedIn
- `post_linkedin_organization(text, visibility)` - Post as organization
- `send_linkedin_message(user_urn, message, subject)` - Send DM
- `get_linkedin_profile()` - Get profile info

### Facebook Tools
- `post_facebook(message, image_url, link)` - Post to Page
- `send_facebook_message(recipient_id, message)` - Send message
- `get_facebook_insights()` - Get Page insights

### Odoo Tools
- `create_invoice(partner_name, amount, description, due_date)` - Create invoice
- `record_payment(invoice_id, amount, payment_date, reference)` - Record payment
- `get_financial_report(period)` - Get P&L report
- `list_unpaid_invoices()` - List outstanding invoices

---

## Scheduled Tasks

### Weekly CEO Briefing
- **Schedule:** Every Monday at 10:00 AM
- **Script:** `scheduling/weekly_briefing.ps1` (Windows) or `weekly_briefing.sh` (Linux/Mac)
- **Output:** `/Briefings/YYYY-MM-DD_Monday_Briefing.md`

**Briefing Contents:**
- Executive Summary
- Financial Performance (Odoo revenue, expenses, profit)
- Social Media Performance (Facebook posts, LinkedIn activity)
- Communications Summary (Email, WhatsApp stats)
- Document Processing (Files processed)
- Key Metrics (Completed, Pending, In Progress)
- Needs Action by Category
- Recent Activity (Last 15 actions)
- Proactive Suggestions
- Next Week Focus
- Business Goals Reference

### Dashboard Updates
- **Schedule:** Every 20 minutes (1200 seconds)
- **Method:** Orchestrator triggers Claude with `/update-dashboard` skill
- **Timeout:** 10 minutes (600 seconds)

---

## Human-in-the-Loop (HITL) Workflow

### For Sensitive Actions

1. **Claude creates approval request** → `/Pending_Approval/<category>/`
2. **Human reviews** the approval request + Plan.md
3. **Human decides:**
   - **Approve:** Move to `/Approved/<category>/`
   - **Reject:** Move to `/Rejected/<category>/`
4. **Orchestrator detects** approved/rejected file
5. **Orchestrator executes** (if approved) or archives (if rejected)
6. **Files moved** to `/Done/<category>/` or `/Archive/<category>/`

### Approval Thresholds

| Action | Auto-Approve | Require Approval |
|--------|--------------|------------------|
| Email reply | Known contacts | New contacts, bulk sends |
| WhatsApp reply | Simple responses | Business negotiations |
| LinkedIn post | ❌ Never | All posts require approval |
| Facebook post | ❌ Never | All posts require approval |
| Payment | ❌ Never | All payments require approval |
| Invoice creation | ❌ Never | All invoices require approval |

---

## Logging Features

### Color-Coded Logging

| Component | Color | Logger Name |
|-----------|-------|-------------|
| Orchestrator | White | `ORCHESTRATOR` |
| FileSystem | Gold/Yellow | `FILES` |
| Gmail | Pink/Magenta | `GMAIL` |
| WhatsApp | Light Green | `WHATSAPP` |
| LinkedIn | Light Blue | `LINKEDIN` |
| Facebook | Cyan | `FACEBOOK` |
| Odoo | Purple/Magenta | `ODOO` |
| Claude Code | Orange/Red | `CLAUDE` |

**Log Format:**
```
HH:MM:SS | LEVEL | [COMPONENT] message
```

**Example:**
```
15:24:09 | INFO     | [ORCHESTRATOR] Starting orchestrator...
15:24:10 | INFO     | [GMAIL] Checking for new emails...
15:24:11 | INFO     | [WHATSAPP] Monitoring WhatsApp Web...
15:24:14 | INFO     | [CLAUDE] Processing item from /Needs_Action/email/
```

### Audit Logging

All actions are logged to `/Logs/audit/YYYY-MM-DD.json`:
- Email sent/received
- WhatsApp messages
- LinkedIn posts/messages
- Facebook posts/messages
- Odoo invoices/payments
- Error recovery attempts
- Orchestrator actions

---

## Error Recovery

### Retry Logic
- **Max attempts:** 3
- **Backoff:** Exponential (1s, 2s, 4s)
- **Logged to:** Audit log

### Circuit Breaker
- **Failure threshold:** 3 consecutive failures
- **Recovery timeout:** 300 seconds (5 minutes)
- **States:** CLOSED → OPEN → HALF_OPEN → CLOSED

### Health Checks
- **Services:** Odoo, Facebook, Email, LinkedIn, WhatsApp
- **Cache TTL:** 60 seconds
- **Usage:** Check before making service calls

---

## Security

### Credential Management
- All credentials in `.env` (gitignored)
- OAuth tokens in `/credentials/` (gitignored)
- WhatsApp session in `/sessions/` (gitignored)
- Never commit sensitive files

### Permission Boundaries

| Action | Auto-Execute | Require Approval |
|--------|--------------|------------------|
| Email to known contacts | ✅ Yes | ❌ No |
| Email to new contacts | ❌ No | ✅ Yes |
| WhatsApp simple reply | ✅ Yes | ❌ No |
| WhatsApp business msg | ❌ No | ✅ Yes |
| LinkedIn/Facebook post | ❌ No | ✅ Yes |
| Payment | ❌ No | ✅ Yes |
| Invoice creation | ❌ No | ✅ Yes |

---

## Requirements

### Software
- Python 3.13+
- Claude Code (installed and in PATH)
- Obsidian (optional, for GUI)
- Docker Desktop (for Odoo)
- Node.js v24+ (for MCP servers)

### API Credentials
- Gmail API (OAuth 2.0)
- LinkedIn API (Access Token)
- Facebook Graph API (Page Access Token)
- WhatsApp Web (Session)
- Odoo (Username/Password)

### Hardware
- Minimum: 8GB RAM, 4-core CPU, 20GB free disk
- Recommended: 16GB RAM, 8-core CPU, SSD
- For always-on: Dedicated mini-PC or cloud VM

---

## Testing

### Test All Services
```bash
uv run python tests/test_services.py
```

### Test Individual Services
```bash
# WhatsApp
uv run python tests/test_whatsapp_only.py

# Email
uv run python tests/test_email_only.py

# LinkedIn
uv run python tests/test_linkedin_only.py

# Facebook
uv run python tests/test_facebook_only.py

# WhatsApp Standalone
uv run python tests/test_whatsapp_standalone.py
```

### Test Results (All Passed ✅)
| Service | Status | Details |
|---------|--------|---------|
| WhatsApp | ✅ PASSED | Message sent to "Me Telenor" |
| Email | ✅ PASSED | Sent to binadnanosama@gmail.com |
| LinkedIn | ✅ PASSED | Post ID: urn:li:share:7438400164194734080 |
| Facebook | ✅ PASSED | Post ID: 969310802941448_122103426987207806 |

---

## Troubleshooting

### WhatsApp Not Sending
```bash
# Check if session exists
ls sessions/whatsapp/

# Re-authenticate (scan QR code)
uv run python -m watchers.whatsapp --no-headless
```

### Gmail Auth Failed
```bash
# Re-run OAuth setup
uv run python -c "from watchers.gmail_watcher import setup_oauth; setup_oauth()"
```

### Odoo Connection Failed
```bash
# Check if Odoo is running
cd odoo && docker-compose ps

# Restart Odoo
cd odoo && docker-compose restart
```

### Dashboard Update Timeout
- **Default timeout:** 10 minutes (600 seconds)
- **Check interval:** 20 minutes (1200 seconds)
- **Fix:** Increase timeout in `orchestrator/main.py` line 1298

### Ralph Wiggum Not Looping
- Check `trigger_claude_process()` in `orchestrator/main.py`
- Verify max_iterations is set (default: 5)
- Check completion detection logic

---

## Gold Tier Completion Status

| # | Requirement | Status |
|---|-------------|--------|
| 1 | All Silver requirements | ✅ Complete |
| 2 | Full cross-domain integration | ✅ Complete (Personal + Business) |
| 3 | Odoo accounting integration | ✅ Complete (Docker + MCP) |
| 4 | Facebook/Instagram integration | ✅ Complete (Facebook done, Instagram via FB Graph) |
| 5 | Twitter (X) integration | ❌ Not implemented |
| 6 | Multiple MCP servers | ✅ Complete (Main + Odoo) |
| 7 | Weekly CEO Briefing | ✅ Complete (All data sources) |
| 8 | Error recovery & graceful degradation | ✅ Complete (Retry + Circuit Breaker) |
| 9 | Comprehensive audit logging | ✅ Complete (JSON logs) |
| 10 | Ralph Wiggum loop | ✅ Complete (Max 5 iterations) |
| 11 | Documentation | ✅ Complete |
| 12 | All AI functionality as Agent Skills | ✅ Complete (13 skills) |

**Overall Gold Tier Completion: ~92%** (Only Twitter/X missing)

---

## Next Steps

### Gold Tier Polish
- [ ] Add Instagram-specific features (via Facebook Graph API)
- [ ] Add Twitter/X integration (watcher + service + skills)
- [ ] Performance optimization for large message volumes

### Platinum Tier (Next Level)
- [ ] Cloud deployment (24/7 operation)
- [ ] Work-zone specialization (Cloud vs Local)
- [ ] Vault sync for delegation
- [ ] Odoo on Cloud VM
- [ ] A2A messaging upgrade

---

## Support & Resources

### Documentation
- `CLAUDE.md` - Project overview
- `docs/` - Additional guides
- `.claude/skills/` - Agent skill documentation

### Setup Guides
- Odoo: `odoo/README.md`
- Gmail OAuth: Run `--setup-oauth`
- Facebook: Facebook Developer Console

### Community
- Hackathon meetings: Wednesdays 10 PM
- Zoom: https://us06web.zoom.us/j/87188707642
- YouTube: https://www.youtube.com/@panaversity

---

*Last Updated: March 2026*
*Gold Tier - AI Employee Project*
*Tagline: Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.*
