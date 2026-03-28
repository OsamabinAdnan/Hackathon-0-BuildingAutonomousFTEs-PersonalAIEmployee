---
name: send-whatsapp
description: |
  Send a WhatsApp message via WhatsApp Web using the MCP service.
  Use this skill when an approved action requires sending a WhatsApp message.
  Always confirm recipient and message content before sending.
  For messages to new contacts, require approval first.
---

# Send WhatsApp Skill

Send a WhatsApp message via WhatsApp Web using the MCP service.

---

## IMPORTANT: Output Action Tags

**Always print action tags during execution:**

```
[SKILL] Using skill: /send-whatsapp
[READ] Reading approval request
[MCP] Calling mcp__ai-employee__send_whatsapp
[DONE] WhatsApp sent to: +1234567890
```

---

## When to Use

Use this skill when:
- An approved action file requires sending a WhatsApp message
- Quick informal communication is needed
- Urgent time-sensitive messages
- Follow-up on pending items

**Require approval before sending when:**
- Message to new contact (not in Company_Handbook.md)
- Message contains pricing/financial information
- Message is formal business communication
- First-time contact with client/prospect

---

## MCP Tool

This skill uses the MCP tool:
```
mcp__ai-employee__send_whatsapp(recipient_name, message)
```

---

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| recipient_name | string | Contact name or phone number (with country code, e.g., +1234567890) |
| message | string | Message text to send |

---

## Workflow

### Step 1: Verify Approval
Check if the action has been approved:
- For new contacts: Verify approval file exists in /Approved/
- For existing contacts: Can proceed directly

### Step 2: Prepare Message Content
```
[READ] Reading approval request or action file
```
Extract:
- Recipient name/number
- Message content

### Step 3: Check DRY_RUN Mode
Before sending, check if DRY_RUN is enabled:
- If `DRY_RUN=true`: Log the message that would be sent
- If `DRY_RUN=false`: Proceed with sending

### Step 4: Send via MCP
```
[MCP] Calling mcp__ai-employee__send_whatsapp(recipient_name, message)
```

Wait for the tool response.

### Step 5: Report Result
```
[DONE] WhatsApp message sent successfully to {recipient_name}
```

Or if failed:
```
[ERROR] Failed to send WhatsApp: {error message}
```

---

## Example Usage

### Example 1: Quick Follow-up

**User:** /send-whatsapp

**AI:**
```
[SKILL] Using skill: /send-whatsapp
[READ] Reading action file: WHATSAPP_client_followup.md
[INFO] Preparing message to: +923001234567
[INFO] Message: "Hi! Just following up on our conversation..."
[MCP] Calling mcp__ai-employee__send_whatsapp(recipient_name="+923001234567", message="Hi! Just following up...")
[DONE] WhatsApp message sent successfully to +923001234567
```

### Example 2: New Contact (Requires Approval)

**AI:**
```
[SKILL] Using skill: /send-whatsapp
[READ] Checking approval status...
[INFO] This is a new contact - requires approval
[WRITE] Creating approval request in /Pending_Approval/
[DONE] Awaiting human approval before sending
```

---

## Message Templates

### Template 1: Quick Check-in
```
Hi {name}! Hope you're doing well. Just wanted to check in about {topic}. Let me know when you have a moment. Thanks!
```

### Template 2: Meeting Reminder
```
Hi {name}, this is a friendly reminder about our meeting scheduled for {date_time}. Looking forward to speaking with you!
```

### Template 3: Invoice Follow-up
```
Hi {name}, hope you're well. Just a quick reminder that invoice #{number} is due on {date}. Please let me know if you have any questions. Thanks!
```

---

## Safety Rules

1. **Keep messages concise** - WhatsApp is for quick communication
2. **Professional tone** - Even though it's informal, maintain professionalism
3. **Verify recipient** - Double-check phone number/name
4. **Check approval status** - Don't message new contacts without approval
5. **Respect DRY_RUN mode** - Don't send real messages when testing
6. **WhatsApp session required** - Ensure WhatsApp watcher setup is complete

---

## Prerequisites

Before using this skill:
1. WhatsApp session must be set up:
   ```bash
   python -m watchers --watcher whatsapp --setup
   ```
2. Browser must be logged into WhatsApp Web
3. Session data saved in `sessions/whatsapp/`

---

## Error Handling

| Error | Action |
|-------|--------|
| WhatsApp session not found | Report error, suggest running setup |
| Contact not found | Report error, ask for correct name/number |
| Not logged in | Report error, suggest re-running setup |
| Approval required | Create approval request in /Pending_Approval/ |
| MCP tool failure | Log error, move to /Done/ with error notes |

---

## Completion Checklist

- [ ] Verified approval status (if required)
- [ ] Prepared message content
- [ ] Checked DRY_RUN mode
- [ ] Called MCP tool: mcp__ai-employee__send_whatsapp
- [ ] Logged result (success or error)
- [ ] Updated action file status
