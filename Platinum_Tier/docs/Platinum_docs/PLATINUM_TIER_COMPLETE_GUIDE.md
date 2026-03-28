# Platinum Tier: Complete Guide (Cloud-Ready)

**Version:** 1.0  
**Last Updated:** March 25, 2026  
**Status:** 🚧 **Cloud-Ready (Local Development Mode)** - Full implementation pending cloud access

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Platinum Tier Requirements](#platinum-tier-requirements)
3. [Architecture Overview](#architecture-overview)
4. [Current Implementation Status](#current-implementation-status)
5. [Local Simulation (No Cloud Required)](#local-simulation-no-cloud-required)
6. [Cloud Deployment Guide (Future)](#cloud-deployment-guide-future)
7. [Testing & Verification](#testing--verification)

---

## Executive Summary

Platinum Tier represents the **production-ready** version of the Personal AI Employee system. It extends Gold Tier with a **dual-agent architecture** that separates Cloud operations (always-on) from Local operations (human-proximate), enabling 24/7 monitoring while maintaining security and human oversight.

### Key Innovation: Work-Zone Specialization

| Zone | Responsibilities | Execution Mode |
|------|------------------|----------------|
| **Cloud** | Email triage, social drafts, monitoring | **Draft-only** (no sending) |
| **Local** | Approvals, WhatsApp, payments, final send | **Full execution** |

### Why Platinum Tier?

| Benefit | Description |
|---------|-------------|
| **24/7 Coverage** | Cloud agents never sleep, monitor while you sleep |
| **Security** | Sensitive credentials (WhatsApp, banking) stay local |
| **Human Oversight** | Critical actions require local approval |
| **Scalability** | Cloud handles volume, Local handles judgment |
| **Privacy** | Secrets never sync to cloud |

---

## Platinum Tier Requirements

Based on the official hackathon specification, Platinum Tier must deliver:

### ✅ 1. Cloud Deployment (24/7 Always-On)

**Requirement:** Run the AI Employee on Cloud 24/7 with health monitoring.

**Sub-Tasks:**
- [ ] Deploy watchers + orchestrator on cloud VM (Oracle/AWS/GCP)
- [ ] Setup health monitoring with auto-restart
- [ ] Configure remote logging aggregation
- [ ] **Current Status:** Infrastructure ready, deployment pending cloud access

**Cloud Provider Options:**

| Provider | Free Tier | Suitable For |
|----------|-----------|--------------|
| **Oracle Cloud** | Always-free VM (4 ARM cores, 24GB RAM) | Full Platinum deployment |
| **AWS Free Tier** | 12 months t2.micro | Limited but workable |
| **Google Cloud** | $300 credit for 90 days | Trial deployment |

---

### ✅ 2. Work-Zone Specialization

**Requirement:** Split responsibilities between Cloud and Local.

**Cloud Owns:**
- Email triage + draft replies (draft-only)
- Social post drafts/scheduling (draft-only)
- Monitoring (Gmail, LinkedIn, Facebook, Odoo)

**Local Owns:**
- Approvals (HITL workflow)
- WhatsApp session (stays local)
- Payments/banking (final send actions)
- Final "send/post" actions

**Current Status:** Architecture designed, draft-only mode implementable locally

---

### ✅ 3. Delegation via Synced Vault (Phase 1)

**Requirement:** Agents communicate by writing files with sync.

**Folder Structure:**
```
shared_vault/
├── Needs_Action/<domain>/      # Email, WhatsApp, LinkedIn, etc.
├── Plans/<domain>/             # Claude's action plans
├── Pending_Approval/<domain>/  # Awaiting human approval
├── Updates/                    # Cloud → Local handoff
├── In_Progress/<agent>/        # Claim-by-move rule
├── Approved/<domain>/          # Human approved
├── Done/<domain>/              # Completed tasks
└── Logs/audit/                 # Audit trail
```

**Sync Rules:**
- **Claim-by-move:** First agent to move file to `/In_Progress/<agent>/` owns it
- **Single-writer:** Only Local writes `Dashboard.md`
- **Sync method:** Git or Syncthing
- **Sync interval:** Every 5 minutes

**Current Status:** Can simulate locally with Git

---

### ✅ 4. Security Rules

**Requirement:** Secrets never sync to cloud.

**Excluded from Sync:**
- `.env` files
- OAuth tokens (`*.token.json`)
- WhatsApp sessions (`sessions/*`)
- Banking credentials
- Payment API keys

**Current Status:** Can implement locally via `.gitignore`

---

### ✅ 5. Odoo on Cloud VM

**Requirement:** Deploy Odoo Community on cloud VM with HTTPS, backups, health monitoring.

**Sub-Tasks:**
- [ ] Cloud VM Odoo deployment (Docker Compose)
- [ ] HTTPS/SSL certificate setup (Let's Encrypt)
- [ ] Automated backups configuration
- [ ] Odoo health monitoring
- [ ] Cloud Agent: Draft-only accounting actions via MCP
- [ ] Local: Approval for invoice/payment posting

**Current Status:** Can simulate locally with Docker

---

### ✅ 6. A2A Messaging Upgrade (Phase 2 - Optional)

**Requirement:** Replace file handoffs with direct agent-to-agent messages.

**Sub-Tasks:**
- [ ] A2A messaging protocol design
- [ ] Direct message queue implementation
- [ ] Keep vault as audit record
- [ ] Hybrid file/A2A architecture

**Current Status:** Future enhancement

---

### ✅ 7. Platinum Demo (Minimum Passing Gate)

**Requirement:** End-to-end demo of Cloud/Local split.

**Demo Scenario:**
```
1. Email arrives while Local is offline
2. Cloud drafts reply + writes approval file
3. Local returns, user approves
4. Local executes send via MCP
5. Logs action
6. Moves task to /Done
```

**Current Status:** Can demo locally with offline simulation

---

## Architecture Overview

### Gold Tier (Current) vs Platinum Tier (Target)

```
┌─────────────────────────────────────────────────────────────────┐
│                        GOLD TIER                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    LOCAL MACHINE                          │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐                │   │
│  │  │ Watchers │→ │Orchestrator│→ │  Claude  │                │   │
│  │  │ (6 total)│  │          │  │  Code    │                │   │
│  │  └──────────┘  └──────────┘  └──────────┘                │   │
│  │                          │                                │   │
│  │                          ▼                                │   │
│  │                   ┌──────────┐                           │   │
│  │                   │   MCP    │                           │   │
│  │                   │  Server  │                           │   │
│  │                   └──────────┘                           │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      PLATINUM TIER                               │
│  ┌─────────────────────────┐    ┌────────────────────────────┐  │
│  │      CLOUD VM           │    │      LOCAL MACHINE         │  │
│  │  (Always-On, 24/7)      │    │  (Human-Proximate)         │  │
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
```

### Execution Modes

| Mode | Agent Type | Capabilities | Restrictions |
|------|-----------|--------------|--------------|
| **draft_only** | Cloud Agent | Create drafts, monitor, write /Updates/ | Cannot send/post/pay |
| **full** | Local Agent | Execute approved actions, WhatsApp, payments | Must approve Cloud drafts |

---

## Current Implementation Status

### ✅ Completed (Gold Tier Foundation)

| Component | Status | Notes |
|-----------|--------|-------|
| 6 Watchers (Gmail, WhatsApp, LinkedIn, Facebook, FileSystem, Odoo) | ✅ Complete | Can run in draft-only mode |
| MCP Server (14 tools) | ✅ Complete | Supports draft-only execution |
| Odoo Integration (Docker) | ✅ Complete | Can simulate cloud deployment locally |
| Ralph Wiggum Loop | ✅ Complete | Autonomous task completion |
| Audit Logging | ✅ Complete | JSON logging for all actions |
| Error Recovery | ✅ Complete | Retry + Circuit Breaker |
| Agent Skills (13) | ✅ Complete | All workflow and action skills |

### 🚧 In Progress (Platinum-Specific)

| Component | Status | Notes |
|-----------|--------|-------|
| Dual-Agent Architecture | 📋 Designed | Cloud/Local mode separation |
| Draft-Only Execution Mode | 🚧 Ready to Implement | Configuration flag |
| Handoff Folder Structure | 📋 Designed | `/Updates/`, `/Signals/` |
| Claim-by-Move Rule | 📋 Designed | `/In_Progress/<agent>/` |
| Git Sync Simulation | 🚧 Ready to Implement | Local vault sync |
| Security Filters | 🚧 Ready to Implement | .env exclusion |
| Cloud Deployment Scripts | 📋 Prepared | Docker, PM2 configs ready |

### ❌ Pending (Requires Cloud Access)

| Component | Status | Notes |
|-----------|--------|-------|
| Cloud VM Deployment | ❌ Pending Cloud Access | Oracle/AWS/GCP |
| HTTPS/SSL for Odoo | ❌ Pending Cloud Access | Let's Encrypt |
| Cloud Health Monitoring | ❌ Pending Cloud Access | Remote monitoring |
| Automated Cloud Backups | ❌ Pending Cloud Access | S3/backblaze |
| A2A Messaging | ❌ Future Enhancement | Phase 2 |

---

## Local Simulation (No Cloud Required)

You can implement **90% of Platinum Tier locally** by simulating the Cloud/Local split on a single machine.

### Implementation Roadmap

| Phase | Task | Estimated Time |
|-------|------|----------------|
| **Phase 1** | Dual-agent architecture (Cloud/Local modes) | 4-6 hours |
| **Phase 2** | Draft-only execution mode | 2-3 hours |
| **Phase 3** | Handoff folder structure (`/Updates/`) | 1-2 hours |
| **Phase 4** | Claim-by-move rule implementation | 1-2 hours |
| **Phase 5** | Git-based sync simulation | 2-3 hours |
| **Phase 6** | Security filters (.env exclusion) | 1 hour |
| **Phase 7** | Platinum demo (offline scenario) | 3-4 hours |
| **Phase 8** | Cloud deployment prep (Docker, scripts) | 4-6 hours |
| **TOTAL** | **Platinum-ready without cloud** | **18-27 hours** |

### Local Simulation Architecture

```
Single Machine Simulation:
┌─────────────────────────────────────────────────────────────┐
│                     YOUR LAPTOP                              │
│                                                              │
│  ┌─────────────────────┐      ┌─────────────────────┐       │
│  │   "Cloud Agent"     │      │   "Local Agent"     │       │
│  │   (Draft-Only Mode) │      │  (Full Execution)   │       │
│  │                     │      │                     │       │
│  │  - Email drafts     │      │  - Approvals        │       │
│  │  - Social drafts    │      │  - WhatsApp send    │       │
│  │  - Monitoring       │      │  - Payment send     │       │
│  │  - /Updates/ write  │      │  - /Updates/ read   │       │
│  │                     │      │                     │       │
│  │  EXECUTION_MODE:    │      │  EXECUTION_MODE:    │       │
│  │  draft_only         │      │  full               │       │
│  └─────────────────────┘      └─────────────────────┘       │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │              SHARED VAULT (Git Sync Simulated)         │  │
│  │  /Needs_Action/  /Updates/  /In_Progress/  /Approved/  │  │
│  └────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Step-by-Step Local Setup

#### Step 1: Create Test Directories

```bash
cd Platinum_Tier

# Create separate directories for Cloud/Local simulation
mkdir -p cloud_agent_env
mkdir -p local_agent_env

# Copy environment files
cp .env.cloud cloud_agent_env/.env
cp .env.local local_agent_env/.env
```

#### Step 2: Create Shared Vault

```bash
mkdir -p shared_vault/Needs_Action/{email,whatsapp,linkedin,facebook,odoo,files}
mkdir -p shared_vault/Updates
mkdir -p shared_vault/In_Progress/{cloud,local}
mkdir -p shared_vault/Pending_Approval
mkdir -p shared_vault/Approved
mkdir -p shared_vault/Done
mkdir -p shared_vault/Logs/audit
mkdir -p shared_vault/Plans

# Create initial Dashboard.md
cat > shared_vault/Dashboard.md << 'EOF'
# AI Employee Dashboard

**Last Updated:** {{ timestamp }}

**Mode:** Platinum Tier (Cloud + Local Simulation)

## Status
- Cloud Agent: Running (draft_only)
- Local Agent: Running (full)

## Metrics
| Category | Count |
|----------|-------|
| Needs Action | 0 |
| In Progress | 0 |
| Pending Approval | 0 |
| Done Today | 0 |
EOF
```

#### Step 3: Run Cloud Agent (Terminal 1)

```bash
# Terminal 1 - Cloud Agent
cd Platinum_Tier/cloud_agent_env
EXECUTION_MODE=draft_only uv run python -m orchestrator
```

#### Step 4: Run Local Agent (Terminal 2)

```bash
# Terminal 2 - Local Agent
cd Platinum_Tier/local_agent_env
EXECUTION_MODE=full uv run python -m orchestrator
```

#### Step 5: Test Handoff

```bash
# Terminal 3 - Create test email
cat > shared_vault/Needs_Action/email/TEST_001.md << 'EOF'
---
type: email
from: test@example.com
subject: Test Email for Platinum Handoff
received: 2026-03-25T10:00:00Z
priority: high
status: pending
---

## Email Content
This is a test email to verify Cloud → Local handoff.

## Suggested Actions
- [ ] Draft reply
- [ ] Move to /Done after processing
EOF
```

**Expected Flow:**
1. Cloud Agent detects test email
2. Cloud Agent processes (draft mode)
3. Cloud writes to `shared_vault/Updates/email_draft.json`
4. Local Agent detects update
5. Local Agent creates approval request
6. User approves (moves to `/Approved/`)
7. Local Agent executes (full mode)
8. Local Agent moves to `/Done/`

---

## Cloud Deployment Guide (Future)

When you get cloud access, here's how to deploy the Cloud Agent.

### Step 1: Provision Cloud VM

**Oracle Cloud Free VM (Recommended):**
1. Sign up: https://www.oracle.com/cloud/free/
2. Create VM instance:
   - Shape: VM.Standard.A1.Flex (4 OCPUs, 24GB RAM - always free)
   - Image: Ubuntu 22.04
   - Boot volume: 200GB
3. Note public IP address

### Step 2: SSH into VM

```bash
ssh -i <your-key> ubuntu@<cloud-vm-ip>
```

### Step 3: Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.13
sudo apt install -y python3.13 python3.13-venv python3-pip

# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env

# Install Node.js (for MCP)
curl -fsSL https://deb.nodesource.com/setup_24.x | sudo -E bash -
sudo apt install -y nodejs

# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker ubuntu

# Install PM2
sudo npm install -g pm2
```

### Step 4: Clone Repository

```bash
git clone <your-repo-url> Platinum_Tier
cd Platinum_Tier
```

### Step 5: Configure Environment

```bash
# Copy and edit cloud configuration
cp .env.cloud .env
nano .env  # Fill in your cloud-specific credentials
```

### Step 6: Setup Odoo (Optional)

```bash
cd odoo
docker-compose up -d

# Wait for Odoo to start
docker-compose logs -f

# Access http://<cloud-vm-ip>:8069
# Login: admin / admin
```

### Step 7: Setup Vault Sync (Git)

```bash
# Configure Git
git config --global user.email "cloud-agent@example.com"
git config --global user.name "Cloud Agent"

# Initialize vault as Git repo
cd AI_Employee_Vault_FTE
git init
git remote add origin git@github.com:<your-username>/ai-employee-vault.git
git pull origin main
```

### Step 8: Start Cloud Agent

```bash
cd /home/ubuntu/Platinum_Tier

# Test run
EXECUTION_MODE=draft_only uv run python -m orchestrator

# If successful, setup PM2 for auto-restart
pm2 start "EXECUTION_MODE=draft_only uv run python -m orchestrator" --name cloud-agent

# Save PM2 configuration
pm2 save

# Setup PM2 startup on boot
pm2 startup
# Copy/paste the generated command
```

### Step 9: Setup HTTPS for Odoo (Optional)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot certonly --standalone -d your-domain.com

# Configure Nginx reverse proxy with SSL
sudo nano /etc/nginx/sites-available/odoo

# Add configuration:
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8069;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Enable site
sudo ln -s /etc/nginx/sites-available/odoo /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 10: Setup Health Monitoring

```bash
# Create health check script
cat > /home/ubuntu/Platinum_Tier/health_check.sh << 'EOF'
#!/bin/bash

# Check orchestrator
if ! pm2 list | grep -q "cloud-agent.*online"; then
    echo "Cloud Agent is down! Restarting..."
    pm2 restart cloud-agent
fi

# Check Odoo
if ! curl -s http://localhost:8069 > /dev/null; then
    echo "Odoo is down!"
fi

# Check disk space
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 90 ]; then
    echo "Disk usage critical: ${DISK_USAGE}%"
fi
EOF

chmod +x /home/ubuntu/Platinum_Tier/health_check.sh

# Add to cron (every 5 minutes)
crontab -e
# Add line:
*/5 * * * * /home/ubuntu/Platinum_Tier/health_check.sh >> /var/log/ai-employee/health.log 2>&1
```

---

## Testing & Verification

### Test Scenario: Email → Draft → Approval → Send

**Prerequisites:**
- Cloud Agent running (draft_only mode)
- Local Agent running (full mode)
- Shared vault configured

**Test Steps:**

```bash
# Step 1: Create test email file
cat > shared_vault/Needs_Action/email/PLATINUM_TEST_001.md << 'EOF'
---
type: email
from: platinum-test@example.com
subject: Platinum Tier Handoff Test
received: 2026-03-25T12:00:00Z
priority: high
status: pending
---

## Email Content
This is a test to verify the Platinum Tier Cloud → Local handoff.

Please reply confirming receipt.

## Suggested Actions
- [ ] Draft reply (Cloud)
- [ ] Approve draft (Human)
- [ ] Send reply (Local)
- [ ] Move to /Done (Local)
EOF

# Step 2: Watch Cloud Agent logs
tail -f cloud_agent_env/logs/orchestrator.log

# Expected: Cloud detects email, creates draft, writes to /Updates/

# Step 3: Check /Updates/ folder
cat shared_vault/Updates/email_draft.json

# Expected content:
# {
#   "type": "email_draft",
#   "original_email": "PLATINUM_TEST_001",
#   "draft_id": "gmail_draft_xxx",
#   "status": "pending_local_approval",
#   "timestamp": "2026-03-25T12:01:00Z"
# }

# Step 4: Watch Local Agent logs
tail -f local_agent_env/logs/orchestrator.log

# Expected: Local detects update, creates approval request

# Step 5: Check /Pending_Approval/
ls shared_vault/Pending_Approval/email/

# Step 6: Approve (simulate human)
mv shared_vault/Pending_Approval/email/PLATINUM_TEST_001_approval.md \
   shared_vault/Approved/email/

# Step 7: Watch Local execute
tail -f local_agent_env/logs/orchestrator.log

# Expected: Local sends email, moves to /Done/

# Step 8: Verify completion
ls shared_vault/Done/email/
cat shared_vault/Logs/audit/$(date +%Y-%m-%d).json
```

### Test Results Checklist

| Step | Expected | Actual | Status |
|------|----------|--------|--------|
| Cloud detects email | Log entry | | ⬜ |
| Cloud creates draft | Gmail draft created | | ⬜ |
| Cloud writes /Updates/ | JSON file created | | ⬜ |
| Local detects update | Log entry | | ⬜ |
| Local creates approval | /Pending_Approval/ file | | ⬜ |
| Human approves | File moved to /Approved/ | | ⬜ |
| Local executes | Email sent | | ⬜ |
| Local logs action | Audit log entry | | ⬜ |
| Local moves to /Done/ | File in /Done/ | | ⬜ |

---

## Summary: Platinum Tier Deliverables

| Deliverable | Local Simulation | Cloud Deployment |
|-------------|------------------|------------------|
| Dual-Agent Architecture | ✅ Implementable | ✅ Deployable |
| Draft-Only Mode | ✅ Implementable | ✅ Deployable |
| Handoff Folders | ✅ Implementable | ✅ Deployable |
| Claim-by-Move Rule | ✅ Implementable | ✅ Deployable |
| Git Sync | ✅ Implementable | ✅ Deployable |
| Security Filters | ✅ Implementable | ✅ Deployable |
| Odoo on VM | ❌ Local Docker only | ✅ Deployable |
| 24/7 Operations | ❌ Machine must be on | ✅ Deployable |
| Health Monitoring | ✅ Local monitoring | ✅ Remote monitoring |
| Platinum Demo | ✅ Simulated | ✅ Full demo |

---

## References

- **Official Hackathon Spec:** [`../../Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md`](../../Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026.md)
- **Gold Tier README:** [`../README.md`](../README.md)
- **Ralph Wiggum Plugin:** https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum
- **Oracle Cloud Free VM:** https://www.oracle.com/cloud/free/

---

**Document Version:** 1.0  
**Last Updated:** March 25, 2026  
**Status:** Cloud-Ready (Local Development Mode)
