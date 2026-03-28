# HITL Workflow Fixes - Session Summary

**Date:** 2026-03-03
**Status:** ✅ COMPLETE

---

## Issues Found & Fixed

### Issue 1: Approval Files Not in Category Subfolders ❌ → ✅
**Problem:** Claude was creating approval files in `/Pending_Approval/APPROVAL_{filename}.md` instead of `/Pending_Approval/email/APPROVAL_{filename}.md`

**Impact:** Orchestrator couldn't detect approved files because it looks in category subfolders

**Fix:** Updated `process-inbox/SKILL.md` to explicitly require category subfolders:
```
/Pending_Approval/email/APPROVAL_{filename}.md
/Pending_Approval/whatsapp/APPROVAL_{filename}.md
/Pending_Approval/linkedin/APPROVAL_{filename}.md
/Pending_Approval/files/APPROVAL_{filename}.md
```

---

### Issue 2: Dashboard Showing UTC Time Instead of Local Time ❌ → ✅
**Problem:** Dashboard showed `2026-03-03 18:23:05` (UTC) instead of local time `2026-03-03 23:29:38`

**Impact:** Timestamps were 5 hours off, confusing for audit trails

**Fix:** Updated `update-dashboard/SKILL.md` with explicit local time instructions:
- NEVER use ISO 8601 format with Z suffix
- NEVER use `datetime.utcnow()`
- ALWAYS use `datetime.now()` for local system time
- Format: `YYYY-MM-DD HH:MM:SS` (24-hour local time)

---

### Issue 3: Original File Moving to Wrong Location ❌ → ✅
**Problem:** Claude was moving original file from `/In_Progress/<category>/` to `/Pending_Approval/<category>/` when flagging for approval

**Impact:** File workflow was broken - original file shouldn't move until approval decision

**Fix:** Updated `process-inbox/SKILL.md` with correct workflow:

#### Initial Processing (When Flagging for Approval):
```
/Needs_Action/<category>/{filename}
    ↓ [MOVE - CLAIM]
/In_Progress/<category>/{filename} ← STAYS HERE (locked)
    ↓ [CREATE]
/Pending_Approval/<category>/APPROVAL_{filename}.md ← NEW approval request
    ↓ [CREATE]
/Plans/<category>/PLAN_{filename}.md ← NEW plan document
```

#### After Human Approval:
```
/In_Progress/<category>/{filename}
    ↓ [EXECUTE ACTION]
    ↓ [MOVE]
/Archive/<category>/{filename} ← Original file archived

/Approved/<category>/APPROVAL_{filename}.md
    ↓ [MOVE]
/Done/<category>/APPROVAL_{filename}.md ← Audit trail
```

#### After Human Rejection:
```
/In_Progress/<category>/{filename}
    ↓ [MOVE - NO EXECUTION]
/Archive/<category>/{filename} ← Original file archived

/Rejected/<category>/APPROVAL_{filename}.md
    ↓ [RENAME]
/Rejected/<category>/REJECTED_APPROVAL_{filename}.md ← Stays in Rejected (audit trail)
```

---

## Complete HITL Workflow (Corrected)

### Phase 1: Initial Processing (Claude)
1. Claude reads action file from `/Needs_Action/<category>/`
2. Claude moves to `/In_Progress/<category>/` (CLAIM - lock it)
3. Claude creates `Plan.md` in `/Plans/<category>/`
4. Claude creates `APPROVAL_{filename}.md` in `/Pending_Approval/<category>/`
5. **Claude KEEPS original in `/In_Progress/<category>/` (DO NOT MOVE)**
6. Claude outputs: `[DONE] Flagged for approval: {reason}`

**File State:**
- `/Needs_Action/<category>/` → EMPTY
- `/In_Progress/<category>/{filename}` → LOCKED
- `/Plans/<category>/PLAN_{filename}.md` → Created
- `/Pending_Approval/<category>/APPROVAL_{filename}.md` → Created

### Phase 2: Human Review
1. Human opens `/Pending_Approval/<category>/`
2. Human reads `APPROVAL_{filename}.md`
3. Human checks `Plan.md` in `/Plans/<category>/`
4. Human decides:
   - **APPROVE:** Move `APPROVAL_{filename}.md` to `/Approved/<category>/`
   - **REJECT:** Move `APPROVAL_{filename}.md` to `/Rejected/<category>/`

### Phase 3A: Orchestrator Detects Approval
1. Orchestrator detects file in `/Approved/<category>/`
2. Triggers Claude with approved action
3. Claude reads approval request + Plan.md
4. Claude executes action via MCP tool
5. Claude moves original from `/In_Progress/<category>/` to `/Archive/<category>/`
6. Claude moves approval from `/Approved/<category>/` to `/Done/<category>/`
7. Claude updates Dashboard.md

**Final State (Approved):**
- `/Archive/<category>/{filename}` → Original (completed)
- `/Done/<category>/APPROVAL_{filename}.md` → Audit trail

### Phase 3B: Orchestrator Detects Rejection
1. Orchestrator detects file in `/Rejected/<category>/`
2. Logs rejection with reason
3. Renames: `APPROVAL_{filename}.md` → `REJECTED_APPROVAL_{filename}.md`
4. Keeps file in `/Rejected/<category>/` (audit trail)
5. Moves original from `/In_Progress/<category>/` to `/Archive/<category>/`
6. Updates Dashboard.md

**Final State (Rejected):**
- `/Archive/<category>/{filename}` → Original (cancelled)
- `/Rejected/<category>/REJECTED_APPROVAL_{filename}.md` → Audit trail

---

## Critical Rules

✅ **Original file ALWAYS moves to `/Archive/<category>/` in both cases (Approved OR Rejected)**

✅ **Original file NEVER moves to `/Pending_Approval/` or `/Approved/` or `/Rejected/`**

✅ **Only the APPROVAL REQUEST file moves between folders**

✅ **Approval files must be in category subfolders: `/Pending_Approval/email/`, `/Approved/whatsapp/`, etc.**

✅ **Dashboard timestamps must use LOCAL system time, never UTC**

✅ **Rejected approval files get `REJECTED_` prefix and stay in `/Rejected/<category>/`**

---

## Files Modified

1. **`.claude/skills/process-inbox/SKILL.md`**
   - Fixed file movement logic (lines 78-103)
   - Updated HITL Flow section (lines 272-338)
   - Added critical rules (lines 333-338)

2. **`.claude/skills/update-dashboard/SKILL.md`**
   - Enhanced local time instructions (lines 303-313)
   - Added explicit warnings against UTC timestamps

---

## Test Case Created

**File:** `/Needs_Action/email/EMAIL_20260303_182938_hitl_fix_test.md`

**Expected Behavior:**
1. ✅ Approval file created in `/Pending_Approval/email/` (with category subfolder)
2. ✅ Original file stays in `/In_Progress/email/` (locked)
3. ✅ Plan.md created in `/Plans/email/`
4. ✅ Dashboard updates with LOCAL time (not UTC)
5. ✅ When approved, original moves to `/Archive/email/`
6. ✅ When rejected, approval file renamed to `REJECTED_APPROVAL_*` and stays in `/Rejected/email/`

---

## Next Steps

Run the orchestrator with the test file:

```bash
cd "E:\Hackathon-0-Personal-FTE\Silver_Tier"
uv run python -m orchestrator
```

**Verify:**
1. Approval file appears in `/Pending_Approval/email/` (correct location)
2. Original file stays in `/In_Progress/email/` (not moved)
3. Dashboard shows local time (not UTC)
4. Move approval to `/Approved/email/` and verify execution
5. Check that original moves to `/Archive/email/` after approval

---

**Status:** ✅ All fixes applied and documented
