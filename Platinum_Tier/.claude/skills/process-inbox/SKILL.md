---
name: process-inbox
description: |
  Process all files in the /Needs_Action folder across all categories 
  (email, whatsapp, linkedin, files). Read each file, create a plan,
  execute actions or flag for approval, and move completed items to /Done.
  For sensitive actions, create approval request in /Pending_Approval.
  Human will move to /Approved or /Rejected, then orchestrator triggers execution.
  Uses MCP tools for external actions (send email, WhatsApp, LinkedIn posts).
---

# Process Inbox - Silver Tier

Process all pending items in the `/Needs_Action/<category>/` folders.

---

## IMPORTANT: Output Action Tags

**Always print action tags during execution for logging:**

```
[SKILL] Using skill: /process-inbox
[READ] Reading: filename.md
[WRITE] Writing: filename.md
[MOVE] Moving: source -> destination
[MCP] Using MCP tool: mcp__ai-employee__*
[DONE] Completed: action description
```

---

## Silver Tier Updates

This skill now supports:
- **4 Categories**: email, whatsapp, linkedin, files
- **MCP Tools**: For external actions (send email, WhatsApp, LinkedIn)
- **Category Subfolders**: All operations respect category folders

---

## Workflow

### Step 1: Scan All Category Folders
```
[SKILL] Using skill: /process-inbox
```
List all `.md` files in:
- `/Needs_Action/email/`
- `/Needs_Action/whatsapp/`
- `/Needs_Action/linkedin/`
- `/Needs_Action/files/`

### Step 2: Process Each Item

For each file in each category:

1. **Read the file**
   ```
   [READ] Reading: {filename}
   ```
   Parse frontmatter (type, priority, status) and content

2. **Claim ownership**
   ```
   [MOVE] Moving: /Needs_Action/<category>/{filename} -> /In_Progress/<category>/{filename}
   ```

3. **Create a Plan.md**
   ```
   [WRITE] Writing: /Plans/<category>/PLAN_{filename}.md
   ```

4. **Determine action type**:
   - **Routine**: Execute action (possibly using MCP tools)
   - **Sensitive**: Create approval request in `/Pending_Approval/<category>/`

5. **Execute or Flag**:
   - **Routine**:
     ```
     [MCP] Using MCP tool: mcp__ai-employee__*
     [MOVE] Moving: /In_Progress/<category>/{filename} -> /Done/<category>/{filename}
     [DONE] Completed: {action summary}
     ```
   - **Sensitive**:
     ```
     [WRITE] Writing: /Pending_Approval/<category>/APPROVAL_{filename}.md
     [DONE] Flagged for approval: {reason}
     ```
     CRITICAL WORKFLOW:

     **DO NOT MOVE the original file from /In_Progress/**
     - Original file STAYS in `/In_Progress/<category>/{filename}` (locked/claimed)
     - Only the APPROVAL REQUEST file goes to `/Pending_Approval/<category>/APPROVAL_{filename}.md`

     **File Movement Rules:**
     - `/In_Progress/<category>/{filename}` → STAYS HERE (locked until decision)
     - `/Pending_Approval/<category>/APPROVAL_{filename}.md` → NEW approval request file

     **After Human Decision:**
     - If APPROVED: Orchestrator triggers Claude → Claude executes action → moves original to `/Done/<category>/`
     - If REJECTED: Original file moves to `/Archive/<category>/` (action cancelled)

---

## MCP Tools Available

When executing actions, use these MCP tools:

| Tool | Purpose | Category |
|------|---------|----------|
| `mcp__ai-employee__send_email(to, subject, body)` | Send email via Gmail | email |
| `mcp__ai-employee__draft_email(to, subject, body)` | Create email draft | email |
| `mcp__ai-employee__search_emails(query)` | Search Gmail | email |
| `mcp__ai-employee__send_whatsapp(recipient_name, message)` | Send WhatsApp message | whatsapp |
| `mcp__ai-employee__post_linkedin(text, visibility)` | Post to LinkedIn | linkedin |
| `mcp__ai-employee__send_linkedin_message(recipient_name, message)` | Send LinkedIn DM | linkedin |

---

## File Types and Actions by Category

### Email Category (`/Needs_Action/email/`)

**Action Types:**
- Reply to email → Use `mcp__ai-employee__send_email` or `mcp__ai-employee__draft_email`
- Forward email → Use `mcp__ai-employee__send_email`
- Archive email → Move to /Done/email/

**Approval Required When:**
- **ALL EMAILS REQUIRE APPROVAL BEFORE SENDING** (MANDATORY)
- This includes replies, forwards, and new emails
- Only routine archiving/reading does NOT require approval

### WhatsApp Category (`/Needs_Action/whatsapp/`)

**Action Types:**
- Reply to message → Use `mcp__ai-employee__send_whatsapp`
- Follow-up → Use `mcp__ai-employee__send_whatsapp`

**Approval Required When:**
- Messaging new contact
- Business proposals
- Financial/pricing discussions

### LinkedIn Category (`/Needs_Action/linkedin/`)

**Action Types:**
- Post update → Use `mcp__ai-employee__post_linkedin`
- Reply to message → Use `mcp__ai-employee__send_linkedin_message`
- Connection follow-up → Use `mcp__ai-employee__send_linkedin_message`

**Approval Required When:**
- ALL posts (always require approval)
- ALL messages (always require approval)

### Files Category (`/Needs_Action/files/`)

**Action Types:**
- Process document → Read and analyze
- Extract data → Parse and summarize
- Convert format → Process and save

**Approval Required When:**
- Deleting files
- Sharing externally
- Sensitive data handling

---

## Creating Plan.md

When processing a file, create a Plan.md in `/Plans/<category>/`:

```markdown
# Plan: {original_filename}

## Source
- **Category:** {email|whatsapp|linkedin|files}
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

## MCP Tools Required
- [ ] mcp__ai-employee__send_email
- [ ] mcp__ai-employee__send_whatsapp
- [ ] mcp__ai-employee__post_linkedin
- [ ] mcp__ai-employee__send_linkedin_message
- [ ] None (routine file processing)

## Approval Required?
- [ ] No - Routine action, will execute directly
- [ ] Yes - Sensitive action, requires human approval
  Reason: {why approval is needed}

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

For sensitive actions, create a file in `/Pending_Approval/<category>/`:

```markdown
---
type: approval_request
action: {action_type}
category: {email|whatsapp|linkedin|files}
created: {timestamp}
expires: {expiry_timestamp}
status: pending
---

# Approval Required

## Original File
- **Action File:** {action_filename}
- **Plan File:** /Plans/<category>/PLAN_{filename}.md
- **Category:** {category}

## Action Summary
{What needs to be done}

## Reason for Approval
{Why this needs human review}

## Proposed Action (Email Format)
When sending emails, ALWAYS format the details exactly like this so DirectExecutor can parse them:
```
- To: user@example.com
- Subject: Subject line here
- Body:
  First line of the email
  Remaining lines...
```
Use plain text for the body (no block quotes) and one space of indentation. For WhatsApp/LinkedIn, include `- Recipient:` and `- Message:` lines instead (with one-space indentation for the multi-line message body).

## MCP Tool to Use
{Which MCP tool will be used, e.g., mcp__ai-employee__send_email}

## Instructions for Human

### To Approve
Move this file to /Approved/<category>/ folder. The orchestrator will automatically trigger execution.

### To Reject
Move this file to /Rejected/<category>/ folder and add notes below.

## Notes (Human Use)
{Space for human to add notes}
```

---

## HITL Flow

### When Claude Flags for Approval (Initial Processing)
```
1. Claude reads action file from /Needs_Action/<category>/
2. Claude moves action file to /In_Progress/<category>/ (CLAIM - lock it)
3. Claude creates Plan.md in /Plans/<category>/
4. Claude creates APPROVAL REQUEST in /Pending_Approval/<category>/APPROVAL_{filename}.md
5. Claude KEEPS original file in /In_Progress/<category>/ (DO NOT MOVE IT)
6. Claude outputs: [DONE] Flagged for approval: {reason}
7. Claude waits (does not execute action)
```

**File State After Initial Processing:**
- `/Needs_Action/<category>/` → EMPTY (file claimed)
- `/In_Progress/<category>/{filename}` → LOCKED (original file stays here)
- `/Plans/<category>/PLAN_{filename}.md` → Created
- `/Pending_Approval/<category>/APPROVAL_{filename}.md` → Created (for human review)

### Human Reviews and Decides
```
Human opens /Pending_Approval/<category>/:
  - Reads APPROVAL_{filename}.md
  - Checks Plan.md in /Plans/<category>/
  - Makes decision:
    - APPROVE: Move APPROVAL_{filename}.md to /Approved/<category>/
    - REJECT: Move APPROVAL_{filename}.md to /Rejected/<category>/
```

### Orchestrator Detects /Approved (Execution Phase)
```
1. Orchestrator detects APPROVAL_{filename}.md in /Approved/<category>/
2. Triggers Claude with approved action
3. Claude reads approval request + Plan.md
4. Claude uses appropriate MCP tool to execute action
5. Claude moves ORIGINAL file from /In_Progress/<category>/ to /Archive/<category>/
6. Claude moves APPROVAL file from /Approved/<category>/ to /Done/<category>/
7. Claude updates Dashboard.md
```

**File State After Approval & Execution:**
- `/In_Progress/<category>/{filename}` → MOVED to /Archive (action completed)
- `/Approved/<category>/APPROVAL_{filename}.md` → MOVED to /Done
- `/Archive/<category>/{filename}` → Original file (completed action record)
- `/Done/<category>/APPROVAL_{filename}.md` → Approval record (audit trail)

### Orchestrator Detects /Rejected (Cancellation Phase)
```
1. Orchestrator detects APPROVAL_{filename}.md in /Rejected/<category>/
2. Logs the rejection with reason
3. Renames file: APPROVAL_{filename}.md → REJECTED_APPROVAL_{filename}.md
4. Keeps file in /Rejected/<category>/ (audit trail)
5. Moves ORIGINAL file from /In_Progress/<category>/ to /Archive/<category>/
6. Updates Dashboard.md
```

**File State After Rejection:**
- `/In_Progress/<category>/{filename}` → MOVED to /Archive (action cancelled)
- `/Rejected/<category>/REJECTED_APPROVAL_{filename}.md` → RENAMED (stays in Rejected folder as audit trail)
- `/Archive/<category>/{filename}` → Original file (cancelled action record)

**CRITICAL RULES:**
- In BOTH cases (Approved OR Rejected), the original file from `/In_Progress/<category>/` moves to `/Archive/<category>/`
- If APPROVED: Execute action first, then move original to Archive
- If REJECTED: Just move original to Archive without executing
- Rejected approval files get `REJECTED_` prefix and stay in `/Rejected/<category>/` as audit trail
- Approved approval files move to `/Done/<category>/` as audit trail

---

## Example Workflow - Email (Routine)

```
User: /process-inbox

AI:
1. Scanning /Needs_Action folders...
2. Found 1 file: [email] EMAIL_20260301_client_inquiry.md
3. Processing...
   - [MOVE] Moving to /In_Progress/email/ (claiming)
   - [WRITE] Creating Plan.md in /Plans/email/
   - [READ] Reading email content
   - Analysis: Routine inquiry from existing client
   - Action: Send reply using MCP tool
   - [MCP] Using mcp__ai-employee__send_email(to="client@example.com", ...)
   - [MOVE] Moving to /Done/email/
   - [DONE] Email sent to client@example.com
4. Updating Dashboard.md
5. Complete
```

---

## Example Workflow - LinkedIn Post (Requires Approval)

```
User: /process-inbox

AI:
1. Scanning /Needs_Action folders...
2. Found 1 file: [linkedin] LINKEDIN_post_draft.md
3. Processing...
   - [MOVE] Moving to /In_Progress/linkedin/ (claiming)
   - [WRITE] Creating Plan.md in /Plans/linkedin/
   - [READ] Reading post content
   - Analysis: Business update post
   - Action: Post to LinkedIn (ALWAYS requires approval)
   - [WRITE] Creating approval request in /Pending_Approval/linkedin/
   - [MOVE] Moving to /Pending_Approval/linkedin/
   - [DONE] Awaiting human approval before posting

[Human reviews and moves to /Approved/linkedin/]

AI (triggered by orchestrator):
4. Detected approved file: /Approved/linkedin/APPROVAL_LINKEDIN_post_draft.md
5. Reading approval request and Plan.md
6. Executing approved action:
   - [MCP] Using mcp__ai-employee__post_linkedin(text="...", visibility="PUBLIC")
   - [DONE] LinkedIn post created! Post ID: urn:li:ugcPost:123456
7. Moving files to /Done/linkedin/
8. Updating Dashboard.md
9. Complete
```

---

## Safety Rules

- **Always claim files first** - Move to `/In_Progress/<category>/` before processing
- **Create plans** - Document proposed actions before executing
- **Flag sensitive items** - Use `/Pending_Approval/<category>/` for uncertain/sensitive actions
- **Never bypass HITL** - Wait for human to move to `/Approved/<category>/`
- **Use MCP tools correctly** - Reference full tool name: `mcp__ai-employee__*`
- **Check DRY_RUN mode** - Don't execute real actions when testing
- **Always check Company_Handbook.md** for rules

---

## Completion Checklist

- [ ] All files processed from `/Needs_Action/<category>/`
- [ ] Plan.md created for each processed file (in `/Plans/<category>/`)
- [ ] Routine actions executed (using MCP tools when needed) and moved to `/Done/<category>/`
- [ ] Sensitive actions moved to `/Pending_Approval/<category>/`
- [ ] Dashboard.md updated with results
- [ ] Action tags printed for logging
