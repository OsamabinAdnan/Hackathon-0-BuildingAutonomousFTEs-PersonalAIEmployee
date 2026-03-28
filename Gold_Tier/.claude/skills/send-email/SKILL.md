---
name: send-email
description: |
  Send an email via Gmail using the MCP email service.
  Use this skill when an approved action requires sending an email.
  Always confirm recipient, subject, and body before sending.
  For sensitive emails (new contacts, financial info), require approval first.
---

# Send Email Skill

Send an email via Gmail using the MCP email service.

---

## IMPORTANT: Output Action Tags

**Always print action tags during execution:**

```
[SKILL] Using skill: /send-email
[READ] Reading approval request
[MCP] Calling mcp__ai-employee__send_email
[DONE] Email sent to: recipient@example.com
```

---

## When to Use

Use this skill when:
- An approved action file requires sending an email
- A routine email reply is needed (existing contact)
- Follow-up emails for business communications

**Require approval before sending when:**
- Email to new contact (not in Company_Handbook.md)
- Email contains pricing/financial information
- Email contains sensitive business data
- Email is a formal proposal or contract

---

## MCP Tool

This skill uses the MCP tool:
```
mcp__ai-employee__send_email(to, subject, body)
```

---

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| to | string | Recipient email address |
| subject | string | Email subject line |
| body | string | Email body text (can include line breaks) |

---

## Workflow

### Step 1: Verify Approval
Check if the action has been approved:
- For sensitive emails: Verify approval file exists in /Approved/
- For routine emails: Check Company_Handbook.md for existing contact

### Step 2: Prepare Email Content
```
[READ] Reading approval request or action file
```
Extract:
- Recipient email address
- Email subject
- Email body content

### Step 3: Check DRY_RUN Mode
Before sending, check if DRY_RUN is enabled:
- If `DRY_RUN=true`: Log the email that would be sent
- If `DRY_RUN=false`: Proceed with sending

### Step 4: Send Email via MCP
```
[MCP] Calling mcp__ai-employee__send_email(to, subject, body)
```

Wait for the tool response.

### Step 5: Report Result
```
[DONE] Email sent successfully to {recipient}
```

Or if failed:
```
[ERROR] Failed to send email: {error message}
```

---

## Example Usage

### Example 1: Routine Reply

**User:** /send-email

**AI:**
```
[SKILL] Using skill: /send-email
[READ] Reading action file: EMAIL_client_inquiry.md
[INFO] Preparing email to: john@example.com
[INFO] Subject: Re: Project Inquiry
[MCP] Calling mcp__ai-employee__send_email(to="john@example.com", subject="Re: Project Inquiry", body="Hi John,\n\nThank you for your inquiry...\n\nBest regards")
[DONE] Email sent successfully to john@example.com (Message ID: msg_12345)
```

### Example 2: Sensitive Email (Requires Approval)

**User:** /send-email

**AI:**
```
[SKILL] Using skill: /send-email
[READ] Checking approval status...
[INFO] This email requires approval (new contact)
[WRITE] Creating approval request in /Pending_Approval/
[MOVE] Moving action file to /Pending_Approval/
[DONE] Awaiting human approval before sending
```

**Human:** Moves file to /Approved/

**AI (triggered by orchestrator):**
```
[READ] Reading approved action
[MCP] Calling mcp__ai-employee__send_email(...)
[DONE] Email sent successfully
```

---

## Email Templates

### Template 1: Client Inquiry Response
```
Subject: Re: {original_subject}

Dear {name},

Thank you for your inquiry regarding {topic}.

{response_content}

Please let me know if you have any questions.

Best regards,
{your_name}
```

### Template 2: Invoice Follow-up
```
Subject: Invoice #{number} - Payment Reminder

Dear {name},

This is a friendly reminder that invoice #{number} is now due.

Amount: ${amount}
Due Date: {date}

Please let us know if you have any questions.

Best regards,
{your_name}
```

---

## Safety Rules

1. **Always verify recipient email** - Check for typos
2. **Check approval status** - Don't send sensitive emails without approval
3. **Review email content** - Ensure professional tone
4. **Log all sent emails** - For audit trail
5. **Respect DRY_RUN mode** - Don't send real emails when testing

---

## Error Handling

| Error | Action |
|-------|--------|
| Gmail not authenticated | Report error, suggest running Gmail watcher setup |
| Invalid email address | Report error, ask for correct address |
| Approval required | Create approval request in /Pending_Approval/ |
| MCP tool failure | Log error, move to /Done/ with error notes |

---

## Completion Checklist

- [ ] Verified approval status (if required)
- [ ] Prepared email content (to, subject, body)
- [ ] Checked DRY_RUN mode
- [ ] Called MCP tool: mcp__ai-employee__send_email
- [ ] Logged result (success or error)
- [ ] Updated action file status
