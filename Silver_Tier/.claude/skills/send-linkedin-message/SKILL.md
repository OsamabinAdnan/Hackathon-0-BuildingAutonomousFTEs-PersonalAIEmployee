---
name: send-linkedin-message
description: |
  Send a direct message on LinkedIn using Playwright browser automation.
  Use this skill for personalized outreach, follow-ups, and networking.
  All LinkedIn messages require human approval before sending.
---

# Send LinkedIn Message Skill

Send a direct message on LinkedIn using Playwright browser automation.

---

## IMPORTANT: Output Action Tags

**Always print action tags during execution:**

```
[SKILL] Using skill: /send-linkedin-message
[READ] Reading approval request
[MCP] Calling mcp__ai-employee__send_linkedin_message
[DONE] LinkedIn message sent to: {recipient_name}
```

---

## When to Use

Use this skill when:
- Following up with a new connection
- Responding to a LinkedIn inquiry
- Personalized outreach to prospects
- Networking with industry professionals
- Scheduling meetings/calls

**ALWAYS require approval before sending:**
- All LinkedIn messages require human approval
- Especially important for first-time contacts
- Ensures professional tone and messaging

---

## MCP Tool

This skill uses the MCP tool:
```
mcp__ai-employee__send_linkedin_message(recipient_name, message)
```

---

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| recipient_name | string | Recipient's name (as it appears on LinkedIn) |
| message | string | Message text to send |

---

## Workflow

### Step 1: Create Approval Request
```
[SKILL] Using skill: /send-linkedin-message
[WRITE] Creating approval request in /Pending_Approval/linkedin/
[DONE] Awaiting human approval before sending
```

### Step 2: Wait for Human Approval
Human reviews and moves file to /Approved/linkedin/

### Step 3: Execute Approved Message
```
[READ] Reading approved message content
[INFO] Recipient: {name}
[INFO] Message: {first 50 chars}...
[MCP] Calling mcp__ai-employee__send_linkedin_message(recipient_name, message)
[DONE] LinkedIn message sent successfully to {recipient_name}
```

---

## Example Usage

### Example 1: New Connection Follow-up

**User:** Send a follow-up message to John Smith on LinkedIn

**AI:**
```
[SKILL] Using skill: /send-linkedin-message
[WRITE] Creating approval request in /Pending_Approval/linkedin/

## Proposed LinkedIn Message

**Recipient:** John Smith
**Message:**
Hi John,

Thanks for connecting! I noticed we're both in the [industry] space. I'd love to learn more about your work at [company] and explore potential synergies.

Would you be open to a quick 15-minute call next week?

Best regards,
[Your name]

---
To approve: Move this file to /Approved/linkedin/
```

**Human:** Moves file to /Approved/linkedin/

**AI (triggered by orchestrator):**
```
[READ] Reading approved message content
[MCP] Calling mcp__ai-employee__send_linkedin_message(recipient_name="John Smith", message="Hi John, Thanks for connecting!...")
[DONE] LinkedIn message sent successfully to John Smith
```

---

## Message Templates

### Template 1: New Connection Follow-up
```
Hi {name},

Thanks for connecting! I noticed we're both in the {industry} space. I'd love to learn more about your work at {company} and explore potential synergies.

Would you be open to a quick 15-minute call next week?

Best regards,
{your_name}
```

### Template 2: Responding to Inquiry
```
Hi {name},

Thank you for reaching out regarding {topic}. I'd be happy to help!

{brief_response}

Would you prefer to continue this conversation via email or schedule a quick call?

Looking forward to hearing from you.

Best,
{your_name}
```

### Template 3: Meeting Request
```
Hi {name},

I hope this message finds you well. I'm reaching out because {reason}.

I believe a brief conversation could be mutually beneficial. Would you have 15-20 minutes for a call sometime next week?

Here are a few time slots that work for me:
- {option_1}
- {option_2}
- {option_3}

Let me know what works best for you!

Best regards,
{your_name}
```

### Template 4: Thank You Message
```
Hi {name},

I wanted to extend a personal thank you for {specific_action}. I truly appreciate {specific_reason}.

Looking forward to staying connected and potentially collaborating in the future.

Best regards,
{your_name}
```

---

## Best Practices

### Message Guidelines
1. **Keep it concise** - 100-300 characters ideal
2. **Personalize** - Reference something specific about them
3. **Clear call-to-action** - What do you want next?
4. **Professional tone** - Friendly but professional
5. **Proofread** - Check for typos before sending

### Connection Request Limits
- LinkedIn limits: 100 connection requests per week
- Don't send identical messages (spam detection)
- Personalize each message

### Response Time
- Aim to respond within 24-48 hours
- Follow up once if no response (wait 1 week)

---

## Safety Rules

1. **ALWAYS require approval** - No automatic messaging
2. **Personalize messages** - Avoid generic templates
3. **Respect LinkedIn limits** - Don't spam
4. **Professional tone** - Maintain brand image
5. **Check DRY_RUN mode** - Don't send real messages when testing

---

## Prerequisites

Before using this skill:
1. LinkedIn session must be set up:
   ```bash
   python -m watchers --watcher linkedin --setup
   ```
2. Browser must be logged into LinkedIn
3. Session data saved in `sessions/linkedin/`

---

## Error Handling

| Error | Action |
|-------|--------|
| LinkedIn session not found | Report error, suggest running setup |
| Contact not found | Report error, verify exact name on LinkedIn |
| Not logged in | Report error, suggest re-running setup |
| Message too long | Truncate message, warn user |
| Approval required | Create approval request (always required) |
| MCP tool failure | Log error, move to /Done/ with error notes |

---

## Completion Checklist

- [ ] Created approval request (always required)
- [ ] Human approved the message
- [ ] Verified recipient name (exact LinkedIn name)
- [ ] Checked message content
- [ ] Checked DRY_RUN mode
- [ ] Called MCP tool: mcp__ai-employee__send_linkedin_message
- [ ] Logged result (success or error)
- [ ] Updated action file status
