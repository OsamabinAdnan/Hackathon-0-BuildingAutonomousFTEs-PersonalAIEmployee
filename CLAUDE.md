# Personal AI Employee - Digital FTE Project

## Project Overview

**Tagline:** *Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.*

This project builds a "Digital FTE" (Full-Time Equivalent) - an AI agent powered by Claude Code and Obsidian that proactively manages personal and business affairs 24/7. Think of it as hiring a senior employee who figures out how to solve problems autonomously.

### Key Innovation
The "Monday Morning CEO Briefing" - the AI autonomously audits bank transactions and tasks to report revenue and bottlenecks, transforming the AI from a chatbot into a proactive business partner.

---

## Architecture & Tech Stack

### Core Components

| Component | Technology | Purpose |
|-----------|------------|---------|
| **The Brain** | Claude Code | Reasoning engine with Ralph Wiggum Stop hook for continuous iteration |
| **The Memory/GUI** | Obsidian | Local Markdown dashboard for data storage and visualization |
| **The Senses (Watchers)** | Python scripts | Monitor Gmail, WhatsApp, LinkedIn, filesystems to trigger AI |
| **The Hands (MCP)** | Model Context Protocol servers | Handle external actions like emails, payments, social posts |

### Architecture Pattern: Perception → Reasoning → Action

```
EXTERNAL SOURCES (Gmail, WhatsApp, Bank APIs, Files)
        ↓
PERCEPTION LAYER (Watchers)
        ↓
OBSIDIAN VAULT (Local Storage)
        ↓
REASONING LAYER (Claude Code)
        ↓
ACTION LAYER (MCP Servers) → EXTERNAL ACTIONS
```

### Solving the "Lazy Agent" Problem
- **Watchers** wake the agent up rather than waiting for user input
- **Ralph Wiggum** (Stop hook pattern) keeps it working until done

---

## Project Structure

```
E:\Hackathon-0-Personal-FTE\
├── vault/                          # Obsidian vault (knowledge base)
│   ├── Dashboard.md               # Real-time summary of business state
│   ├── Company_Handbook.md        # Rules of Engagement
│   ├── Business_Goals.md          # Objectives and metrics
│   ├── Needs_Action/              # Incoming tasks (categorized)
│   │   ├── email/
│   │   ├── whatsapp/
│   │   ├── linkedin/
│   │   └── files/
│   ├── Plans/                     # Claude-generated action plans
│   ├── Pending_Approval/          # HITL approval requests
│   ├── Approved/                  # User-approved actions
│   ├── Rejected/                  # User-rejected actions
│   ├── Done/                      # Completed tasks
│   ├── Logs/                      # Audit logs
│   └── Briefings/                 # CEO briefing reports
│
├── watchers/                       # Perception layer scripts
│   ├── base_watcher.py            # Abstract base class
│   ├── gmail_watcher.py           # Gmail API monitoring
│   ├── whatsapp_watcher.py        # WhatsApp Web automation
│   ├── linkedin_watcher.py        # LinkedIn monitoring
│   └── filesystem_watcher.py      # Local file drops
│
├── mcp_server/                     # Action layer (MCP servers)
│   ├── server.py                  # Main MCP server
│   ├── whatsapp_service.py        # WhatsApp message sending
│   └── direct_executor.py         # Direct action execution
│
├── orchestrator/                   # Orchestration layer
│   └── main.py                    # Master process manager
│
├── integrations/                   # External integrations
│   └── linkedin_poster.py         # LinkedIn auto-posting
│
├── credentials/                    # OAuth credentials (gitignored)
├── sessions/                       # Browser session data
│   └── whatsapp/                  # WhatsApp Web session
│
├── .claude/                        # Claude Code configuration
│   ├── skills/                    # Agent skills
│   ├── settings.json              # MCP server config
│   └── hooks/                     # Ralph Wiggum hook
│
├── .env                           # Environment variables (gitignored)
├── CLAUDE.md                      # This file
└── README.md                      # Project documentation
```

---

## Human FTE vs Digital FTE Comparison

| Feature | Human FTE | Digital FTE |
|----------|-----------|-------------|
| Availability | 40 hours/week | 168 hours/week (24/7) |
| Monthly Cost | $4,000 – $8,000+ | $500 – $2,000 |
| Ramp-up Time | 3 – 6 Months | Instant (via SKILL.md) |
| Consistency | Variable (85–95%) | Predictable (99%+) |
| Scaling | Linear | Exponential (Instant duplication) |
| Cost per Task | ~$3.00 – $6.00 | ~$0.25 – $0.50 |
| Annual Hours | ~2,000 hours | ~8,760 hours |

---

## Tiered Deliverables

### Bronze Tier: Foundation (8-12 hours)
- [x] Obsidian vault with Dashboard.md and Company_Handbook.md
- [x] One working Watcher script (Gmail OR file system monitoring)
- [x] Claude Code reading from and writing to the vault
- [x] Basic folder structure: /Inbox, /Needs_Action, /Done
- [x] AI functionality as Agent Skills

### Silver Tier: Functional Assistant (20-30 hours)
- [x] All Bronze requirements
- [x] Two or more Watcher scripts (Gmail + WhatsApp + LinkedIn)
- [x] Auto-post on LinkedIn for business/sales
- [x] Claude reasoning loop creating Plan.md files
- [x] One working MCP server for external action
- [x] Human-in-the-loop approval workflow
- [x] Basic scheduling via cron or Task Scheduler
- [x] All AI functionality as Agent Skills

### Gold Tier: Autonomous Employee (40+ hours)
- [ ] All Silver requirements
- [ ] Full cross-domain integration (Personal + Business)
- [ ] Odoo Community accounting integration via MCP
- [ ] Facebook/Instagram integration
- [ ] Twitter (X) integration
- [ ] Multiple MCP servers for different action types
- [ ] Weekly Business and Accounting Audit with CEO Briefing
- [ ] Error recovery and graceful degradation
- [ ] Comprehensive audit logging
- [ ] Ralph Wiggum loop for autonomous multi-step completion
- [ ] Architecture documentation

### Platinum Tier: Always-On Cloud + Local Executive (60+ hours)
- [ ] All Gold requirements
- [ ] 24/7 Cloud deployment with health monitoring
- [ ] Work-zone specialization (Cloud vs Local ownership)
- [ ] Delegation via Synced Vault
- [ ] Security: Secrets never sync to cloud
- [ ] Odoo Community on Cloud VM
- [ ] Optional A2A messaging upgrade

---

## Watcher Architecture

### Base Pattern

All watchers follow this structure:

```python
class BaseWatcher(ABC):
    def __init__(self, vault_path: str, check_interval: int = 60):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.check_interval = check_interval

    @abstractmethod
    def check_for_updates(self) -> list:
        '''Return list of new items to process'''
        pass

    @abstractmethod
    def create_action_file(self, item) -> Path:
        '''Create .md file in Needs_Action folder'''
        pass

    def run(self):
        while True:
            items = self.check_for_updates()
            for item in items:
                self.create_action_file(item)
            time.sleep(self.check_interval)
```

### Implemented Watchers

| Watcher | File | Check Interval | Purpose |
|---------|------|----------------|---------|
| Gmail | `watchers/gmail_watcher.py` | 120s | Monitor unread important emails |
| WhatsApp | `watchers/whatsapp_watcher.py` | 30s | Monitor for keyword messages |
| LinkedIn | `watchers/linkedin_watcher.py` | 300s | Monitor engagement, messages |
| FileSystem | `watchers/filesystem_watcher.py` | Real-time | Monitor local drop folders |

---

## MCP Server Configuration

### Recommended MCP Servers

| Server | Capabilities | Use Case |
|--------|--------------|----------|
| filesystem | Read, write, list files | Built-in, use for vault |
| email-mcp | Send, draft, search emails | Gmail integration |
| browser-mcp | Navigate, click, fill forms | Payment portals |
| calendar-mcp | Create, update events | Scheduling |
| slack-mcp | Send messages, read channels | Team communication |

### Configuration Example

```json
// ~/.config/claude-code/mcp.json
{
  "servers": [
    {
      "name": "email",
      "command": "node",
      "args": ["/path/to/email-mcp/index.js"],
      "env": {
        "GMAIL_CREDENTIALS": "/path/to/credentials.json"
      }
    },
    {
      "name": "browser",
      "command": "npx",
      "args": ["@anthropic/browser-mcp"],
      "env": {
        "HEADLESS": "true"
      }
    }
  ]
}
```

---

## Human-in-the-Loop (HITL) Pattern

For sensitive actions, Claude creates an approval request file instead of acting directly:

```markdown
# /Vault/Pending_Approval/PAYMENT_Client_A_2026-01-07.md
---
type: approval_request
action: payment
amount: 500.00
recipient: Client A
reason: Invoice #1234 payment
created: 2026-01-07T10:30:00Z
expires: 2026-01-08T10:30:00Z
status: pending
---

## Payment Details
- Amount: $500.00
- To: Client A (Bank: XXXX1234)

## To Approve
Move this file to /Approved folder.

## To Reject
Move this file to /Rejected folder.
```

### Permission Boundaries

| Action Category | Auto-Approve Threshold | Always Require Approval |
|-----------------|------------------------|-------------------------|
| Email replies | To known contacts | New contacts, bulk sends |
| Payments | < $50 recurring | All new payees, > $100 |
| Social media | Scheduled posts | Replies, DMs |
| File operations | Create, read | Delete, move outside vault |

---

## Ralph Wiggum Loop (Persistence Pattern)

Claude Code runs in interactive mode - after processing, it waits for more input. The Ralph Wiggum pattern keeps the AI Employee working autonomously:

### How It Works
1. Orchestrator creates state file with prompt
2. Claude works on task
3. Claude tries to exit
4. Stop hook checks: Is task file in /Done?
5. YES → Allow exit (complete)
6. NO → Block exit, re-inject prompt
7. Repeat until complete or max iterations

### Usage

```bash
/ralph-loop "Process all files in /Needs_Action, move to /Done when complete" \
  --completion-promise "TASK_COMPLETE" \
  --max-iterations 10
```

### Completion Strategies
1. **Promise-based:** Claude outputs `<promise>TASK_COMPLETE</promise>`
2. **File movement (Gold tier):** Stop hook detects when task file moves to /Done

Reference: https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum

---

## Agent Skills (8 Total)

### Workflow Skills
| Skill | Purpose |
|-------|---------|
| `process-inbox` | Process all files in /Needs_Action |
| `create-plan` | Create Plan.md with action steps |
| `process-tasks` | Execute planned tasks |
| `update-dashboard` | Update Dashboard.md with results |

### Action Skills
| Skill | Purpose |
|-------|---------|
| `send-email` | Send email via MCP |
| `send-whatsapp` | Send WhatsApp message |
| `post-linkedin` | Post to LinkedIn |
| `send-linkedin-message` | Send LinkedIn message |

---

## CEO Briefing System

### Business_Goals.md Template

```markdown
# /Vault/Business_Goals.md
---
last_updated: 2026-01-07
review_frequency: weekly
---

## Q1 2026 Objectives

### Revenue Target
- Monthly goal: $10,000
- Current MTD: $4,500

### Key Metrics to Track
| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Client response time | < 24 hours | > 48 hours |
| Invoice payment rate | > 90% | < 80% |
| Software costs | < $500/month | > $600/month |

### Subscription Audit Rules
Flag for review if:
- No login in 30 days
- Cost increased > 20%
- Duplicate functionality with another tool
```

### CEO Briefing Output Template

```markdown
# /Vault/Briefings/2026-01-06_Monday_Briefing.md
---
generated: 2026-01-06T07:00:00Z
period: 2025-12-30 to 2026-01-05
---

# Monday Morning CEO Briefing

## Executive Summary
Strong week with revenue ahead of target. One bottleneck identified.

## Revenue
- **This Week**: $2,450
- **MTD**: $4,500 (45% of $10,000 target)
- **Trend**: On track

## Completed Tasks
- [x] Client A invoice sent and paid
- [x] Project Alpha milestone 2 delivered

## Bottlenecks
| Task | Expected | Actual | Delay |
|------|----------|--------|-------|
| Client B proposal | 2 days | 5 days | +3 days |

## Proactive Suggestions
- **Notion**: No activity in 45 days. Cancel subscription?
```

---

## Security Architecture

### Credential Management
- **Never** store credentials in plain text or in Obsidian vault
- Use environment variables for API keys
- Use secrets manager (macOS Keychain, Windows Credential Manager, 1Password CLI)
- Create `.env` file (add to `.gitignore`)
- Rotate credentials monthly

### .env Structure

```bash
# .env - NEVER commit this file
GMAIL_CLIENT_ID=your_client_id
GMAIL_CLIENT_SECRET=your_client_secret
BANK_API_TOKEN=your_token
WHATSAPP_SESSION_PATH=/secure/path/session
LINKEDIN_ACCESS_TOKEN=your_linkedin_token
DRY_RUN=true
```

### Sandboxing & Isolation
- **Development Mode:** `DEV_MODE` flag prevents real external actions
- **Dry Run:** All action scripts support `--dry-run` flag
- **Separate Accounts:** Use test/sandbox accounts during development
- **Rate Limiting:** Max 10 emails, 3 payments per hour

### Audit Logging

Every action must be logged:

```json
{
  "timestamp": "2026-01-07T10:30:00Z",
  "action_type": "email_send",
  "actor": "claude_code",
  "target": "client@example.com",
  "parameters": {"subject": "Invoice #123"},
  "approval_status": "approved",
  "approved_by": "human",
  "result": "success"
}
```

Store in `/Vault/Logs/YYYY-MM-DD.json` - retain 90+ days.

---

## Error Handling & Recovery

### Error Categories

| Category | Examples | Recovery Strategy |
|----------|----------|-------------------|
| Transient | Network timeout, API rate limit | Exponential backoff retry |
| Authentication | Expired token, revoked access | Alert human, pause operations |
| Logic | Claude misinterprets message | Human review queue |
| Data | Corrupted file, missing field | Quarantine + alert |
| System | Orchestrator crash, disk full | Watchdog + auto-restart |

### Graceful Degradation
- **Gmail API down:** Queue emails locally
- **Banking API timeout:** Never auto-retry payments
- **Claude Code unavailable:** Watchers continue collecting
- **Obsidian vault locked:** Write to temp folder

### Watchdog Process

```python
PROCESSES = {
    'orchestrator': 'python orchestrator.py',
    'gmail_watcher': 'python gmail_watcher.py',
    'file_watcher': 'python filesystem_watcher.py'
}

def check_and_restart():
    for name, cmd in PROCESSES.items():
        if not is_process_running(pid_file):
            logger.warning(f'{name} not running, restarting...')
            proc = subprocess.Popen(cmd.split())
            notify_human(f'{name} was restarted')
```

---

## Process Management

Watchers are daemon processes that need process management:

### Why Process Management?
- Scripts terminate if TTY/SSH closes
- Scripts crash on unhandled exceptions
- No auto-recovery after system reboot

### PM2 Quick Start (Recommended)

```bash
# Install PM2
npm install -g pm2

# Start watcher and keep alive
pm2 start gmail_watcher.py --interpreter python3

# Freeze for boot startup
pm2 save
pm2 startup
```

---

## Continuous vs Scheduled Operations

| Operation Type | Example Task | Trigger |
|----------------|--------------|---------|
| **Scheduled** | Daily Briefing at 8:00 AM | cron/Task Scheduler |
| **Continuous** | WhatsApp lead capture | Python watchdog |
| **Project-Based** | Q1 Tax Prep | Manual file drop |

---

## Prerequisites & Setup

### Required Software

| Component | Requirement | Purpose |
|-----------|-------------|---------|
| Claude Code | Pro subscription or free Gemini API with router | Primary reasoning engine |
| Obsidian | v1.10.6+ (free) | Knowledge base & dashboard |
| Python | 3.13 or higher | Sentinel scripts & orchestration |
| Node.js | v24+ LTS | MCP servers & automation |
| Github Desktop | Latest stable | Version control for vault |

### Hardware Requirements
- Minimum: 8GB RAM, 4-core CPU, 20GB free disk space
- Recommended: 16GB RAM, 8-core CPU, SSD storage
- Always-on: Dedicated mini-PC or cloud VM
- Internet: 10+ Mbps for API calls

### Skill Level Expectations
- Comfortable with CLI (terminal/bash)
- Understanding of file systems
- Familiarity with APIs
- No prior AI/ML experience required
- Able to use and prompt Claude Code

---

## Learning Resources

### Prerequisites
| Topic | Resource |
|-------|----------|
| Presentation | [Google Slides](https://docs.google.com/presentation/d/1UGvCUk1-O8m5i-aTWQNxzg8EXoKzPa8fgcwfNh8vRjQ/edit) |
| Claude Code Fundamentals | [Textbook](https://agentfactory.panaversity.org/docs/AI-Tool-Landscape/claude-code-features-and-workflows) |
| Obsidian Fundamentals | help.obsidian.md/Getting+started |
| MCP Introduction | modelcontextprotocol.io/introduction |
| Agent Skills | platform.claude.com/docs/en/agents-and-tools/agent-skills/overview |

### Core Learning
| Topic | Resource |
|-------|----------|
| Claude + Obsidian | youtube.com/watch?v=sCIS05Qt79Y |
| Building MCP Servers | modelcontextprotocol.io/quickstart |
| Claude Agent Teams | youtube.com/watch?v=0J2_YGuNrDo |
| Gmail API Setup | developers.google.com/gmail/api/quickstart |
| Playwright Automation | playwright.dev/python/docs/intro |

---

## Ethics & Responsible Automation

### When AI Should NOT Act Autonomously
- Emotional contexts (condolences, conflicts, negotiations)
- Legal matters (contracts, legal advice, filings)
- Medical decisions
- Financial edge cases (unusual transactions, large amounts)
- Irreversible actions

### Transparency Principles
- Disclose AI involvement in communications
- Maintain audit trails
- Allow opt-out for contacts
- Schedule weekly AI decision reviews

### Oversight Schedule
- **Daily:** 2-minute dashboard check
- **Weekly:** 15-minute action log review
- **Monthly:** 1-hour comprehensive audit
- **Quarterly:** Full security and access review

---

## Research Meetings

**When:** Every Wednesday at 10:00 PM

**Zoom:** https://us06web.zoom.us/j/87188707642?pwd=a9XloCsinvn1JzICbPc2YGUvWTbOTr.1
- Meeting ID: 871 8870 7642
- Passcode: 744832

**YouTube (if full):** https://www.youtube.com/@panaversity

---

## Judging Criteria

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Functionality | 30% | Does it work? Are core features complete? |
| Innovation | 25% | Creative solutions, novel integrations |
| Practicality | 20% | Would you actually use this daily? |
| Security | 15% | Proper credential handling, HITL safeguards |
| Documentation | 10% | Clear README, setup instructions, demo |

---

## Next Steps

1. **For Cloud FTE:** See [Advanced Custom Cloud FTE Architecture](https://docs.google.com/document/d/15GuwZwIOQy_g1XsIJjQsFNHCTQTWoXQhWGVMhiH0swc/edit)
2. **For Odoo Integration:** See [Odoo JSON-RPC API](https://www.odoo.com/documentation/19.0/developer/reference/external_api.html)
