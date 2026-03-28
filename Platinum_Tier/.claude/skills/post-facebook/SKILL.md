---
name: post-facebook
description: Post updates to Facebook business page. Use for business announcements, sales posts, company updates, event promotions, or when asked to share content on Facebook.
---

# Post to Facebook - Gold Tier

Post content to Facebook Page via MCP server.

---

## When to Use

Use this skill when:
- User requests Facebook post
- Sharing business announcement
- Promoting sales or offers
- Posting company updates
- Scheduled social media posting

---

## Instructions

### Step 1: Gather Post Details

Collect the following information:
- **Message content** (text to post)
- **Image URL** (optional)
- **Link URL** (optional)

### Step 2: Check DRY_RUN Mode

Before posting:
- If `DRY_RUN=true`: Log what would be posted, don't create real post
- If `DRY_RUN=false`: Proceed with posting

### Step 3: Post via MCP

Use the MCP tool to post:

```
mcp__ai-employee__post_facebook(
    message="Your post content here",
    image_url="https://example.com/image.jpg",  # optional
    link="https://example.com"  # optional
)
```

### Step 4: Log the Action

Print action tags for logging:
```
[SKILL] Using skill: /post-facebook
[MCP] Calling mcp__ai-employee__post_facebook
[DONE] Facebook post created: POST_ID
```

### Step 5: Record in Vault

1. Save post record to `/Done/facebook/`
2. Update Dashboard.md via /update-dashboard skill

---

## Examples

### Example 1: Simple Post

**User:** Post on Facebook: "Excited to announce our new AI Employee service!"

**AI:**
```
[SKILL] Using skill: /post-facebook
[INFO] Posting to Facebook: "Excited to announce..."
[MCP] Calling mcp__ai-employee__post_facebook(message="Excited to announce our new AI Employee service!")
[DONE] Facebook post created: 969310802941448_122101875009207806
```

### Example 2: Business Announcement

**User:** Create Facebook post about our 20% off sale

**AI:**
```
[SKILL] Using skill: /post-facebook
[WRITE] Creating post content
[INFO] Posting sale announcement
[MCP] Calling mcp__ai-employee__post_facebook(message="🎉 20% OFF SALE! Get 20% off all services this week. Use code SAVE20. Offer ends Friday!")
[DONE] Facebook post created: 969310802941448_122101875009207807
[WRITE] Saving to /Done/facebook/POST_20260309.md
```

### Example 3: Dry Run Mode

**If DRY_RUN=true:**
```
[SKILL] Using skill: /post-facebook
[DRY RUN] Would post to Facebook: "Excited to announce..."
[DRY RUN] Page ID: 969310802941448
[DONE] Dry run complete - no real post created
```

---

## MCP Tool Reference

| Tool | Parameters | Returns |
|------|------------|---------|
| `mcp__ai-employee__post_facebook` | message (str), image_url (str, optional), link (str, optional) | Post ID, success status |

---

## Post Templates

### Template 1: Business Update
```
📢 Business Update

{Update content}

Key points:
- Point 1
- Point 2
- Point 3

#BusinessUpdate #CompanyName
```

### Template 2: Sales Post
```
🎉 Special Offer!

{Offer details}

Use code: {CODE}
Valid until: {DATE}

#Sale #Discount #SpecialOffer
```

### Template 3: Announcement
```
🚀 Exciting News!

{Announcement content}

Learn more: {LINK}

#Announcement #News
```

---

## Error Handling

| Error | Action |
|-------|--------|
| Invalid token | Report error, suggest regenerating Facebook token |
| Page not found | Verify PAGE_ID in .env |
| Permission denied | Check app permissions in Facebook Developer |
| DRY_RUN mode | Log what would be posted, don't create post |

---

## Related Skills

- `/send-facebook-message` - Send direct message (different from post)
- `/post-linkedin` - Post to LinkedIn instead
- `/generate-briefing` - Include Facebook metrics in briefing
- `/update-dashboard` - Show Facebook activity on dashboard

---

## Completion Checklist

- [ ] Gathered post content
- [ ] Checked DRY_RUN mode
- [ ] Called MCP tool: mcp__ai-employee__post_facebook
- [ ] Logged result with post ID
- [ ] Saved post record to vault
- [ ] Updated Dashboard.md
