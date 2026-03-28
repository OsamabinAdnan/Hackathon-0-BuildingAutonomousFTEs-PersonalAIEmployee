---
name: send-facebook-message
description: Send direct messages (DMs) via Facebook Messenger. Use when replying to customer inquiries, sending personalized messages, or following up with leads via Facebook Messenger.
---

# Send Facebook Message - Gold Tier

Send direct messages to Facebook users via Messenger.

---

## When to Use

Use this skill when:
- Replying to Facebook message inquiries
- Sending personalized follow-ups to leads
- Customer support via Messenger
- Direct outreach to specific users
- Responding to comments with private message

---

## Instructions

### Step 1: Gather Message Details

Collect the following information:
- **Recipient ID** (Facebook user ID or page-scoped ID)
- **Message content** (text to send)

### Step 2: Check DRY_RUN Mode

Before sending:
- If `DRY_RUN=true`: Log what would be sent, don't send real message
- If `DRY_RUN=false`: Proceed with sending

### Step 3: Send Message via MCP

Use the MCP tool to send:

```
mcp__ai-employee__send_facebook_message(
    recipient_id="1234567890",
    message="Your message content here"
)
```

### Step 4: Log the Action

Print action tags for logging:
```
[SKILL] Using skill: /send-facebook-message
[MCP] Calling mcp__ai-employee__send_facebook_message
[DONE] Facebook message sent to: {recipient_id}
```

### Step 5: Record in Vault

1. Save message record to `/Done/facebook-messages/`
2. Update Dashboard.md via /update-dashboard skill

---

## Examples

### Example 1: Reply to Customer Inquiry

**User:** Send Facebook message to user 1234567890: "Thanks for your interest! Our team will contact you soon."

**AI:**
```
[SKILL] Using skill: /send-facebook-message
[INFO] Sending message to: 1234567890
[MCP] Calling mcp__ai-employee__send_facebook_message(recipient_id="1234567890", message="Thanks for your interest! Our team will contact you soon.")
[DONE] Facebook message sent to: 1234567890
```

### Example 2: Follow-up with Lead

**User:** Follow up with Facebook lead about our AI Employee service

**AI:**
```
[SKILL] Using skill: /send-facebook-message
[WRITE] Creating follow-up message
[INFO] Sending follow-up to lead
[MCP] Calling mcp__ai-employee__send_facebook_message(
    recipient_id="9876543210",
    message="Hi! Thanks for your interest in our AI Employee service. Would you like to schedule a demo call this week?"
)
[DONE] Facebook message sent successfully
[WRITE] Saving to /Done/facebook-messages/FB_MSG_20260309.md
```

### Example 3: Dry Run Mode

**If DRY_RUN=true:**
```
[SKILL] Using skill: /send-facebook-message
[DRY RUN] Would send Facebook message to: 1234567890
[DRY RUN] Message: "Thanks for your interest!"
[DONE] Dry run complete - no real message sent
```

---

## MCP Tool Reference

| Tool | Parameters | Returns |
|------|------------|---------|
| `mcp__ai-employee__send_facebook_message` | recipient_id (str), message (str) | Message ID, success status |

---

## Message Templates

### Template 1: Customer Support Reply
```
Hi {Name},

Thanks for reaching out! {Response to their question}

Best regards,
{Your Company}
```

### Template 2: Lead Follow-up
```
Hi {Name},

Thanks for your interest in {Product/Service}!

{Brief value proposition}

Would you like to schedule a call to learn more?

Best,
{Your Name}
```

### Template 3: Appointment Reminder
```
Hi {Name},

This is a friendly reminder about your appointment on {Date} at {Time}.

See you soon!
{Your Company}
```

---

## Error Handling

| Error | Action |
|-------|--------|
| Invalid recipient ID | Verify user ID, ask for correct ID |
| Message too long | Truncate to Facebook limit (640 chars) |
| User can't receive messages | Report error, user has DMs disabled |
| Invalid token | Report error, suggest regenerating Facebook token |
| DRY_RUN mode | Log what would be sent, don't send message |

---

## Related Skills

- `/post-facebook` - Post to Facebook Page (public posts)
- `/send-whatsapp` - Send WhatsApp message instead
- `/send-email` - Send email instead
- `/send-linkedin-message` - Send LinkedIn message instead

---

## Completion Checklist

- [ ] Gathered recipient ID and message content
- [ ] Checked DRY_RUN mode
- [ ] Called MCP tool: mcp__ai-employee__send_facebook_message
- [ ] Logged result with message ID
- [ ] Saved message record to vault
- [ ] Updated Dashboard.md

---

## Privacy & Compliance Notes

⚠️ **Important:**
- Only send messages to users who have contacted you first
- Respect Facebook's messaging policies
- Don't send unsolicited promotional messages
- Include opt-out option in promotional messages
- Keep message records for compliance

---

*This Skill enables direct customer communication via Facebook Messenger.*
