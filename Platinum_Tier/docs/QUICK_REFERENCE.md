# HITL Workflow - Quick Reference Guide

**Last Updated:** 2026-03-03
**Status:** ✅ All Fixes Applied

---

## File Movement Rules (CRITICAL)

### When Flagging for Approval
```
/Needs_Action/email/{filename}
    ↓ MOVE
/In_Progress/email/{filename} ← STAYS HERE (LOCKED)

/Pending_Approval/email/APPROVAL_{filename} ← NEW FILE (for human)
/Plans/email/PLAN_{filename} ← NEW FILE (for human)
```

### When Approved
```
/In_Progress/email/{filename}
    ↓ MOVE (after executing action)
/Archive/email/{filename} ← COMPLETED

/Approved/email/APPROVAL_{filename}
    ↓ MOVE
/Done/email/APPROVAL_{filename} ← AUDIT TRAIL
```

### When Rejected
```
/In_Progress/email/{filename}
    ↓ MOVE (no execution)
/Archive/email/{filename} ← CANCELLED

/Rejected/email/APPROVAL_{filename}
    ↓ RENAME
/Rejected/email/REJECTED_APPROVAL_{filename} ← STAYS HERE (AUDIT TRAIL)
```

---

## Folder Structure (Correct)

```
✅ CORRECT:
/Pending_Approval/email/APPROVAL_EMAIL_*.md
/Pending_Approval/whatsapp/APPROVAL_WHATSAPP_*.md
/Pending_Approval/linkedin/APPROVAL_LINKEDIN_*.md
/Pending_Approval/files/APPROVAL_FILE_*.md

❌ WRONG:
/Pending_Approval/APPROVAL_EMAIL_*.md (no category subfolder)
```

---

## Dashboard Timestamps

```
✅ CORRECT (Local Time):
Last Sync: 2026-03-03 23:49:26

❌ WRONG (UTC Time):
Last Sync: 2026-03-03T18:49:26Z
Last Sync: 2026-03-03 18:49:26
```

---

## Original File Rules

| Scenario | Original File Location |
|----------|------------------------|
| Initial Processing | `/In_Progress/<category>/` (STAYS) |
| After Approval | `/Archive/<category>/` (MOVED) |
| After Rejection | `/Archive/<category>/` (MOVED) |
| Never | `/Pending_Approval/`, `/Approved/`, `/Rejected/` |

---

## Approval File Rules

| Scenario | Approval File Location | Filename |
|----------|------------------------|----------|
| Initial Processing | `/Pending_Approval/<category>/` | `APPROVAL_{filename}` |
| After Approval | `/Done/<category>/` | `APPROVAL_{filename}` |
| After Rejection | `/Rejected/<category>/` | `REJECTED_APPROVAL_{filename}` |

---

## Test Command

```bash
cd "E:\Hackathon-0-Personal-FTE\Silver_Tier"
uv run python -m orchestrator
```

---

## Verification Checklist

- [ ] Approval file in `/Pending_Approval/email/` (with category subfolder)
- [ ] Original file stays in `/In_Progress/email/` (not moved)
- [ ] Plan file created in `/Plans/email/`
- [ ] Dashboard shows local time (not UTC)
- [ ] After approval: original moves to `/Archive/email/`
- [ ] After rejection: approval renamed to `REJECTED_APPROVAL_*`

---

**Ready to test! Run orchestrator and verify the workflow.**
