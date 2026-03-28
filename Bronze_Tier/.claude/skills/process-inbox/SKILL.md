---
name: process-inbox
description: |
  Process all files in the /Needs_Action folder. Read each file, create a plan,
  execute actions or flag for approval, and move completed items to /Done.
  For sensitive actions, create approval request in /Pending_Approval.
  Human will move to /Approved or /Rejected, then orchestrator triggers execution.
---

# Process Inbox

Process all pending items in the `/Needs_Action` folder.

---

## IMPORTANT: Output Action Tags

**Always print action tags during execution for logging:**

```
[SKILL] Using skill: /process-inbox
[READ] Reading: filename.md
[WRITE] Writing: filename.md
[MOVE] Moving: source -> destination
[DONE] Completed: action description
```

---

## Workflow

### Step 1: Scan Needs_Action Folder
```
[SKILL] Using skill: /process-inbox
```
List all `.md` files in the `/Needs_Action` folder.

### Step 2: Process Each Item

For each file:

1. **Read the file**
   ```
   [READ] Reading: {filename}
   ```
   Parse frontmatter and content

2. **Claim ownership**
   ```
   [MOVE] Moving: /Needs_Action/{filename} -> /In_Progress/{filename}
   ```

3. **Create a Plan.md**
   ```
   [WRITE] Writing: /Plans/PLAN_{filename}.md
   ```

4. **Determine action type**:
   - **Routine**: Execute action, then:
     ```
     [MOVE] Moving: /In_Progress/{filename} -> /Done/{filename}
     [DONE] Completed: {action summary}
     ```
   - **Sensitive**: Create approval request:
     ```
     [WRITE] Writing: /Pending_Approval/APPROVAL_{filename}.md
     [MOVE] Moving: /In_Progress/{filename} -> /Pending_Approval/{filename}
     [DONE] Flagged for approval: {reason}
     ```

### Step 3: Update Dashboard
```
[SKILL] Using skill: /update-dashboard
```
After processing all items, update `Dashboard.md`

---

## Folder Structure

| Folder | Purpose |
|--------|---------|
| `/Needs_Action` | Items waiting to be processed |
| `/In_Progress` | Items currently being processed (claimed) |
| `/Plans` | Plan.md files with proposed actions |
| `/Pending_Approval` | Items needing human approval |
| `/Approved` | Human approved - awaiting execution |
| `/Rejected` | Human rejected items |
| `/Archive` | Original files (read-only) |
| `/Done` | Completed tasks |

---

## Creating Plan.md

When processing a file, create a Plan.md in `/Plans`:

```markdown
# Plan: {original_filename}

## Source
- **Original File:** /Archive/{filename}
- **Action File:** {action_filename}
- **Type:** {type}
- **Priority:** {priority}

## Analysis
{Brief analysis of what needs to be done}

## Proposed Actions
- [ ] Action 1
- [ ] Action 2
- [ ] Action 3

## Approval Required?
- [ ] No - Routine action, will execute directly
- [ ] Yes - Sensitive action, requires human approval

## Status
- [ ] In Progress
- [ ] Pending Approval
- [ ] Approved - Awaiting Execution
- [ ] Complete

## Notes
{Any additional notes}
```

---

## Flagging for Approval (HITL)

For sensitive actions, create a file in `/Pending_Approval`:

```markdown
---
type: approval_request
action: {action_type}
created: {timestamp}
expires: {expiry_timestamp}
status: pending
---

# Approval Required

## Original File
- **Action File:** {action_filename}
- **Plan File:** /Plans/PLAN_{filename}.md

## Action Summary
{What needs to be done}

## Reason for Approval
{Why this needs human review}

## Proposed Action
{Detailed proposed action}

## Instructions for Human

### To Approve
Move this file to /Approved folder. The orchestrator will automatically trigger execution.

### To Reject
Move this file to /Rejected folder and add notes below.

## Notes (Human Use)
{Space for human to add notes}
```

---

## HITL Flow

### When Claude Flags for Approval
```
1. Claude creates approval request in /Pending_Approval
2. Claude moves action file to /Pending_Approval
3. Claude waits (does not execute)
```

### Human Reviews
```
Human opens /Pending_Approval:
  - Reads approval request
  - Checks Plan.md in /Plans
  - Makes decision:
    - APPROVE: Move file to /Approved
    - REJECT: Move file to /Rejected
```

### Orchestrator Detects /Approved
```
1. Orchestrator detects file in /Approved
2. Triggers Claude with approved action
3. Claude reads approval request
4. Claude executes the approved action
5. Claude moves files to /Done
6. Claude updates Dashboard.md
```

### Orchestrator Detects /Rejected
```
1. Orchestrator detects file in /Rejected
2. Logs the rejection
3. Archives the files
4. Updates Dashboard.md
```

---

## File Types and Actions

### File Drop (type: file_drop)
1. Read file info from action file
2. Read original file from `/Archive/{archive_path}`
3. Determine if approval needed:
   - Contains sensitive data: Flag for approval
   - Routine file: Process directly
4. Process according to type:
   - `.txt`: Read and summarize
   - `.csv`: Parse and analyze
   - `.json`: Parse and analyze
5. Move to `/Done` or `/Pending_Approval`

---

## Sensitive Actions (Require Approval)

Flag for approval when:
- Sending emails to new contacts
- Deleting files
- Sharing data externally
- Financial transactions (future tiers)
- Any action with legal implications

---

## Example Workflow - Routine

```
User: /process-inbox

AI:
1. Found 1 file in /Needs_Action
2. Processing FILE_20260227_test.txt...
   - Moving to /In_Progress (claiming)
   - Creating Plan.md in /Plans
   - Reading original from /Archive
   - Analysis: Routine text file, no sensitive content
   - Action: Summarize content
   - Moving to /Done
3. Updating Dashboard.md
4. Complete
```

---

## Example Workflow - Sensitive (HITL)

```
User: /process-inbox

AI:
1. Found 1 file in /Needs_Action
2. Processing EMAIL_client_request.md...
   - Moving to /In_Progress (claiming)
   - Creating Plan.md in /Plans
   - Analysis: Email to new contact, contains pricing inquiry
   - Action: Sensitive - requires approval
   - Creating approval request in /Pending_Approval
   - Moving to /Pending_Approval
3. Waiting for human approval...
4. Dashboard.md updated - shows pending approval

[Human reviews and moves to /Approved]

AI (triggered by orchestrator):
5. Detected approved file: APPROVAL_EMAIL_client_request.md
6. Reading approval request and Plan.md
7. Executing approved action: Send reply to client
8. Moving files to /Done
9. Updating Dashboard.md
10. Complete
```

---

## Safety Rules

- **Always claim files first** - Move to `/In_Progress` before processing
- **Create plans** - Document proposed actions before executing
- **Flag sensitive items** - Use `/Pending_Approval` for uncertain/sensitive actions
- **Never bypass HITL** - Wait for human to move to `/Approved`
- **Never delete files** without explicit permission
- **Always check Company_Handbook.md** for rules

---

## Completion Checklist

- [ ] All files processed from `/Needs_Action`
- [ ] Plan.md created for each processed file
- [ ] Routine actions executed and moved to `/Done`
- [ ] Sensitive actions moved to `/Pending_Approval`
- [ ] Dashboard.md updated
