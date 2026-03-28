---
name: update-dashboard
description: |
  Update the Dashboard.md file with current system state. Refresh statistics,
  pending items, in-progress items, approval queue, approved items, and recent activity.
  Use this skill after processing items or when the dashboard needs refreshing.
---

# Update Dashboard

Update the `Dashboard.md` file with current system state.

---

## IMPORTANT: Output Action Tags

**Always print action tags during execution for logging:**

```
[SKILL] Using skill: /update-dashboard
[READ] Reading: Dashboard.md
[WRITE] Writing: Dashboard.md
[DONE] Completed: Dashboard updated
```

---

## Workflow

### Step 1: Count Items in All Folders

Count items in each folder:
- `/Inbox` - Raw incoming items
- `/Needs_Action` - Pending items
- `/In_Progress` - Items being processed
- `/Plans` - Plan files
- `/Pending_Approval` - Items awaiting approval
- `/Approved` - Approved items awaiting execution
- `/Rejected` - Rejected items
- `/Archive` - Archived original files
- `/Done` - Completed items (today)

### Step 2: Build Pending Items Table

For each file in `/Needs_Action`:
1. Read frontmatter
2. Extract: type, source, status, priority
3. Add to pending items table

### Step 3: Build In Progress Table

For each file in `/In_Progress`:
1. Read frontmatter
2. Extract: filename, start time, action
3. Add to in progress table

### Step 4: Build Pending Approval Table

For each file in `/Pending_Approval`:
1. Read frontmatter
2. Extract: filename, action, created time
3. Add to approval table

### Step 5: Build Approved Table

For each file in `/Approved`:
1. Read frontmatter
2. Extract: filename, approved time, status
3. Add to approved table

### Step 6: Build Recent Activity

Read recent files from `/Done`:
- Get last 10 completed items
- Extract action summary
- Format for activity log

### Step 7: Calculate Statistics

Calculate:
- Files in Inbox
- Needs Action count
- In Progress count
- Pending Approval count
- Approved count
- Rejected count
- Completed today

### Step 8: Update Dashboard.md

Write updated content to Dashboard.md:

**IMPORTANT: Use local system time for all timestamps, NOT UTC.**

```markdown
# Dashboard

## System Status
- **Last Updated:** [current timestamp in LOCAL time format: YYYY-MM-DD HH:MM:SS]
- **Status:** [Active/Idle]
- **Mode:** Bronze Tier
- **Active Tasks:** [count from Needs_Action + In_Progress + Approved]

---

## Pending Items

| Type | Source | Status | Priority |
|------|--------|--------|----------|
| [from Needs_Action files] |

---

## In Progress

| File | Started | Action |
|------|---------|--------|
| [from In_Progress files] |

---

## Pending Approval

| File | Action | Waiting Since |
|------|--------|---------------|
| [from Pending_Approval files] |

---

## Approved (Awaiting Execution)

| File | Approved At | Status |
|------|-------------|--------|
| [from Approved files] |

---

## Recent Activity

- [timestamp] [action summary]

---

## Quick Stats

| Metric | Count |
|--------|-------|
| Files in Inbox | [count] |
| Needs Action | [count] |
| In Progress | [count] |
| Pending Approval | [count] |
| Approved | [count] |
| Rejected | [count] |
| Completed Today | [count] |

---

## Folder Status

| Folder | Count | Status |
|--------|-------|--------|
| /Inbox | [count] | [Ready/Empty] |
| /Needs_Action | [count] | [Ready/Empty] |
| /In_Progress | [count] | [Ready/Empty] |
| /Plans | [count] | [Ready/Empty] |
| /Pending_Approval | [count] | [Ready/Empty] |
| /Approved | [count] | [Ready/Empty] |
| /Rejected | [count] | [Ready/Empty] |
| /Archive | [count] | [Ready/Empty] |
| /Done | [count] | [Ready/Empty] |

---

*Last updated by AI Employee - Bronze Tier*
```

---

## Dashboard Sections Reference

### System Status Section
| Field | Description |
|-------|-------------|
| Last Updated | ISO timestamp of last update |
| Status | Active (has tasks) or Idle (no tasks) |
| Mode | Bronze/Silver/Gold/Platinum |
| Active Tasks | Count of files in /Needs_Action + /In_Progress + /Approved |

### Pending Items Section
| Column | Description |
|--------|-------------|
| Type | file_drop, email |
| Source | Original filename |
| Status | pending, waiting |
| Priority | high, medium, low |

### In Progress Section
| Column | Description |
|--------|-------------|
| File | Action filename |
| Started | When processing started |
| Action | Current action being performed |

### Pending Approval Section
| Column | Description |
|--------|-------------|
| File | Approval request filename |
| Action | What needs approval |
| Waiting Since | When it was submitted |

### Approved Section
| Column | Description |
|--------|-------------|
| File | Approved filename |
| Approved At | When human approved |
| Status | awaiting_execution, executing |

### Quick Stats Section
| Metric | Description |
|--------|-------------|
| Files in Inbox | Count in /Inbox |
| Needs Action | Count in /Needs_Action |
| In Progress | Count in /In_Progress |
| Pending Approval | Count in /Pending_Approval |
| Approved | Count in /Approved |
| Rejected | Count in /Rejected |
| Completed Today | Count in /Done today |

---

## Example

```
User: /update-dashboard

AI:
1. Scanning folders...
   - /Inbox: 0 files
   - /Needs_Action: 0 files
   - /In_Progress: 0 files
   - /Plans: 2 files
   - /Pending_Approval: 1 file
   - /Approved: 1 file
   - /Rejected: 0 files
   - /Archive: 3 files
   - /Done: 5 files today

2. Building tables...
   - Pending Items: 0 entries
   - In Progress: 0 entries
   - Pending Approval: 1 entry
   - Approved: 1 entry

3. Calculating statistics...

4. Updating Dashboard.md

5. Dashboard updated successfully
```

---

## Notes

- Always preserve the overall structure
- Update timestamp every time
- Remove completed items from tables
- Keep activity log chronological (newest first)
- Show last 10 activity entries
