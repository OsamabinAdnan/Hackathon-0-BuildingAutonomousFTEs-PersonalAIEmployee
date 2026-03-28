# Platinum Tier - Local Testing Guide

**Week 4: Demo Testing (No Git Required)**

---

## Quick Test (5 Minutes)

### Step 1: Start Both Agents

**Terminal 1 - Cloud Agent:**
```bash
cd Platinum_Tier
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
cd Platinum_Tier
.\run_local_agent.bat
```

**Expected Output:**
```
PLATINUM TIER - Execution Mode: full
Cloud Agent: False
```

---

### Step 2: Create Test Email

File: `AI_Employee_Vault_FTE/Needs_Action/email/PLATINUM_TEST_001.md`

```markdown
---
type: email
from: test@example.com
subject: Platinum Test
---

Test email for Platinum handoff.
```

---

### Step 3: Watch the Flow

**What Should Happen:**

1. **Cloud Agent detects email**
   - Log: `Processing item from /Needs_Action/email/`
   
2. **Cloud Agent creates draft** (not sends!)
   - Log: `Creating email draft...`
   - OR calls MCP: `send_email()` → creates draft

3. **Cloud writes to /Updates/**
   - File: `AI_Employee_Vault_FTE/Updates/email_draft_*.json`
   
4. **Local Agent detects update**
   - Log: `Detected update in /Updates/`

5. **Local creates approval request**
   - File: `AI_Employee_Vault_FTE/Pending_Approval/email/PLATINUM_TEST_001_approval.md`

6. **Human approves** (you do this)
   - Move file from `/Pending_Approval/` to `/Approved/`

7. **Local executes** (sends real email)
   - Log: `Executing approved action...`

8. **Local moves to /Done/**
   - File moved to `/Done/email/`

---

## Verification Checklist

| Step | Expected | Check |
|------|----------|-------|
| Cloud starts | `draft_only` mode logged | ⬜ |
| Local starts | `full` mode logged | ⬜ |
| Cloud detects email | Log entry | ⬜ |
| Cloud creates draft | Draft created (not sent) | ⬜ |
| Cloud writes /Updates/ | JSON file appears | ⬜ |
| Local detects update | Log entry | ⬜ |
| Local creates approval | File in /Pending_Approval/ | ⬜ |
| Human approves | File moved to /Approved/ | ⬜ |
| Local executes | Email sent | ⬜ |
| Local moves to /Done/ | File in /Done/ | ⬜ |

---

## Troubleshooting

### Problem: Cloud Agent not starting

**Solution:**
```bash
# Check .env.cloud exists
dir .env.cloud

# Check EXECUTION_MODE
type .env.cloud | findstr EXECUTION_MODE
# Should be: EXECUTION_MODE=draft_only
```

---

### Problem: No /Updates/ folder

**Solution:**
```bash
# Create manually
mkdir AI_Employee_Vault_FTE\Updates
```

---

### Problem: Local Agent not detecting updates

**Solution:**
```bash
# Check Local is running in full mode
type .env.local | findstr EXECUTION_MODE
# Should be: EXECUTION_MODE=full

# Restart Local Agent
Ctrl+C
.\run_local_agent.bat
```

---

### Problem: Both agents trying to process same file

**Solution:**
```bash
# This is expected without Git claim-by-move rule
# For now, run one at a time:

# Terminal 1: Cloud Agent only
.\run_cloud_agent.bat
# ...test...
Ctrl+C

# Terminal 2: Local Agent only
.\run_local_agent.bat
```

---

## Success Criteria

**Platinum Demo Works When:**

✅ Cloud Agent runs in `draft_only` mode (no real sending)  
✅ Local Agent runs in `full` mode (executes approved actions)  
✅ Cloud creates drafts (email, LinkedIn, Facebook, Odoo invoice)  
✅ Cloud writes to `/Updates/` folder  
✅ Local reads from `/Updates/` folder  
✅ Full handoff flow works: Email → Draft → Approval → Send → /Done/

---

## Next Steps (After Local Test Works)

### When You Get Cloud Access:

1. **Deploy Cloud Agent to VM**
   ```bash
   # On Oracle/AWS VM
   scp .env.cloud user@vm:/opt/ai-employee/
   EXECUTION_MODE=draft_only uv run python -m orchestrator
   ```

2. **Setup Git Sync**
   ```bash
   cd AI_Employee_Vault_FTE
   git init
   git remote add origin <repo-url>
   ```

3. **Test Real Cloud/Local Split**
   - Cloud on VM (24/7)
   - Local on laptop
   - Git sync over internet

---

## Test Results Template

```
Date: ___________
Tester: ___________

Cloud Agent Start: [ ] Success  [ ] Failed
Local Agent Start: [ ] Success  [ ] Failed

Draft Creation:
- Email draft: [ ] Works  [ ] Failed
- LinkedIn draft: [ ] Works  [ ] Failed
- Facebook draft: [ ] Works  [ ] Failed
- Odoo invoice draft: [ ] Works  [ ] Failed

Handoff:
- Cloud writes /Updates/: [ ] Works  [ ] Failed
- Local reads /Updates/: [ ] Works  [ ] Failed
- Approval workflow: [ ] Works  [ ] Failed
- Local executes: [ ] Works  [ ] Failed

NOTES:
_________________________________
_________________________________
```

---

**Status:** Ready for testing!
