---
name: post-linkedin
description: |
  Post a text update to LinkedIn using the LinkedIn API.
  Use this skill for business updates, announcements, and content sharing.
  All LinkedIn posts require human approval before posting.
---

# Post LinkedIn Skill

Post a text update to LinkedIn using the LinkedIn API.

---

## IMPORTANT: Output Action Tags

**Always print action tags during execution:**

```
[SKILL] Using skill: /post-linkedin
[READ] Reading post content
[MCP] Calling mcp__ai-employee__post_linkedin
[DONE] LinkedIn post created: {post_id}
```

---

## When to Use

Use this skill when:
- Business announcement needs to be shared
- Project milestone completed
- New service/product launch
- Company update or news
- Thought leadership content
- Engagement with industry trends

**ALWAYS require approval before posting:**
- All LinkedIn posts require human approval
- This ensures brand voice consistency
- Prevents accidental inappropriate posts

---

## MCP Tool

This skill uses the MCP tool:
```
mcp__ai-employee__post_linkedin(text, visibility)
```

---

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| text | string | Post content (max 3000 characters) |
| visibility | string | Post visibility: PUBLIC, CONNECTIONS, or CONTACTS (default: PUBLIC) |

---

## Workflow

### Step 1: Create Approval Request
```
[SKILL] Using skill: /post-linkedin
[WRITE] Creating approval request in /Pending_Approval/linkedin/
[DONE] Awaiting human approval before posting
```

### Step 2: Wait for Human Approval
Human reviews and moves file to /Approved/linkedin/

### Step 3: Execute Approved Post
```
[READ] Reading approved post content
[INFO] Post text: {first 100 chars}...
[INFO] Visibility: PUBLIC
[MCP] Calling mcp__ai-employee__post_linkedin(text, visibility="PUBLIC")
[DONE] LinkedIn post created successfully! Post ID: {post_id}
```

---

## Example Usage

### Example: Business Update Post

**User:** Create a LinkedIn post about completing a project

**AI:**
```
[SKILL] Using skill: /post-linkedin
[WRITE] Creating approval request in /Pending_Approval/linkedin/

## Proposed LinkedIn Post

**Content:**
🎉 Project Milestone Achieved! 

We're excited to announce the successful completion of [Project Name] for our valued client. This marks another step forward in our commitment to delivering excellence.

#ProjectManagement #Success #BusinessGrowth

**Visibility:** PUBLIC

---
To approve: Move this file to /Approved/linkedin/
```

**Human:** Moves file to /Approved/linkedin/

**AI (triggered by orchestrator):**
```
[READ] Reading approved post content
[MCP] Calling mcp__ai-employee__post_linkedin(text="🎉 Project Milestone Achieved!...", visibility="PUBLIC")
[DONE] LinkedIn post created successfully! Post ID: urn:li:ugcPost:1234567890

View your post at: https://www.linkedin.com/feed/
```

---

## Post Templates

### Template 1: Project Completion
```
🎉 Project Milestone Achieved!

We're excited to announce the successful completion of [Project Name] for our valued client. This marks another step forward in our commitment to delivering excellence.

Thank you to our amazing team for their dedication and hard work!

#ProjectManagement #Success #BusinessGrowth
```

### Template 2: New Service Launch
```
🚀 Exciting News!

We're thrilled to launch our new [Service/Product Name] designed to help businesses [key benefit].

Key features:
✅ Feature 1
✅ Feature 2
✅ Feature 3

Ready to [achieve outcome]? Let's connect!

#Innovation #NewLaunch #Business
```

### Template 3: Thought Leadership
```
💡 Industry Insight:

[Share relevant industry trend or insight]

Key takeaways:
1. Point 1
2. Point 2
3. Point 3

What's your experience with [topic]? Share your thoughts below!

#ThoughtLeadership #Industry #Insights
```

### Template 4: Client Success
```
⭐ Client Success Story!

Helped [client type] achieve [specific result] through [solution provided].

Results:
📈 [Metric 1]
📈 [Metric 2]
📈 [Metric 3]

Ready to achieve similar results? Let's talk!

#ClientSuccess #Results #Business
```

---

## Best Practices

### Content Guidelines
1. **Keep it professional** - Maintain brand voice
2. **Use emojis sparingly** - 1-3 relevant emojis max
3. **Include hashtags** - 3-5 relevant hashtags
4. **Add call-to-action** - Encourage engagement
5. **Character limit** - Max 3000 characters (LinkedIn limit)

### Posting Frequency
- Recommended: 2-3 posts per week
- Avoid: Multiple posts per day
- Best times: Tuesday-Thursday, 9-11 AM

### Visibility Options
- **PUBLIC**: Anyone can see (recommended for business content)
- **CONNECTIONS**: Only connections can see
- **CONTACTS**: Only 1st-degree connections can see

---

## Safety Rules

1. **ALWAYS require approval** - No automatic posting
2. **Review content carefully** - Check for typos and accuracy
3. **Respect character limit** - Max 3000 characters
4. **Use appropriate hashtags** - Relevant to content
5. **Check DRY_RUN mode** - Don't post real content when testing

---

## Prerequisites

Before using this skill:
1. LinkedIn API access token must be configured in `.env`:
   ```
   LINKEDIN_ACCESS_TOKEN=your_token_here
   ```
2. Token must have `w_member_social` permission

---

## Error Handling

| Error | Action |
|-------|--------|
| Access token not configured | Report error, ask to set LINKEDIN_ACCESS_TOKEN |
| Invalid token/permissions | Report error, suggest regenerating token |
| Content too long | Truncate to 3000 characters, warn user |
| API rate limit | Report error, suggest waiting before retry |
| Approval required | Create approval request (always required) |

---

## Completion Checklist

- [ ] Created approval request (always required)
- [ ] Human approved the post
- [ ] Verified post content (max 3000 chars)
- [ ] Checked visibility setting
- [ ] Checked DRY_RUN mode
- [ ] Called MCP tool: mcp__ai-employee__post_linkedin
- [ ] Logged result with post ID
- [ ] Provided LinkedIn URL for viewing
