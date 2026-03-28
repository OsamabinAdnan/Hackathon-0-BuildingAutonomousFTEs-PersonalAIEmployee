# Personal AI Employee Hackathon 0

**Tagline:** *Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.*

**Build Status:**
- 🥉 **Bronze Tier:** ✅ Complete
- 🥈 **Silver Tier:** ✅ Complete
- 🥇 **Gold Tier:** ✅ Complete
- 🏆 **Platinum Tier:** ✅ Local Simulation Complete (Cloud Deployment Ready)

---

## Project Overview

This project builds a **"Digital FTE" (Full-Time Equivalent)** - an AI agent powered by Claude Code and Obsidian that proactively manages personal and business affairs 24/7. Think of it as hiring a senior employee who figures out how to solve problems autonomously.

### Key Innovation

The **"Monday Morning CEO Briefing"** - the AI autonomously audits bank transactions and tasks to report revenue and bottlenecks, transforming the AI from a chatbot into a proactive business partner.

---

## Architecture: Perception → Reasoning → Action

```
EXTERNAL SOURCES (Gmail, WhatsApp, LinkedIn, Facebook, Bank APIs, Files)
        ↓
PERCEPTION LAYER (Watchers - Python scripts)
        ↓
OBSIDIAN VAULT (Local Markdown Storage)
        ↓
REASONING LAYER (Claude Code)
        ↓
ACTION LAYER (MCP Servers) → EXTERNAL ACTIONS (Email, Posts, Payments)
```

### Core Components

| Component | Technology | Purpose |
|-----------|------------|---------|
| **The Brain** | Claude Code | Reasoning engine with Ralph Wiggum Stop hook |
| **The Memory/GUI** | Obsidian | Local Markdown dashboard for data storage |
| **The Senses** | Python Watchers | Monitor Gmail, WhatsApp, LinkedIn, filesystems |
| **The Hands** | MCP Servers | Handle external actions (emails, payments, posts) |

---

## Human FTE vs Digital FTE Comparison

| Feature | Human FTE | Digital FTE |
|---------|-----------|-------------|
| Availability | 40 hours/week | 168 hours/week (24/7) |
| Monthly Cost | $4,000 – $8,000+ | $500 – $2,000 |
| Ramp-up Time | 3 – 6 Months | Instant (via SKILL.md) |
| Consistency | Variable (85–95%) | Predictable (99%+) |
| Scaling | Linear | Exponential (Instant duplication) |
| Cost per Task | ~$3.00 – $6.00 | ~$0.25 – $0.50 |
| Annual Hours | ~2,000 hours | ~8,760 hours |

**The 'Aha!' Moment:** A Digital FTE works nearly 9,000 hours a year vs a human's 2,000. The cost per task reduction (from ~$5.00 to ~$0.50) is an 85–90% cost saving.

---

## Tier Structure

This hackathon has **4 achievement tiers**. Choose your target based on your experience and ambition.

### 🥉 Bronze Tier: Foundation (8-12 hours)

**Status:** ✅ Complete

**Features:**
- Obsidian vault with Dashboard.md and Company_Handbook.md
- One working Watcher script (FileSystem monitoring)
- Claude Code reading from and writing to the vault
- Basic folder structure: /Inbox, /Needs_Action, /Done
- Agent Skills implementation

**Location:** [`Bronze_Tier/`](./Bronze_Tier/)

---

### 🥈 Silver Tier: Functional Assistant (20-30 hours)

**Status:** ✅ Complete

**New Features:**
- All Bronze features plus:
- 4 Watcher scripts (Gmail, WhatsApp, LinkedIn, FileSystem)
- LinkedIn auto-posting for business
- Claude reasoning loop with Plan.md files
- MCP server for external actions (Email, WhatsApp, LinkedIn)
- Human-in-the-loop approval workflow
- Basic scheduling via Task Scheduler
- 7 Agent Skills

**Location:** [`Silver_Tier/`](./Silver_Tier/)

---

### 🥇 Gold Tier: Autonomous Employee (40+ hours)

**Status:** ✅ Complete

**New Features:**
- All Silver features plus:
- **Odoo Accounting Integration** - Docker Compose with Odoo 19 + PostgreSQL
- **Facebook Business Integration** - Page posting, messaging, auto-posting
- **LinkedIn Auto-Posting** - 7 templates, scheduled posting
- **Multiple MCP Servers** - Separate servers for different domains
- **Weekly CEO Briefing** - Automated business audit
- **Ralph Wiggum Loop** - Autonomous multi-step task completion
- **Audit Logging** - Comprehensive JSON logging
- **Error Recovery** - Retry logic & circuit breaker
- **14+ MCP Tools** - Invoice creation, payment recording, financial reports
- **13 Agent Skills** - Workflow, action, Odoo, and social media skills

**Location:** [`Gold_Tier/`](./Gold_Tier/)

---

### 🏆 Platinum Tier: Always-On Cloud + Local Executive (60+ hours)

**Status:** ✅ Local Simulation Complete (Cloud Deployment Ready)

**New Features:**
- All Gold features plus:
- **Dual-Agent Architecture** - Cloud (draft_only) + Local (full)
- **Work-Zone Specialization** - Cloud drafts, Local executes
- **Security Hardening** - WhatsApp stays local, payments require approval
- **Cloud→Local Handoff** - /Updates/ folder, claim-by-move rule
- **Draft-Only Mode** - All MCP tools support draft creation
- **Git Sync Ready** - Vault .gitignore, sync scripts

**Current Deployment:** Local Simulation (Single Machine)  
**Cloud Deployment:** Ready (Zero code changes needed)

**Location:** [`Platinum_Tier/`](./Platinum_Tier/)

---

## Project Structure

```
E:\Hackathon-0-Personal-FTE\
├── README.md                     # This file (project overview)
├── CLAUDE.md                     # Main project documentation
├── Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md
│
├── Bronze_Tier/                  # 🥉 Foundation
│   ├── AI_Employee_Vault_FTE/    # Obsidian vault
│   ├── orchestrator/             # Main controller
│   ├── watchers/                 # FileSystem watcher
│   ├── .claude/                  # Claude Code config
│   └── README.md
│
├── Silver_Tier/                  # 🥈 Functional Assistant
│   ├── AI_Employee_Vault_FTE/
│   ├── orchestrator/
│   ├── watchers/                 # Gmail, WhatsApp, LinkedIn, FileSystem
│   ├── mcp_server/               # Email, WhatsApp, LinkedIn services
│   ├── integrations/             # LinkedIn auto-posting
│   ├── scheduling/               # Task Scheduler scripts
│   └── README.md
│
├── Gold_Tier/                    # 🥇 Autonomous Employee
│   ├── AI_Employee_Vault_FTE/
│   ├── orchestrator/             # Ralph Wiggum integration
│   ├── watchers/                 # + Facebook watcher
│   ├── mcp_server/               # + Facebook, Odoo services
│   ├── integrations/             # + Facebook auto-posting
│   ├── odoo/                     # Docker Compose setup
│   ├── ralph_wiggum/             # Autonomous task completion
│   ├── audit/                    # Logging & error recovery
│   ├── tests/                    # 22 test files
│   └── README.md
│
└── Platinum_Tier/                # 🏆 Production-Ready
    ├── AI_Employee_Vault_FTE/
    ├── orchestrator/             # EXECUTION_MODE support
    ├── mcp_server/               # Draft-only mode
    ├── .env.cloud                # Cloud Agent config
    ├── .env.local                # Local Agent config
    ├── run_cloud_agent.bat       # Launch Cloud Agent
    ├── run_local_agent.bat       # Launch Local Agent
    ├── sync_vault.bat            # Vault sync script
    ├── setup_auto_sync.bat       # Auto-sync scheduler
    └── docs/Platinum_docs/       # 6 comprehensive guides
```

---

## Quick Start

### Prerequisites

| Software | Version | Purpose |
|----------|---------|---------|
| [Claude Code](https://claude.com/product/claude-code) | Latest | Primary reasoning engine |
| [Obsidian](https://obsidian.md/download) | v1.10.6+ | Knowledge base & dashboard |
| [Python](https://www.python.org/downloads/) | 3.13+ | Watcher scripts & orchestration |
| [Node.js](https://nodejs.org/) | v24+ LTS | MCP servers |
| [Docker Desktop](https://www.docker.com/products/docker-desktop) | Latest | Odoo (Gold+ tiers) |

### Choose Your Tier

```bash
# Bronze Tier (Foundation)
cd Bronze_Tier
uv sync
uv run python -m orchestrator

# Silver Tier (Functional Assistant)
cd Silver_Tier
uv sync
uv run python -m orchestrator

# Gold Tier (Autonomous Employee)
cd Gold_Tier
uv sync
uv run python -m orchestrator

# Platinum Tier (Production-Ready)
cd Platinum_Tier
uv sync

# Terminal 1 - Cloud Agent
.\run_cloud_agent.bat

# Terminal 2 - Local Agent
.\run_local_agent.bat
```

---

## Agent Skills

### Bronze Tier (2 Skills)
| Skill | Purpose |
|-------|---------|
| `/process-inbox` | Process files in /Needs_Action |
| `/update-dashboard` | Update Dashboard.md |

### Silver Tier (7 Skills)
| Skill | Purpose |
|-------|---------|
| All Bronze skills + | |
| `/send-email` | Send via Gmail API |
| `/send-whatsapp` | Send via WhatsApp Web |
| `/post-linkedin` | Post to LinkedIn |
| `/send-linkedin-message` | Send LinkedIn DM |
| `/browsing-with-playwright` | Browser automation |

### Gold/Platinum Tier (13 Skills)
| Skill | Purpose |
|-------|---------|
| All Silver skills + | |
| `/generate-briefing` | Generate CEO briefing |
| `/post-facebook` | Post to Facebook |
| `/send-facebook-message` | Send Facebook message |
| `/create-invoice` | Create Odoo invoice |
| `/record-payment` | Record Odoo payment |
| `/get-financial-report` | Get Odoo financials |

---

## Human-in-the-Loop (HITL) Workflow

For sensitive actions, the AI creates an approval request instead of acting directly:

```
1. Claude processes file → Creates approval request → /Pending_Approval/
2. Human reviews the request
3. Human decides:
   - APPROVE: Move to /Approved/ → Orchestrator executes
   - REJECT: Move to /Rejected/ → Orchestrator archives
4. Files moved to /Done/ or /Archive/
```

### Approval Thresholds

| Action | Auto-Approve | Require Approval |
|--------|--------------|------------------|
| Email to known contacts | ✅ Yes | ❌ No |
| Email to new contacts | ❌ No | ✅ Yes |
| WhatsApp simple reply | ✅ Yes | ❌ No |
| LinkedIn/Facebook post | ❌ No | ✅ Yes |
| Payment | ❌ No | ✅ Yes |
| Invoice creation | ❌ No | ✅ Yes |

---

## Watcher Configuration

| Watcher | Check Interval | Monitors | Output Folder |
|---------|---------------|----------|---------------|
| FileSystem | Real-time | /Inbox/ folder | /Needs_Action/files/ |
| Gmail | 701s (~12 min) | Unread emails | /Needs_Action/email/ |
| WhatsApp | 571s (~9.5 min) | Keyword messages | /Needs_Action/whatsapp/ |
| LinkedIn | 839s (~14 min) | Messages, engagement | /Needs_Action/linkedin/ |
| Facebook | 659s (~11 min) | Messages, comments | /Needs_Action/facebook/ |
| Odoo | Event-based | Transactions | /Needs_Action/odoo/ |

---

## Scheduled Tasks

| Task | Schedule | Script |
|------|----------|--------|
| Dashboard Update | Every 20 minutes | Built into orchestrator |
| Weekly CEO Briefing | Monday 10 AM | `scheduling/weekly_briefing.ps1` |
| LinkedIn Post | Mon & Thu 9 AM | `scheduling/linkedin_post.ps1` |
| Facebook Post | Tue & Fri 10 AM | `scheduling/facebook_post.ps1` |

---

## Security

### Credential Management

- All credentials stored in `.env` (gitignored)
- OAuth tokens in `/credentials/` (gitignored)
- WhatsApp session in `/sessions/` (gitignored)
- **Never commit sensitive files**

### Platinum Tier Security

| Credential | Cloud VM | Local Machine |
|------------|----------|---------------|
| Gmail OAuth | ✅ Limited | ✅ Full |
| LinkedIn Token | ✅ Limited | ✅ Full |
| Facebook Token | ✅ Limited | ✅ Full |
| WhatsApp Session | ❌ **NEVER** | ✅ Local only |
| Banking API Token | ❌ **NEVER** | ✅ Local only |
| Payment API Key | ❌ **NEVER** | ✅ Local only |

---

## Documentation by Tier

| Tier | Documentation |
|------|---------------|
| **Bronze** | [`Bronze_Tier/README.md`](./Bronze_Tier/README.md) |
| **Silver** | [`Silver_Tier/README.md`](./Silver_Tier/README.md) |
| **Gold** | [`Gold_Tier/README.md`](./Gold_Tier/README.md) |
| **Platinum** | [`Platinum_Tier/README.md`](./Platinum_Tier/README.md) |

### Platinum Tier Detailed Docs

- [`PLATINUM_TIER_COMPLETE_GUIDE.md`](./Platinum_Tier/docs/Platinum_docs/PLATINUM_TIER_COMPLETE_GUIDE.md)
- [`IMPLEMENTATION_DETAILS.md`](./Platinum_Tier/docs/Platinum_docs/IMPLEMENTATION_DETAILS.md)
- [`IMPLEMENTATION_STATUS_ROADMAP.md`](./Platinum_Tier/docs/Platinum_docs/IMPLEMENTATION_STATUS_ROADMAP.md)
- [`PLATINUM_TEST_GUIDE.md`](./Platinum_Tier/docs/Platinum_docs/PLATINUM_TEST_GUIDE.md)
- [`PLATINUM_TIER_LOCAL_COMPLETE.md`](./Platinum_Tier/docs/Platinum_docs/PLATINUM_TIER_LOCAL_COMPLETE.md)

---

## Official Hackathon Specification

For complete requirements and architecture details, see:

**[Personal AI Employee Hackathon 0: Building Autonomous FTEs in 2026](./Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026.md)**

---

## Learning Resources

### Prerequisites
| Topic | Resource |
|-------|----------|
| Claude Code Fundamentals | [Textbook](https://agentfactory.panaversity.org/docs/AI-Tool-Landscape/claude-code-features-and-workflows) |
| Obsidian Fundamentals | [help.obsidian.md](https://help.obsidian.md/Getting+started) |
| MCP Introduction | [modelcontextprotocol.io](https://modelcontextprotocol.io/introduction) |
| Agent Skills | [platform.claude.com](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) |

### Core Learning
| Topic | Resource |
|-------|----------|
| Claude + Obsidian | [YouTube](https://youtube.com/watch?v=sCIS05Qt79Y) |
| Building MCP Servers | [modelcontextprotocol.io/quickstart](https://modelcontextprotocol.io/quickstart) |
| Gmail API Setup | [developers.google.com](https://developers.google.com/gmail/api/quickstart) |
| Playwright Automation | [playwright.dev](https://playwright.dev/python/docs/intro) |

---

## Research Meetings

**When:** Every Wednesday at 10:00 PM

**Zoom:** [https://us06web.zoom.us/j/87188707642?pwd=a9XloCsinvn1JzICbPc2YGUvWTbOTr.1](https://us06web.zoom.us/j/87188707642?pwd=a9XloCsinvn1JzICbPc2YGUvWTbOTr.1)
- Meeting ID: 871 8870 7642
- Passcode: 744832

**YouTube (if full):** [https://www.youtube.com/@panaversity](https://www.youtube.com/@panaversity)

---

## Judging Criteria

| Criterion | Weight | Description |
|-----------|--------|-------------|
| **Functionality** | 30% | Does it work? Are core features complete? |
| **Innovation** | 25% | Creative solutions, novel integrations |
| **Practicality** | 20% | Would you actually use this daily? |
| **Security** | 15% | Proper credential handling, HITL safeguards |
| **Documentation** | 10% | Clear README, setup instructions, demo |

---

## Next Steps

### For Cloud FTE
See [Advanced Custom Cloud FTE Architecture](https://docs.google.com/document/d/15GuwZwIOQy_g1XsIJjQsFNHCTQTWoXQhWGVMhiH0swc/edit)

### For Odoo Integration
See [Odoo JSON-RPC API Reference](https://www.odoo.com/documentation/19.0/developer/reference/external_api.html)

### For Cloud Deployment (Platinum Tier)
[Oracle Cloud Free VMs](https://www.oracle.com/cloud/free/) - Deploy your AI Employee 24/7

---

## Project Status Summary

| Tier | Status | Time | Completion |
|------|--------|------|------------|
| **Bronze** | ✅ Complete | 8-12 hrs | 100% |
| **Silver** | ✅ Complete | 20-30 hrs | 100% |
| **Gold** | ✅ Complete | 40+ hrs | 100% |
| **Platinum (Local)** | ✅ Complete | 10-15 hrs | 85% |
| **Platinum (Cloud)** | ⏸️ Pending | 8-10 hrs | 0% (needs VM) |

**Overall Project:** 🎉 **READY FOR SUBMISSION**

---

**Last Updated:** March 25, 2026  
**Hackathon:** Personal AI Employee Hackathon 0
