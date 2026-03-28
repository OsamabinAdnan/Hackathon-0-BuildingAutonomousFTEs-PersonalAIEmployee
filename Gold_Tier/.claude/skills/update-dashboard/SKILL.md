---
name: update-dashboard
description: |
  Update the Dashboard.md file with current system state across all categories
  (email, whatsapp, linkedin, files). Refresh statistics, pending items, in-progress
  items, approval queue, approved items, and recent activity. Use this skill after
  processing items or when the dashboard needs refreshing.
---

# Update Dashboard - Silver Tier

Update the `Dashboard.md` file with current system state across all categories.

---

## IMPORTANT: Output Action Tags

**Always print action tags during execution:**

```
[SKILL] Using skill: /update-dashboard
[READ] Reading: Dashboard.md
[WRITE] Writing: Dashboard.md
[DONE] Completed: Dashboard updated
```

---

## Silver Tier Updates

This skill now supports:
- **4 Categories**: email, whatsapp, linkedin, files
- **Category-specific counts**: Separate statistics per category
- **Enhanced status display**: Shows watcher states for all channels

---

## Workflow

### Step 1: Count Items in All Folders by Category

Count items in each folder for each category:

| Category | Inbox | Needs_Action | In_Progress | Plans | Pending_Approval | Approved | Rejected | Done |
|----------|-------|--------------|-------------|-------|------------------|----------|----------|------|
| email | count | count | count | count | count | count | count | count |
| whatsapp | count | count | count | count | count | count | count | count |
| linkedin | count | count | count | count | count | count | count | count |
| files | count | count | count | count | count | count | count | count |

### Step 2: Build Pending Items Table by Category

For each file in `/Needs_Action/<category>/`:
1. Read frontmatter
2. Extract: type, source, status, priority
3. Add to pending items table with category label

### Step 3: Build In Progress Table by Category

For each file in `/In_Progress/<category>/`:
1. Read frontmatter
2. Extract: filename, start time, action
3. Add to in progress table with category label

### Step 4: Build Pending Approval Table by Category

For each file in `/Pending_Approval/<category>/`:
1. Read frontmatter
2. Extract: filename, action, created time
3. Add to approval table with category label

### Step 5: Build Approved Table by Category

For each file in `/Approved/<category>/`:
1. Read frontmatter
2. Extract: filename, approved time, status
3. Add to approved table with category label

### Step 6: Build Recent Activity

Read recent files from all `/Done/<category>/` folders:
- Get last 10 completed items across all categories
- Extract action summary with category label
- Format for activity log

### Step 7: Calculate Statistics

Calculate totals and per-category:
- Total files in all folders
- Files per category
- Completed today (total and per category)
- Approval rate
- Success rate

### Step 8: Update Dashboard.md

Write updated content to Dashboard.md with all categories.

---

## Dashboard Template (Silver Tier)

```markdown
# Dashboard

---
> [!abstract] **AI Employee Control Center** | Silver Tier
> **Last Sync:** {LOCAL_TIMESTAMP_IN_YOUR_TIMEZONE} | **Uptime:** Active | **Version:** 2.0.0
---

## System Status

Before updating the table, read watcher heartbeat files from `Logs/watcher-status/` inside the vault. Each watcher has a JSON file named `{watcher}.json` with fields:

```json
{
  "watcher": "gmail",
  "status": "running",
  "last_check": "2026-03-02T21:10:48.123456",
  "last_error": null
}
```

Treat a watcher as `RUNNING` if `status` is `running` or `starting` **and** `last_check` is within the last 5 minutes. Otherwise mark it `OFFLINE`. If a `last_error` exists, note it in the details column.

| Component | Status | Details |
|:----------|:------:|:--------|
| Orchestrator | `RUNNING` | Monitoring active |
| Gmail Watcher | `{gmail_status}` | Checking every 120s (last check: {gmail_last}) |
| WhatsApp Watcher | `{whatsapp_status}` | Checking every 30s (last check: {whatsapp_last}) |
| LinkedIn Watcher | `{linkedin_status}` | Checking every 300s (last check: {linkedin_last}) |
| FileSystem Watcher | `{files_status}` | /Inbox monitored (last check: {files_last}) |
| Claude Code | `READY` | Connected with MCP tools |
| Dashboard | `UPDATED` | Real-time sync |

---

## Performance Metrics

### Daily Progress

**Tasks Completed Today: {total_completed}**

<div style="background: #1a1a2e; border-radius: 8px; padding: 4px; margin: 8px 0;">
<div style="background: linear-gradient(90deg, #4ade80 0%, #22c55e 100%); width: 100%; border-radius: 6px; padding: 8px 12px; color: white; font-weight: bold;">
COMPLETE - {completed}/{total} Tasks
</div>
</div>

### Queue Distribution by Category

| Category | Inbox | Needs Action | In Progress | Pending Approval | Approved | Done |
|:---------|:-----:|:------------:|:-----------:|:----------------:|:--------:|:----:|
| Email | {n} | {n} | {n} | {n} | {n} | {n} |
| WhatsApp | {n} | {n} | {n} | {n} | {n} | {n} |
| LinkedIn | {n} | {n} | {n} | {n} | {n} | {n} |
| Files | {n} | {n} | {n} | {n} | {n} | {n} |
| **TOTAL** | **{total}** | **{total}** | **{total}** | **{total}** | **{total}** | **{total}** |

---

## Work Overview

### Incoming Pipeline

> [!example]- Inbox Queue ({total} items)
> {List items by category}

> [!todo]- Needs Action ({total} items)
> {List items by category}

> [!note]- In Progress ({total} items)
> {List items by category}

### Review Pipeline

> [!warning]- Pending Approval ({total} items)
> {List items by category}

> [!success]- Approved Queue ({total} items)
> {List items by category}

> [!danger]- Rejected Items ({total} items)
> {List items by category}

### Completed Pipeline

> [!check]- Plans ({total} files)
> Planning documents stored in /Plans/

> [!abstract]- Archive ({total} files)
> Original files backed up in /Archive/

> [!tip]- Done ({total} files)
> Completed tasks archived in /Done/

---

## Recent Activity

> [!info] Activity Log
>
> | Timestamp | Category | Action | File | Result |
> |:----------|:--------:|:-------|:-----|:-------|
> | {time} | {cat} | {action} | {file} | {result} |

---

## Statistics Summary

### Folder Summary

| Folder | Total Files |
|:-------|------------:|
| Inbox | {total_inbox} |
| Needs_Action | {total_needs_action} |
| In_Progress | {total_in_progress} |
| Plans | {total_plans} |
| Pending_Approval | {total_pending_approval} |
| Approved | {total_approved} |
| Rejected | {total_rejected} |
| Archive | {total_archive} |
| Done | {total_done} |

### Category Breakdown

| Category | Inbox | Needs Action | In Progress | Plans | Approved | Archive | Done | Total |
|:---------|:-----:|:------------:|:-----------:|:-----:|:--------:|:-------:|:----:|:-----:|
| Email | {n} | {n} | {n} | {n} | {n} | {n} | {n} | {n} |
| WhatsApp | {n} | {n} | {n} | {n} | {n} | {n} | {n} | {n} |
| LinkedIn | {n} | {n} | {n} | {n} | {n} | {n} | {n} | {n} |
| Files | {n} | {n} | {n} | {n} | {n} | {n} | {n} | {n} |
| **TOTAL** | **{total}** | **{total}** | **{total}** | **{total}** | **{total}** | **{total}** | **{total}** | **{total}** |

### Throughput Metrics

| Metric | Today | This Week | Total |
|:-------|:------:|:---------:|:-----:|
| Files Processed | {n} | {n} | {n} |
| Avg. Time/Task | -- | -- | -- |
| Approval Rate | {n}% | {n}% | {n}% |
| Success Rate | {n}% | {n}% | {n}% |

---

## Quick Actions

| Action | Command | Description |
|:-------|:--------|:------------|
| Check Status | `python -m orchestrator --status` | View system status |
| Process Inbox | `/process-inbox` | Process all pending items |
| Update Dashboard | `/update-dashboard` | Refresh this dashboard |
| View Handbook | `[[Company_Handbook]]` | Read rules of engagement |
| Send Email | `/send-email` | Send email via Gmail API |
| Send WhatsApp | `/send-whatsapp` | Send WhatsApp message |
| Post LinkedIn | `/post-linkedin` | Post to LinkedIn |

---

## System Health

| Check | Status | Last Verified |
|:------|:------:|:--------------|
| Vault Structure | `OK` | {date} |
| Folder Permissions | `OK` | {date} |
| Claude Connection | `OK` | {date} |
| Gmail Watcher | `{status}` | {date} |
| WhatsApp Watcher | `{status}` | {date} |
| LinkedIn Watcher | `{status}` | {date} |
| Direct Execution | `OK` | {date} |
| Log Files | `OK` | {date} |

---

## MCP Tools Status

| Tool | Available | Last Used |
|:-----|:---------:|:----------|
| mcp__ai-employee__send_email | ✅ | {time} |
| mcp__ai-employee__draft_email | ✅ | {time} |
| mcp__ai-employee__search_emails | ✅ | {time} |
| mcp__ai-employee__send_whatsapp | ✅ | {time} |
| mcp__ai-employee__post_linkedin | ✅ | {time} |
| mcp__ai-employee__send_linkedin_message | ✅ | {time} |

---

> [!quote]- Technical Details
> **Architecture:** Subprocess-based watchers with direct execution services
> **Watchers:** Gmail (120s), WhatsApp (30s), LinkedIn (300s), FileSystem (real-time)
> **Services:** Email (Gmail API), WhatsApp (Web automation), LinkedIn (API)
> **Skills:** 7 total - process-inbox, update-dashboard, send-email, send-whatsapp, post-linkedin, send-linkedin-message, browsing-with-playwright
> **Vault Path:** {vault_path}

---

*Dashboard auto-updated by AI Employee - Silver Tier*
```

---

## Notes

- **CRITICAL: Use LOCAL SYSTEM TIME for all timestamps, NOT UTC**
  - NEVER use ISO 8601 format with Z suffix (e.g., "2026-03-03T18:27:33Z")
  - NEVER use datetime.utcnow() or UTC timestamps
  - ALWAYS use your computer's LOCAL system time
  - Format: YYYY-MM-DD HH:MM:SS (local time, 24-hour format)
  - Example: "2026-03-03 23:27:33" (local time, NOT "2026-03-03T18:27:33Z" UTC)
  - This applies to: Last Sync, Recent Activity timestamps, all date/time fields
  - If you see a timestamp with "Z" or "UTC" in it, REPLACE IT with local time
  - To get local time: Use `datetime.now()` (Python) or `Get-Date` (PowerShell)
- Always preserve the overall structure
- Update timestamp every time
- Remove completed items from tables
- Keep activity log chronological (newest first)
- Show last 10 activity entries
- Include category labels for all items

---

## Example

```
User: /update-dashboard

AI:
[SKILL] Using skill: /update-dashboard

1. Scanning folders by category...
   
   Email:
   - /Inbox/email: 0 files
   - /Needs_Action/email: 1 file
   - /In_Progress/email: 0 files
   - /Done/email: 3 files today
   
   WhatsApp:
   - /Inbox/whatsapp: 0 files
   - /Needs_Action/whatsapp: 2 files
   - /In_Progress/whatsapp: 0 files
   - /Done/whatsapp: 1 file today
   
   LinkedIn:
   - /Inbox/linkedin: 0 files
   - /Needs_Action/linkedin: 0 files
   - /In_Progress/linkedin: 0 files
   - /Done/linkedin: 0 files today
   
   Files:
   - /Inbox/files: 0 files
   - /Needs_Action/files: 0 files
   - /In_Progress/files: 0 files
   - /Done/files: 2 files today

2. Building tables by category...
   - Pending Items: 3 entries (1 email, 2 whatsapp)
   - In Progress: 0 entries
   - Pending Approval: 1 entry
   - Approved: 0 entries

3. Calculating statistics...
   - Total completed today: 6
   - Approval rate: 25%
   - Success rate: 100%

4. Updating Dashboard.md...
   [WRITE] Writing: Dashboard.md

5. [DONE] Dashboard updated successfully
```
