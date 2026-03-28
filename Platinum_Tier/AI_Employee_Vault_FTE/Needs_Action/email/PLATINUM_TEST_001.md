---
type: email
from: platinum-test@example.com
subject: PLATINUM TIER TEST - Email Handoff
received: 2026-03-25T14:00:00Z
priority: high
status: pending
---

## Email Content

This is a **Platinum Tier test email** to verify the Cloud → Local handoff workflow.

**Test Scenario:**
1. Cloud Agent should detect this email
2. Cloud Agent should create draft reply (draft_only mode)
3. Cloud Agent should write to /Updates/ folder
4. Local Agent should detect update
5. Local Agent should create approval request
6. Human approves (move to /Approved/)
7. Local Agent executes (sends real email)
8. Local Agent moves to /Done/

## Suggested Actions

- [ ] Draft reply (Cloud Agent - draft_only mode)
- [ ] Approve draft (Human)
- [ ] Send reply (Local Agent - full mode)
- [ ] Move to /Done/ (Local Agent)

---

**Test ID:** PLATINUM_TEST_001  
**Created:** Week 4 - Platinum Demo
