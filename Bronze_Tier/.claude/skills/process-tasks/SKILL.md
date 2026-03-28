# process-tasks

End-to-end task orchestrator that runs the complete AI Employee workflow.

## When to Use

Invoke this skill when:
- User asks to "process tasks" or "run workflow"
- User wants full automation of pending work
- Starting a new AI Employee session
- After dropping files in Inbox

## Description

Orchestrates the complete AI Employee workflow:
1. Process Inbox → Create action items
2. Create Plans → Generate execution plans
3. Execute Tasks → Run safe actions, create approval requests
4. Update Dashboard → Reflect current state

## Workflow

```
┌─────────────────┐
│  Process Inbox  │  Scan Inbox, create action items
└────────┬────────┘
         ↓
┌─────────────────┐
│  Create Plans   │  Generate execution plans
└────────┬────────┘
         ↓
┌─────────────────┐
│  Execute Tasks  │  Run safe actions, request approval for sensitive
└────────┬────────┘
         ↓
┌─────────────────┐
│ Update Dashboard│  Refresh Dashboard.md
└─────────────────┘
```

## Instructions

### Phase 1: Process Inbox
1. Scan `AI_Employee_Vault/Inbox/` for files
2. For each file, create action item in `Needs_Action/`
3. Log: "Processed X files from Inbox"

### Phase 2: Create Plans
1. Scan `AI_Employee_Vault/Needs_Action/` for tasks
2. For each task, create plan in `Plans/`
3. Identify approval requirements per `Company_Handbook.md`
4. Log: "Created X execution plans"

### Phase 3: Execute Tasks
1. Read each plan from `Plans/`
2. Execute steps that are safe (no approval required):
   - File read operations
   - File create operations (within vault)
   - Analysis and summarization
3. For steps requiring approval:
   - Create approval request in `Pending_Approval/`
   - Mark as blocked in plan
4. Move completed tasks to `Done/`
5. Log all actions

### Phase 4: Update Dashboard
1. Update `Dashboard.md` with current state
2. Add any alerts for attention-needed items
3. Log: "Dashboard updated"

## Safety Checks

Before executing any action, verify against `Company_Handbook.md`:

| Action | Can Execute? | Action Required |
|--------|--------------|-----------------|
| Read file | ✅ Yes | Execute directly |
| Create file | ✅ Yes | Execute directly |
| Delete file | ❌ No | Create approval request |
| Email known contact | ✅ Yes | Execute directly |
| Email new contact | ❌ No | Create approval request |
| Payment <$50 | ✅ Yes | Execute directly |
| Payment >$100 | ❌ No | Create approval request |

## Approval Request Template

When creating approval requests:

```markdown
---
type: approval_request
action: <action_type>
created: <timestamp>
expires: <24_hours_later>
status: pending
---

# Approval Required

## Action
<description of action to be taken>

## Details
| Property | Value |
|----------|-------|
| <key> | <value> |

## To Approve
Move this file to /Approved folder.

## To Reject
Move this file to /Rejected folder.
```

## Output Format

Report complete workflow results:

```
═══════════════════════════════════════
  AI EMPLOYEE - TASK PROCESSING
═══════════════════════════════════════

📂 PHASE 1: INBOX SCAN
───────────────────────
Found X files in Inbox
Created X action items

📋 PHASE 2: PLANNING
───────────────────────
Analyzed X tasks
Created X plans
X require approval

⚡ PHASE 3: EXECUTION
───────────────────────
Executed: X tasks
Pending approval: X tasks
Errors: X (if any)

📊 PHASE 4: DASHBOARD
───────────────────────
Dashboard updated

═══════════════════════════════════════
  SUMMARY: X completed, X awaiting approval
═══════════════════════════════════════
```

## Notes

- Stop at approval-required steps - do not proceed until approved
- Log all actions to `Logs/YYYY-MM-DD.json`
- Report errors clearly but continue with other tasks
- This skill does NOT auto-approve sensitive actions
