# Platinum Tier: Implementation Details

**Version:** 1.0  
**Last Updated:** March 25, 2026

---

## Table of Contents

1. [Execution Modes](#execution-modes)
2. [Configuration Files](#configuration-files)
3. [Code Changes Required](#code-changes-required)
4. [Vault Sync Implementation](#vault-sync-implementation)
5. [Security Hardening](#security-hardening)
6. [Draft-Only Mode Details](#draft-only-mode-details)
7. [Troubleshooting](#troubleshooting)

---

## Execution Modes

### Mode 1: `draft_only` (Cloud Agent)

```python
# orchestrator/main.py
EXECUTION_MODE = os.getenv("EXECUTION_MODE", "full")
CLOUD_AGENT = os.getenv("CLOUD_AGENT", "false").lower() == "true"

if CLOUD_AGENT:
    assert EXECUTION_MODE == "draft_only", "Cloud Agent must run in draft_only mode"
```

**Characteristics:**
- ✅ Can monitor Gmail, LinkedIn, Facebook, Odoo
- ✅ Can create drafts in all systems
- ✅ Can write to `/Updates/` folder
- ❌ Cannot send real emails
- ❌ Cannot post to social media
- ❌ Cannot execute payments
- ❌ Cannot access WhatsApp (session stays local)

### Mode 2: `full` (Local Agent)

```python
EXECUTION_MODE = os.getenv("EXECUTION_MODE", "full")
CLOUD_AGENT = os.getenv("CLOUD_AGENT", "false").lower() == "true"

if EXECUTION_MODE == "full" and not CLOUD_AGENT:
    # Local Agent behavior:
    # - Execute approved emails
    # - Post approved social media
    # - Execute approved payments
    # - Send WhatsApp messages
    # - Write Dashboard.md
    # - Merge /Updates/ into workflow
    pass
```

**Characteristics:**
- ✅ Can execute all approved actions
- ✅ Can send WhatsApp messages
- ✅ Can execute payments
- ✅ Can post to social media
- ✅ Can write Dashboard.md
- ✅ Can merge Cloud drafts into workflow

---

## Configuration Files

### File Structure

```
Platinum_Tier/
├── .env.cloud              # Cloud Agent configuration
├── .env.local              # Local Agent configuration
├── .env.example.platinum   # Template for both
├── orchestrator/
│   └── main.py             # Reads EXECUTION_MODE
└── mcp_server/
    └── server.py           # Enforces draft_only vs full
```

### `.env.cloud` Template

```bash
# ==========================================
# PLATINUM TIER - CLOUD AGENT CONFIGURATION
# ==========================================
# NEVER commit this file to Git

# ==========================================
# EXECUTION MODE (CRITICAL)
# ==========================================
EXECUTION_MODE=draft_only
CLOUD_AGENT=true
VAULT_PATH=/opt/ai-employee/vault

# ==========================================
# LOGGING
# ==========================================
LOG_LEVEL=INFO
LOG_FILE=/var/log/ai-employee/cloud-agent.log

# ==========================================
# GMAIL API (Cloud - Draft Only)
# ==========================================
GOOGLE_CLIENT_ID=<your-cloud-gmail-client-id>
GOOGLE_CLIENT_SECRET=<your-cloud-gmail-secret>
GMAIL_CREDENTIALS_PATH=/opt/ai-employee/credentials/gmail_credentials.json

# ==========================================
# LINKEDIN API (Cloud - Draft Only)
# ==========================================
LINKEDIN_ACCESS_TOKEN=<your-cloud-linkedin-token>
LINKEDIN_REFRESH_TOKEN=<your-cloud-linkedin-refresh>
LINKEDIN_ORG_ID=<your-linkedin-organization-id>

# ==========================================
# FACEBOOK GRAPH API (Cloud - Draft Only)
# ==========================================
FACEBOOK_APP_ID=<your-facebook-app-id>
FACEBOOK_APP_SECRET=<your-facebook-app-secret>
FACEBOOK_ACCESS_TOKEN=<your-facebook-page-token>
FACEBOOK_PAGE_ID=<your-facebook-page-id>

# ==========================================
# ODOO (Cloud VM - Draft Only)
# ==========================================
ODOO_URL=http://localhost:8069
ODOO_DB=odoo_db
ODOO_USERNAME=admin
ODOO_PASSWORD=<your-odoo-password>

# ==========================================
# VAULT SYNC (Git)
# ==========================================
VAULT_SYNC_ENABLED=true
VAULT_SYNC_GIT_REMOTE=git@github.com:<your-username>/ai-employee-vault.git
VAULT_SYNC_BRANCH=main
VAULT_SYNC_INTERVAL=300

# ==========================================
# SECURITY (CLOUD-SPECIFIC)
# ==========================================
# NOTE: The following are NEVER present on Cloud:
# - WhatsApp session (stays local)
# - Banking tokens (stay local)
# - Payment API keys (stay local)
# ==========================================

# ==========================================
# HEALTH MONITORING
# ==========================================
HEALTH_CHECK_ENABLED=true
HEALTH_CHECK_INTERVAL=60
HEALTH_CHECK_PORT=8080
```

### `.env.local` Template

```bash
# ==========================================
# PLATINUM TIER - LOCAL AGENT CONFIGURATION
# ==========================================
# NEVER commit this file to Git

# ==========================================
# EXECUTION MODE (CRITICAL)
# ==========================================
EXECUTION_MODE=full
CLOUD_AGENT=false
VAULT_PATH=./AI_Employee_Vault_FTE

# ==========================================
# LOGGING
# ==========================================
LOG_LEVEL=INFO
LOG_FILE=./logs/local-agent.log

# ==========================================
# GMAIL API (Local - Full Execution)
# ==========================================
GOOGLE_CLIENT_ID=<your-local-gmail-client-id>
GOOGLE_CLIENT_SECRET=<your-local-gmail-secret>
GMAIL_CREDENTIALS_PATH=./credentials/gmail_credentials.json

# ==========================================
# WHATSAPP WEB (Local ONLY - NEVER SYNCS)
# ==========================================
WHATSAPP_SESSION_PATH=./sessions/whatsapp
WHATSAPP_HEADLESS=false

# ==========================================
# LINKEDIN API (Local - Full Execution)
# ==========================================
LINKEDIN_ACCESS_TOKEN=<your-local-linkedin-token>
LINKEDIN_REFRESH_TOKEN=<your-local-linkedin-refresh>
LINKEDIN_ORG_ID=<your-linkedin-organization-id>

# ==========================================
# FACEBOOK GRAPH API (Local - Full Execution)
# ==========================================
FACEBOOK_APP_ID=<your-facebook-app-id>
FACEBOOK_APP_SECRET=<your-facebook-app-secret>
FACEBOOK_ACCESS_TOKEN=<your-facebook-page-token>
FACEBOOK_PAGE_ID=<your-facebook-page-id>

# ==========================================
# BANKING (LOCAL ONLY - NEVER SYNCS)
# ==========================================
BANK_API_TOKEN=<your-banking-token>
BANK_API_URL=https://api.yourbank.com

# ==========================================
# PAYMENTS (LOCAL ONLY - NEVER SYNCS)
# ==========================================
PAYMENT_API_KEY=<your-payment-api-key>
PAYMENT_GATEWAY_URL=https://payments.example.com

# ==========================================
# ODOO (Local Docker - Full Execution)
# ==========================================
ODOO_URL=http://localhost:8069
ODOO_DB=odoo_db
ODOO_USERNAME=admin
ODOO_PASSWORD=<your-odoo-password>

# ==========================================
# VAULT SYNC (Git)
# ==========================================
VAULT_SYNC_ENABLED=true
VAULT_SYNC_GIT_REMOTE=git@github.com:<your-username>/ai-employee-vault.git
VAULT_SYNC_BRANCH=main
VAULT_SYNC_INTERVAL=300

# ==========================================
# SECURITY (LOCAL-ONLY SECRETS)
# ==========================================
# The following NEVER sync to Cloud:
# - WhatsApp session
# - Banking tokens
# - Payment API keys
# ==========================================
```

---

## Code Changes Required

### 1. Orchestrator Modifications

**File:** `orchestrator/main.py`

```python
import os
import json
from pathlib import Path
from datetime import datetime

class Orchestrator:
    def __init__(self, vault_path: str, check_interval: int = 180):
        self.vault_path = Path(vault_path)
        self.execution_mode = os.getenv("EXECUTION_MODE", "full")
        self.is_cloud_agent = os.getenv("CLOUD_AGENT", "false").lower() == "true"
        
        # Validate configuration
        if self.is_cloud_agent and self.execution_mode != "draft_only":
            raise ValueError("Cloud Agent must run in draft_only mode")
        
        # Setup folders
        self.needs_action = self.vault_path / "Needs_Action"
        self.updates_folder = self.vault_path / "Updates"
        self.in_progress = self.vault_path / "In_Progress"
        self.approved = self.vault_path / "Approved"
        self.done = self.vault_path / "Done"
        
        # Create folders
        self.updates_folder.mkdir(exist_ok=True)
        self.in_progress.mkdir(exist_ok=True)
        
        # Logger setup
        self.logger = self._setup_logger()
        
    def write_update(self, update_type: str, data: dict):
        """Write update to /Updates/ folder (Cloud Agent only)"""
        if self.execution_mode != "draft_only":
            return  # Only Cloud Agent writes updates
        
        update_file = self.updates_folder / f"{update_type}_{int(time.time())}.json"
        update_content = {
            "type": update_type,
            "timestamp": datetime.now().isoformat(),
            "mode": "draft_only",
            **data
        }
        update_file.write_text(json.dumps(update_content, indent=2))
        self.logger.info(f"[CLOUD] Wrote update to {update_file}")
    
    def claim_file(self, filepath: Path, agent_name: str) -> bool:
        """Claim file by moving to /In_Progress/<agent>/"""
        agent_folder = self.in_progress / agent_name
        agent_folder.mkdir(exist_ok=True)
        
        dest = agent_folder / filepath.name
        
        try:
            shutil.move(str(filepath), str(dest))
            self.logger.info(f"[{agent_name.upper()}] Claimed {filepath.name}")
            return True
        except Exception as e:
            self.logger.warning(f"Failed to claim {filepath.name}: {e}")
            return False
```

### 2. MCP Server Modifications

**File:** `mcp_server/server.py`

```python
import os
from pathlib import Path

class MCPServer:
    def __init__(self):
        self.execution_mode = os.getenv("EXECUTION_MODE", "full")
        self.is_cloud_agent = os.getenv("CLOUD_AGENT", "false").lower() == "true"
    
    @mcp.tool()
    async def send_email(self, to: str, subject: str, body: str, 
                         cc: list[str] = None, bcc: list[str] = None, 
                         html: bool = False) -> str:
        """Send email (mode-aware)"""
        if self.execution_mode == "draft_only":
            return await self._create_email_draft(to, subject, body, cc, bcc, html)
        else:
            return await self._send_email_real(to, subject, body, cc, bcc, html)
    
    async def _create_email_draft(self, to: str, subject: str, body: str,
                                   cc: list[str], bcc: list[str], html: bool) -> str:
        """Create Gmail draft instead of sending"""
        try:
            service = build_gmail_service()
            draft = create_draft_message(service, 'me', to, subject, body, cc, bcc, html)
            
            # Write to /Updates/
            write_update("email_draft", {
                "action": "email_draft_created",
                "to": to,
                "subject": subject,
                "draft_id": draft['id'],
                "mode": "draft_only",
                "requires_local_approval": True
            })
            
            return f"Draft created (draft_only mode): {draft['id']}. Requires Local approval to send."
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create draft: {str(e)}")
    
    @mcp.tool()
    async def post_linkedin(self, text: str, visibility: str = "PUBLIC") -> str:
        """Post to LinkedIn (mode-aware)"""
        if self.execution_mode == "draft_only":
            return await self._create_linkedin_draft(text, visibility)
        else:
            return await self._post_linkedin_real(text, visibility)
    
    async def _create_linkedin_draft(self, text: str, visibility: str) -> str:
        """Create LinkedIn draft post"""
        draft_file = Path("drafts/linkedin") / f"post_{int(time.time())}.md"
        draft_file.parent.mkdir(exist_ok=True)
        
        draft_content = f"""---
type: linkedin_draft
visibility: {visibility}
created: {datetime.now().isoformat()}
mode: draft_only
requires_local_approval: true
---

{text}
"""
        draft_file.write_text(draft_content)
        
        write_update("linkedin_draft", {
            "action": "linkedin_draft_created",
            "visibility": visibility,
            "draft_file": str(draft_file),
            "character_count": len(text)
        })
        
        return f"LinkedIn draft created (draft_only mode): {draft_file}. Requires Local approval to post."
    
    @mcp.tool()
    async def create_invoice(self, partner_name: str, amount: float, 
                            description: str, due_date: str) -> str:
        """Create invoice in Odoo (mode-aware)"""
        if self.execution_mode == "draft_only":
            return await self._create_invoice_draft(partner_name, amount, description, due_date)
        else:
            return await self._create_invoice_real(partner_name, amount, description, due_date)
    
    async def _create_invoice_draft(self, partner_name: str, amount: float, 
                                    description: str, due_date: str) -> str:
        """Create Odoo draft invoice"""
        try:
            odoo = OdooService()
            
            # Create as draft in Odoo
            invoice_id = odoo.create_invoice_draft(
                partner_name=partner_name,
                amount=amount,
                description=description,
                due_date=due_date
            )
            
            write_update("invoice_draft", {
                "action": "invoice_draft_created",
                "partner_name": partner_name,
                "amount": amount,
                "due_date": due_date,
                "odoo_draft_id": invoice_id,
                "mode": "draft_only",
                "requires_local_approval": True
            })
            
            return f"Draft invoice created in Odoo (draft_only mode): ID {invoice_id}. Requires Local approval to post."
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create draft invoice: {str(e)}")
```

---

## Vault Sync Implementation

### Git-Based Sync Setup

```bash
# Initialize vault as Git repo
cd AI_Employee_Vault_FTE
git init
git remote add origin git@github.com:<your-username>/ai-employee-vault.git

# Create .gitignore for security
cat > .gitignore << 'EOF'
# NEVER SYNC - Local secrets only
.env
.env.local
.env.cloud
credentials/
sessions/
*.token.json
*.pem
*.key

# OS files
.DS_Store
Thumbs.db

# Python
__pycache__/
*.pyc
.venv/

# IDE
.vscode/
.idea/
EOF

# Initial commit
git add .
git commit -m "Initial vault setup"
git push -u origin main
```

### Sync Script (Optional)

```bash
# sync_vault.sh
#!/bin/bash

VAULT_PATH="${1:-./AI_Employee_Vault_FTE}"
cd "$VAULT_PATH"

# Pull latest changes
git pull origin main

# Add local changes
git add .

# Commit if there are changes
if ! git diff --cached --quiet; then
    git commit -m "Auto-sync: $(date -Iseconds)"
    git push origin main
    echo "Vault synced at $(date)"
else
    echo "No changes to sync"
fi
```

### Cron Job for Sync (Every 5 Minutes)

```bash
crontab -e

# Add line:
*/5 * * * * /path/to/sync_vault.sh /path/to/AI_Employee_Vault_FTE >> /var/log/vault-sync.log 2>&1
```

---

## Security Hardening

### Credential Distribution Matrix

| Credential | Cloud VM | Local Machine | Rationale |
|------------|----------|---------------|-----------|
| Gmail OAuth | ✅ Limited | ✅ Full | Cloud drafts, Local sends |
| LinkedIn Token | ✅ Limited | ✅ Full | Cloud drafts, Local posts |
| Facebook Token | ✅ Limited | ✅ Full | Cloud drafts, Local posts |
| WhatsApp Session | ❌ NEVER | ✅ Local only | Security - never leaves local |
| Banking API Token | ❌ NEVER | ✅ Local only | Security - money stays local |
| Payment API Key | ❌ NEVER | ✅ Local only | Security - payments local |
| Odoo Admin Password | ✅ VM local | ✅ Local only | Both can access Odoo |
| Vault Sync SSH Key | ✅ Limited | ✅ Full | Both need sync access |

### .gitignore Rules

```gitignore
# ==========================================
# PLATINUM TIER - SECURITY EXCLUSIONS
# ==========================================

# Environment files (contain secrets)
.env
.env.local
.env.cloud
.env.example.platinum

# Credentials (OAuth tokens, API keys)
credentials/
*.json
*.token.json
*.pem
*.key
*.crt

# Sessions (WhatsApp, browser)
sessions/
*.session
*.browser

# Banking & Payments
banking/
payments/
*bank*.json
*payment*.json

# Local-only configurations
config.local.*
*.local.json

# OS files
.DS_Store
Thumbs.db
desktop.ini

# Python
__pycache__/
*.pyc
*.pyo
.venv/
uv.lock

# IDE
.vscode/
.idea/
*.swp
*.swo

# Logs (optional - sync if needed for audit)
# Logs/*.log
# Logs/audit/*.json
```

---

## Draft-Only Mode Details

### Mode Comparison Table

| Action | Cloud (draft_only) | Local (full) |
|--------|-------------------|--------------|
| **Email Reply** | Creates Gmail draft | Sends real email |
| **LinkedIn Post** | Creates draft post | Posts to LinkedIn |
| **Facebook Post** | Creates draft post | Posts to Facebook |
| **Invoice Creation** | Creates draft in Odoo | Creates real invoice |
| **Payment Recording** | Creates approval request | Executes payment |
| **WhatsApp Message** | ❌ Not available | Sends real message |
| **Dashboard.md** | Read only | Write |
| **/Updates/** | Writes | Reads |

### Draft File Templates

**Email Draft:**
```json
{
  "type": "email_draft",
  "timestamp": "2026-03-25T12:00:00Z",
  "mode": "draft_only",
  "action": "email_draft_created",
  "to": "client@example.com",
  "subject": "Re: Project Update",
  "draft_id": "gmail_draft_12345",
  "requires_local_approval": true
}
```

**LinkedIn Draft:**
```markdown
---
type: linkedin_draft
visibility: PUBLIC
created: 2026-03-25T12:00:00Z
mode: draft_only
requires_local_approval: true
---

Excited to announce our new AI Employee feature! 🚀

#AI #Automation #Productivity
```

**Invoice Draft:**
```json
{
  "type": "invoice_draft",
  "timestamp": "2026-03-25T12:00:00Z",
  "mode": "draft_only",
  "action": "invoice_draft_created",
  "partner_name": "Client A",
  "amount": 500.00,
  "due_date": "2026-04-25",
  "odoo_draft_id": "draft_123",
  "requires_local_approval": true
}
```

---

## Troubleshooting

### Cloud Agent Issues

**Problem:** Cloud Agent not creating drafts

**Solution:**
```bash
# Check execution mode
echo $EXECUTION_MODE  # Should be: draft_only

# Check logs
tail -f /var/log/ai-employee/cloud-agent.log

# Restart Cloud Agent
pm2 restart cloud-agent
```

### Local Agent Issues

**Problem:** Local Agent not detecting /Updates/

**Solution:**
```bash
# Check vault sync
cd shared_vault
git status
git pull

# Check Local execution mode
echo $EXECUTION_MODE  # Should be: full

# Restart Local Agent
Ctrl+C
uv run python -m orchestrator
```

### Sync Issues

**Problem:** Git sync conflicts

**Solution:**
```bash
cd shared_vault

# Check status
git status

# Resolve conflicts manually
git diff

# Force pull (if Cloud overwrites)
git fetch origin
git reset --hard origin/main

# Or force push (if Local should win)
git push -f origin main
```

### Mode Validation Error

**Problem:** "Cloud Agent must run in draft_only mode"

**Solution:**
```bash
# Check .env file
cat .env.cloud | grep EXECUTION_MODE

# Should be:
# EXECUTION_MODE=draft_only

# Fix if needed:
sed -i 's/EXECUTION_MODE=.*/EXECUTION_MODE=draft_only/' .env.cloud
```

---

## References

- **Complete Guide:** [`PLATINUM_TIER_COMPLETE_GUIDE.md`](./PLATINUM_TIER_COMPLETE_GUIDE.md)
- **Official Hackathon Spec:** [`../../Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md`](../../Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026.md)
- **Gold Tier README:** [`../README.md`](../README.md)
