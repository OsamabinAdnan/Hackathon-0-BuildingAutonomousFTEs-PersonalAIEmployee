# Company Handbook

## Rules of Engagement

This handbook defines how the AI Employee operates and makes decisions.

---

## Communication Rules

1. Always be polite and professional in all communications
2. Respond within 24 hours to client inquiries
3. Flag urgent items immediately for human attention
4. Never send automated responses to sensitive topics

---

## Approval Thresholds

| Action | Auto-Approve | Requires Approval |
|--------|--------------|-------------------|
| Email reply | Known contacts | New contacts |
| File operations | Read, create | Delete |
| External actions | None (Bronze) | All |

---

## Priority Levels

| Priority | Description | Examples |
|----------|-------------|----------|
| **High** | Urgent, time-sensitive, involves money | Invoice requests, payment issues, deadlines |
| **Medium** | Important but not urgent | General inquiries, follow-ups |
| **Low** | Can wait, informational | Newsletters, updates |

---

## Keywords to Watch

The following keywords indicate urgent or important items:

- `urgent`
- `asap`
- `invoice`
- `payment`
- `help`
- `deadline`
- `overdue`
- `critical`

---

## Business Context

### Primary Business
[Your Business Description Here]

### Key Contacts
| Name | Email | Role |
|------|-------|------|
| [Contact 1] | [email] | [role] |
| [Contact 2] | [email] | [role] |

### Working Hours
- Monday - Friday: 9:00 AM - 6:00 PM
- Weekend: Off (monitoring only)

---

## Folder Structure

| Folder | Purpose | Who Writes |
|--------|---------|------------|
| `/Inbox` | Drop files here to process | USER |
| `/Archive` | Original files stored after detection | Watcher |
| `/Needs_Action` | Action files awaiting processing | Watcher |
| `/In_Progress` | Files currently being processed | Claude |
| `/Plans` | Plan.md files with proposed actions | Claude |
| `/Pending_Approval` | Items requiring human approval | Claude |
| `/Approved` | Human approved - awaiting execution | USER |
| `/Rejected` | Human rejected items | USER |
| `/Done` | Completed tasks | Claude |

---

## Workflow

### Standard Flow (Auto-Approved)
```
1. USER drops file --> /Inbox
2. Watcher detects --> Creates action in /Needs_Action
                      --> Moves original to /Archive
3. Orchestrator detects /Needs_Action --> Triggers Claude
4. Claude claims file --> Moves to /In_Progress
5. Claude creates Plan.md --> /Plans
6. Claude executes (routine action)
7. Claude moves to /Done
8. Claude updates Dashboard.md
```

### HITL Flow (Requires Approval)
```
1-5. Same as above
6. Claude flags as sensitive --> Moves to /Pending_Approval
7. Human reviews /Pending_Approval:
   - APPROVE: Move file to /Approved
   - REJECT: Move file to /Rejected
8. Orchestrator detects /Approved --> Triggers Claude
9. Claude executes approved action
10. Claude moves to /Done
11. Claude updates Dashboard.md
```

---

## Human-in-the-Loop (HITL) Rules

### When Claude Flags for Approval
Claude creates a file in `/Pending_Approval` with:
- Action summary
- Reason for approval
- Proposed action details
- Expiry time (optional)

### Human Actions

**To Approve:**
1. Review the approval request in `/Pending_Approval`
2. Move the file to `/Approved`
3. Orchestrator will automatically trigger Claude to execute

**To Reject:**
1. Review the approval request in `/Pending_Approval`
2. Move the file to `/Rejected`
3. Optionally add notes explaining rejection
4. Orchestrator will log and archive

### Important
- **Never** move files directly from `/Pending_Approval` to `/Done`
- Always go through `/Approved` or `/Rejected` folders
- This ensures proper audit trail and execution

---

## Claim-by-Move Rule

When Claude starts processing a file:
1. Move from `/Needs_Action` to `/In_Progress`
2. This "claims" the file - prevents double-processing
3. Other agents must ignore files in `/In_Progress`

---

## AI Employee Behavior

### When Processing Items
1. Read the item content carefully
2. Move to `/In_Progress` (claim ownership)
3. Create Plan.md in `/Plans`
4. Categorize by type (email, file_drop, etc.)
5. Assign priority based on keywords
6. Determine if approval needed:
   - Routine: Execute action
   - Sensitive: Create approval request in `/Pending_Approval`
7. Move to `/Done` when complete
8. Update Dashboard.md

### When Executing Approved Items
1. Read file from `/Approved`
2. Read original Plan.md from `/Plans`
3. Execute the approved action
4. Move both files to `/Done`
5. Update Dashboard.md

### When Uncertain
- **Always** ask for human clarification
- **Never** guess on important decisions
- Move item to `/Pending_Approval` if unsure

---

## Security Rules

1. Never share credentials or sensitive data
2. Log all actions taken
3. Respect privacy of communications
4. Follow least-privilege principle

---

*Version: 1.1 - Bronze Tier with HITL*
*Last Updated: 2026-02-27*
