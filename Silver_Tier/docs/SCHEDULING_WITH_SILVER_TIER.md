# How Scheduling Works with Silver Tier

**Date:** 2026-03-04

---

## Current Silver Tier Scheduling Status

### **What's Already Working:**
- ✅ **Dashboard Updates:** Every 10 minutes (built into orchestrator)
- ✅ **Watchers:** Running continuously (Gmail, WhatsApp, LinkedIn, FileSystem)
- ✅ **HITL Workflow:** Fully operational

### **What Gets Added with Scheduling Setup:**

When you run `.\scheduling\setup_task_scheduler.ps1 -Install`:

#### 1. **Weekly CEO Briefing (Monday 10:00 AM)**
- **Where:** `E:\Hackathon-0-Personal-FTE\Silver_Tier\AI_Employee_Vault_FTE\Briefings\`
- **File:** `YYYY-MM-DD_Monday_Briefing.md`
- **What it does:** Scans all Silver Tier folders and generates comprehensive report:
  - Tasks completed (from `/Done/`)
  - Pending approvals (from `/Pending_Approval/`)
  - Needs action (from `/Needs_Action/` by category)
  - Bottlenecks and suggestions
  - Category breakdown: email, whatsapp, linkedin, files

#### 2. **LinkedIn Weekly Post (Monday 9:00 AM)**
- **Uses:** Built-in templates from `linkedin_poster.py`
- **Template:** `weekly_update` (already configured)
- **What it posts:** Business updates to grow your network
- **Credentials:** Uses your existing LinkedIn API tokens from `.env`

#### 3. **Orchestrator Startup (System Boot)**
- **What it does:** Ensures Silver Tier system starts automatically after reboot
- **Result:** Watchers and orchestrator always running

---

## Integration Points with Silver Tier

### **Data Sources:**
- Reads from the same vault: `AI_Employee_Vault_FTE/`
- Uses same folder structure: `/Needs_Action/`, `/Done/`, `/Pending_Approval/`, etc.
- Leverages 4-category system: email, whatsapp, linkedin, files

### **Template System:**
- **LinkedIn Poster** has 7 built-in templates:
  - `product_launch`, `milestone`, `tip`, `industry_news`, `team_announcement`, `customer_success`, `weekly_update`
- **Default:** Uses `weekly_update` template for Monday posts
- **Customizable:** Can add your own content to templates

### **Credential Integration:**
- Uses existing `.env` file for LinkedIn API tokens
- No additional setup needed if LinkedIn already working
- Direct integration with `mcp_server/linkedin_service.py`

---

## Step-by-Step: What Happens When You Run Setup

### **Command:** `.\scheduling\setup_task_scheduler.ps1 -Install`

1. **Creates 3 Windows Scheduled Tasks:**
   ```
   AI_Employee_Weekly_Briefing: Monday 10:00 AM
   AI_Employee_LinkedIn_Post: Monday 9:00 AM
   AI_Employee_Orchestrator_Startup: System boot
   ```

2. **Weekly Briefing Process:**
   ```
   Monday 10:00 AM → PowerShell script runs → Scans vault folders →
   Generates report → Saves to /Briefings/ folder
   ```

3. **LinkedIn Post Process:**
   ```
   Monday 9:00 AM → PowerShell script runs → Loads weekly_update template →
   Posts via LinkedIn API using your credentials
   ```

4. **Orchestrator Resurrection:**
   ```
   System boot → Task starts orchestrator → All watchers begin monitoring
   ```

---

## Files Generated

### **CEO Briefing Example:**
`E:\Hackathon-0-Personal-FTE\Silver_Tier\AI_Employee_Vault_FTE\Briefings\2026-03-09_Monday_Briefing.md`
```markdown
# Monday Morning CEO Briefing
---
generated: 2026-03-09T10:00:00
period: 2026-03-02 to 2026-03-09
type: weekly_ceo_briefing
---

## Key Metrics
| Metric | Count |
|--------|-------|
| Tasks Completed | 45 |
| Pending Approvals | 3 |
| AWaiting Action | 12 |

## Needs Action by Category
| Category | Items |
|----------|-------|
| Email | 5 |
| WhatsApp | 2 |
| LinkedIn | 1 |
| Files | 4 |
```

### **LinkedIn Post Templates:**
- Uses the `weekly_update` template from `linkedin_poster.py`
- Automatically fills in company-specific details
- Posts to your LinkedIn feed

---

## Silver Tier Enhancement

The scheduling system **enhances** your current Silver Tier setup by:

1. **Adding Proactivity:** Weekly reports transform AI from reactive to proactive
2. **Business Growth:** Automatic LinkedIn posts for marketing/sales
3. **Reliability:** System resurrection ensures 24/7 operation
4. **Reporting:** CEO briefings provide business insights
5. **Consistency:** Regular automated operations

---

## Activation Command

```powershell
cd E:\Hackathon-0-Personal-FTE\Silver_Tier\scheduling
.\setup_task_scheduler.ps1 -Install
```

**Result:**
- ✅ Next Monday morning: CEO briefing in your `/Briefings/` folder
- ✅ LinkedIn post goes out (using your credentials and templates)
- ✅ System stays running after reboots
- ✅ All Silver Tier functionality continues unchanged

---

**Status:** Ready to activate - integrates seamlessly with existing Silver Tier architecture.