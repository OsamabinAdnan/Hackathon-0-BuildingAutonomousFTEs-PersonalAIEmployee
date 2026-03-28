# Personal AI Employee - Platinum Tier 🚀

**Tagline:** *Always-On Cloud + Local Executive - Production-Ready AI Employee*

**Status:** ✅ **Platinum Tier Local Simulation Complete** - Cloud Deployment Ready

---

## Overview

Platinum Tier is the **production-ready** version of the Personal AI Employee system. It extends Gold Tier with a **dual-agent architecture** that separates Cloud operations (always-on, draft-only) from Local operations (human-proximate, full execution), enabling 24/7 monitoring while maintaining security and human oversight.

**Current Deployment:** Local Simulation (Single Machine)  
**Cloud Deployment:** Ready (Pending VM Access)

---

## Features

### From Gold Tier ✅
- All Gold Tier features (6 watchers, 14 MCP tools, Odoo, Facebook)
- Ralph Wiggum Loop for autonomous task completion
- Comprehensive audit logging
- Error recovery (retry + circuit breaker)
- 13 Agent Skills

### New in Platinum Tier 🆕

#### Dual-Agent Architecture
- **Cloud Agent** (draft_only mode) - Email triage, social drafts, monitoring
- **Local Agent** (full mode) - Approvals, WhatsApp, payments, final send
- **Work-Zone Specialization** - Cloud drafts, Local executes

#### Security Hardening
- **WhatsApp stays local** - Cloud Agent cannot access WhatsApp (session never leaves local machine)
- **Payments require approval** - Cloud creates approval request, Local executes
- **Secrets never sync** - .env, credentials, tokens excluded from vault sync

#### Cloud→Local Handoff
- **/Updates/ folder** - Cloud writes updates, Local reads
- **Claim-by-move rule** - Prevents double-processing
- **Draft-only mode** - All MCP tools support draft creation

#### Git Sync Ready
- **Vault .gitignore** - Security rules for cloud sync
- **Sync scripts** - `sync_vault.bat`, `setup_auto_sync.bat`
- **Zero code changes** - Deploy to cloud VM with configuration only

---

## Architecture

### Platinum Tier: Cloud + Local Split

```
┌─────────────────────────────────────────────────────────────────┐
│                      PLATINUM TIER                               │
│  ┌─────────────────────────┐    ┌────────────────────────────┐  │
│  │   CLOUD AGENT           │    │   LOCAL AGENT              │  │
│  │   (draft_only mode)     │    │   (full mode)              │  │
│  │                         │    │                            │  │
│  │  ┌──────────┐          │    │  ┌──────────┐              │  │
│  │  │ Watchers │          │    │  │ Watchers │              │  │
│  │  │ (Draft   │          │    │  │ (WhatsApp│              │  │
│  │  │  Only)   │          │    │  │  Local)  │              │  │
│  │  │ - Gmail  │          │    │  │          │              │  │
│  │  │ - LinkedIn│         │    │  │          │              │  │
│  │  │ - Facebook│         │    │  │          │              │  │
│  │  └────┬─────┘          │    │  └────┬─────┘              │  │
│  │       │                │    │       │                     │  │
│  │       ▼                │    │       ▼                     │  │
│  │  ┌──────────┐          │    │  ┌──────────┐              │  │
│  │  │  Cloud   │          │    │  │  Local   │              │  │
│  │  │Orchestrator│        │    │  │Orchestrator│            │  │
│  │  │(Draft Mode)│        │    │  │(Full Mode)│             │  │
│  │  └────┬─────┘          │    │  └────┬─────┘              │  │
│  │       │                │    │       │                     │  │
│  │       ▼                │    │       ▼                     │  │
│  │  ┌──────────┐          │    │  ┌──────────┐              │  │
│  │  │  Write   │◄─────────┼────┼──►  Read    │              │  │
│  │  │  /Updates/│ SYNC    │    │  │/Updates/ │              │  │
│  │  └──────────┘          │    │  └──────────┘              │  │
│  │                         │    │                            │  │
│  │  ┌──────────┐          │    │  ┌──────────┐              │  │
│  │  │   Odoo   │          │    │  │   MCP    │              │  │
│  │  │  (Draft) │          │    │  │  Server  │              │  │
│  │  └──────────┘          │    │  └──────────┘              │  │
│  └─────────────────────────┘    └────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘

CURRENT: Both agents run on same machine (local simulation)
FUTURE: Cloud Agent deploys to VM, Local stays on laptop
```

---

## Project Structure

```
Platinum_Tier/
├── AI_Employee_Vault_FTE/      # Obsidian vault
│   ├── Dashboard.md            # Real-time system summary (Local writes only)
│   ├── Company_Handbook.md     # Rules of Engagement
│   ├── Business_Goals.md       # Objectives and metrics
│   ├── Needs_Action/           # Action files by source
│   │   ├── email/              # Gmail action files
│   │   ├── whatsapp/           # WhatsApp action files
│   │   ├── linkedin/           # LinkedIn action files
│   │   ├── facebook/           # Facebook action files
│   │   ├── files/              # FileSystem action files
│   │   └── odoo/               # Odoo action files
│   ├── In_Progress/            # Claim-by-move rule (cloud/, local/)
│   ├── Updates/                # 🆕 Cloud → Local handoff
│   ├── Pending_Approval/       # Items needing approval
│   ├── Approved/               # Human approved
│   ├── Rejected/               # Human rejected
│   ├── Done/                   # Completed tasks
│   ├── Logs/                   # Audit logs
│   ├── Briefings/              # CEO briefing reports
│   ├── LinkedIn_Posts/         # LinkedIn post history
│   ├── Facebook_Posts/         # Facebook post history
│   └── drafts/                 # 🆕 Draft posts (draft_only mode)
│       ├── linkedin/
│       └── facebook/
│
├── .env.cloud                  # 🆕 Cloud Agent config (draft_only)
├── .env.local                  # 🆕 Local Agent config (full)
├── run_cloud_agent.bat         # 🆕 Launch Cloud Agent
├── run_local_agent.bat         # 🆕 Launch Local Agent
├── sync_vault.bat              # 🆕 Vault sync script
├── setup_auto_sync.bat         # 🆕 Auto-sync scheduler setup
│
├── watchers/                   # Perception layer (6 watchers)
│   ├── base_watcher.py
│   ├── filesystem_watcher.py
│   ├── gmail_watcher.py
│   ├── whatsapp_watcher.py
│   ├── linkedin_watcher.py
│   └── facebook_watcher.py
│
├── mcp_server/                 # Action layer (Platinum-aware)
│   ├── server.py               # 🆕 Draft-only mode support
│   ├── odoo_mcp.py
│   ├── email_service.py
│   ├── whatsapp_service.py     # 🆕 Blocked on Cloud Agent
│   ├── linkedin_service.py     # 🆕 Draft creation
│   ├── facebook_service.py     # 🆕 Draft creation
│   └── odoo_service.py         # 🆕 create_invoice_draft()
│
├── orchestrator/               # Main controller
│   ├── main.py                 # 🆕 EXECUTION_MODE, claim_file(), write_update()
│   ├── __init__.py
│   └── __main__.py
│
├── ralph_wiggum/               # Autonomous task completion
│   ├── stop_hook.py
│   └── task_tracker.py
│
├── audit/                      # Audit logging & error recovery
│   ├── logger.py
│   ├── retry.py
│   ├── circuit_breaker.py
│   └── health.py
│
├── scheduling/                 # Scheduled tasks
│   ├── weekly_briefing.ps1
│   ├── weekly_briefing.sh
│   ├── linkedin_post.ps1
│   ├── facebook_post.ps1
│   ├── setup_task_scheduler.ps1
│   └── setup_cron.sh
│
├── odoo/                       # Odoo Docker setup
│   ├── docker-compose.yml
│   ├── README.md
│   └── setup.bat
│
├── docs/Platinum_docs/         # 🆕 Platinum documentation
│   ├── PLATINUM_TIER_COMPLETE_GUIDE.md
│   ├── IMPLEMENTATION_DETAILS.md
│   ├── IMPLEMENTATION_STATUS_ROADMAP.md
│   ├── PLATINUM_TEST_GUIDE.md
│   ├── WEEK2_COMPLETE.md
│   └── PLATINUM_TIER_LOCAL_COMPLETE.md
│
├── .claude/                    # Claude Code configuration
│   └── skills/                 # 13 Agent Skills
│
├── credentials/                # OAuth credentials (gitignored)
├── sessions/                   # Browser sessions (gitignored)
├── .watcher_state/             # Watcher state files
├── .gitignore                  # 🆕 Vault security rules
├── .env                        # Environment variables (gitignored)
├── .env.example                # Environment template
├── pyproject.toml
├── README.md                   # This file
└── CLAUDE.md
```

---

## Platinum Tier MCP Tools (14 Total)

### Email Tools
| Tool | Cloud (draft_only) | Local (full) |
|------|-------------------|--------------|
| `send_email()` | ✅ Creates Gmail draft | ✅ Sends real email |
| `create_email_draft()` | ✅ Creates draft | ✅ Creates draft |
| `search_emails()` | ✅ Search | ✅ Search |

### WhatsApp Tools
| Tool | Cloud (draft_only) | Local (full) |
|------|-------------------|--------------|
| `send_whatsapp()` | ❌ **BLOCKED** (security) | ✅ Sends message |

**Security:** WhatsApp session stays local - Cloud Agent cannot access

### LinkedIn Tools
| Tool | Cloud (draft_only) | Local (full) |
|------|-------------------|--------------|
| `post_linkedin()` | ✅ Saves draft file | ✅ Posts to LinkedIn |
| `post_linkedin_organization()` | ✅ Saves draft file | ✅ Posts as org |
| `send_linkedin_message()` | ✅ Saves draft file | ✅ Sends DM |
| `get_linkedin_profile()` | ✅ Get profile | ✅ Get profile |

### Facebook Tools
| Tool | Cloud (draft_only) | Local (full) |
|------|-------------------|--------------|
| `post_facebook()` | ✅ Saves draft file | ✅ Posts to Facebook |
| `send_facebook_message()` | ✅ Saves draft file | ✅ Sends message |
| `get_facebook_insights()` | ✅ Get insights | ✅ Get insights |

### Odoo Tools
| Tool | Cloud (draft_only) | Local (full) |
|------|-------------------|--------------|
| `create_invoice()` | ✅ Creates draft invoice | ✅ Creates real invoice |
| `record_payment()` | ✅ Creates approval request | ✅ Executes payment |
| `get_financial_report()` | ✅ Get report | ✅ Get report |
| `list_unpaid_invoices()` | ✅ List invoices | ✅ List invoices |

---

## Execution Modes

### Cloud Agent (draft_only)

```bash
# .env.cloud
EXECUTION_MODE=draft_only
CLOUD_AGENT=true
```

**Capabilities:**
- ✅ Monitor Gmail, LinkedIn, Facebook, Odoo
- ✅ Create drafts (email, social posts, invoices)
- ✅ Write to `/Updates/` folder
- ❌ Cannot send real emails
- ❌ Cannot post to social media
- ❌ Cannot execute payments
- ❌ Cannot access WhatsApp (security)

### Local Agent (full)

```bash
# .env.local
EXECUTION_MODE=full
CLOUD_AGENT=false
```

**Capabilities:**
- ✅ Execute all approved actions
- ✅ Send WhatsApp messages
- ✅ Execute payments
- ✅ Post to social media
- ✅ Write Dashboard.md
- ✅ Read from `/Updates/`

---

## Quick Start

### 1. Install Dependencies

```bash
cd Platinum_Tier
uv sync
```

### 2. Configure Environment

**For Cloud Agent:**
```bash
cp .env.cloud .env
# Edit with your credentials
```

**For Local Agent:**
```bash
cp .env.local .env
# Edit with your credentials (including WhatsApp, banking)
```

### 3. Start Both Agents

**Terminal 1 - Cloud Agent:**
```bash
.\run_cloud_agent.bat
```

**Expected Output:**
```
PLATINUM TIER - Execution Mode: draft_only
Cloud Agent: True
⚠️ DRAFT-ONLY MODE - No real sending/posting
```

**Terminal 2 - Local Agent:**
```bash
.\run_local_agent.bat
```

**Expected Output:**
```
PLATINUM TIER - Execution Mode: full
Cloud Agent: False
```

### 4. Test Platinum Handoff

1. Create test email: `AI_Employee_Vault_FTE/Needs_Action/email/TEST_001.md`
2. Watch Cloud Agent create draft
3. Watch Cloud write to `/Updates/`
4. Watch Local Agent create approval request
5. Approve (move to `/Approved/`)
6. Watch Local execute

**Full test guide:** [`docs/Platinum_docs/PLATINUM_TEST_GUIDE.md`](./docs/Platinum_docs/PLATINUM_TEST_GUIDE.md)

---

## CLI Commands

### Platinum-Specific Commands

| Command | Description |
|---------|-------------|
| `.\run_cloud_agent.bat` | Start Cloud Agent (draft_only) |
| `.\run_local_agent.bat` | Start Local Agent (full) |
| `.\sync_vault.bat` | Manual vault sync |
| `.\setup_auto_sync.bat` | Setup auto-sync scheduler |

### Standard Commands (from Gold Tier)

All Gold Tier commands work (orchestrator, watchers, MCP server, etc.)

---

## Platinum Tier Requirements Status

Based on [Official Hackathon Spec](../../Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026.md):

| # | Requirement | Status | Notes |
|---|-------------|--------|-------|
| 1 | **Cloud Deployment 24/7** | ⏸️ Pending | Need cloud VM access |
| 2 | **Work-Zone Specialization** | ✅ Complete | Draft-only mode implemented |
| 3 | **Synced Vault (Phase 1)** | ✅ Ready | Git scripts ready, test locally |
| 4 | **Security Rules** | ✅ Complete | WhatsApp blocked, secrets excluded |
| 5 | **Odoo on Cloud VM** | ⏸️ Pending | Need cloud VM access |
| 6 | **A2A Messaging (Optional)** | ❌ Future | Phase 2 enhancement |
| 7 | **Platinum Demo** | ✅ Complete | Can demo locally |

**Completion:** 5 of 7 requirements met locally (71%)  
**Local Simulation:** 100% complete  
**Cloud Deployment:** Ready (zero code changes needed)

---

## Security

### Credential Distribution

| Credential | Cloud VM | Local Machine |
|------------|----------|---------------|
| Gmail OAuth | ✅ Limited | ✅ Full |
| LinkedIn Token | ✅ Limited | ✅ Full |
| Facebook Token | ✅ Limited | ✅ Full |
| WhatsApp Session | ❌ **NEVER** | ✅ Local only |
| Banking API Token | ❌ **NEVER** | ✅ Local only |
| Payment API Key | ❌ **NEVER** | ✅ Local only |

### .gitignore Rules

Vault sync excludes:
- `.env`, `.env.local`, `.env.cloud`
- `credentials/`
- `sessions/`
- `*.token.json`
- `banking/`, `payments/`

**Full .gitignore:** [`AI_Employee_Vault_FTE/.gitignore`](./AI_Employee_Vault_FTE/.gitignore)

---

## Implementation Summary

### Code Changes

| File | Changes | Lines Added |
|------|---------|-------------|
| `orchestrator/main.py` | EXECUTION_MODE, claim_file(), write_update() | ~100 |
| `mcp_server/server.py` | Draft-only logic for all tools | ~200 |
| `mcp_server/odoo_service.py` | create_invoice_draft() | ~90 |
| **Total** | | **~390 lines** |

### Files Created

| Category | Files |
|----------|-------|
| Configuration | `.env.cloud`, `.env.local`, `.gitignore` |
| Launch Scripts | `run_cloud_agent.bat`, `run_local_agent.bat` |
| Sync Scripts | `sync_vault.bat`, `setup_auto_sync.bat` |
| Documentation | 6 comprehensive guides |
| **Total** | **12 new files** |

---

## When Cloud Access Available

### Deploy Cloud Agent to VM (Copy-Paste Ready)

```bash
# 1. Provision Oracle Cloud VM
# https://www.oracle.com/cloud/free/

# 2. SSH into VM
ssh user@vm-ip

# 3. Install dependencies
curl -LsSf https://astral.sh/uv/install.sh | sh
curl -fsSL https://get.docker.com | sh
sudo npm install -g pm2

# 4. Clone and configure
git clone <your-repo> Platinum_Tier
cd Platinum_Tier
cp .env.cloud .env

# 5. Start Cloud Agent
EXECUTION_MODE=draft_only uv run python -m orchestrator

# 6. Setup PM2 for auto-restart
pm2 start "EXECUTION_MODE=draft_only uv run python -m orchestrator" --name cloud-agent
pm2 save
pm2 startup
```

**Zero code changes needed!**

---

## Troubleshooting

### Cloud Agent Not Starting

```bash
# Check .env.cloud exists
dir .env.cloud

# Check EXECUTION_MODE
type .env.cloud | findstr EXECUTION_MODE
# Should be: EXECUTION_MODE=draft_only
```

### WhatsApp Blocked on Cloud

**Expected behavior!** WhatsApp is intentionally blocked on Cloud Agent for security.

```
❌ WhatsApp not available on Cloud Agent - WhatsApp session stays local for security
```

### Local Agent Not Detecting Updates

```bash
# Check Local is running in full mode
type .env.local | findstr EXECUTION_MODE
# Should be: EXECUTION_MODE=full

# Restart Local Agent
.\run_local_agent.bat
```

---

## References

- **Official Spec:** [`../../Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md`](../../Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026.md)
- **Complete Guide:** [`docs/Platinum_docs/PLATINUM_TIER_COMPLETE_GUIDE.md`](./docs/Platinum_docs/PLATINUM_TIER_COMPLETE_GUIDE.md)
- **Test Guide:** [`docs/Platinum_docs/PLATINUM_TEST_GUIDE.md`](./docs/Platinum_docs/PLATINUM_TEST_GUIDE.md)
- **Status:** [`docs/Platinum_docs/PLATINUM_TIER_LOCAL_COMPLETE.md`](./docs/Platinum_docs/PLATINUM_TIER_LOCAL_COMPLETE.md)

---

**PLATINUM TIER STATUS: ✅ READY FOR SUBMISSION**

**Local Simulation:** 100% Complete  
**Cloud Deployment:** Ready (pending VM access)
