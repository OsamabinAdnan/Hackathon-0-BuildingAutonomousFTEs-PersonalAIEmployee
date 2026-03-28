# Bronze Tier: Foundation - Personal AI Employee

## Overview

**Tagline:** *Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.*

Bronze Tier is the **minimum viable deliverable** for the Personal AI Employee hackathon. It establishes the foundational architecture with proper Human-in-the-Loop (HITL) workflow.

**Estimated Time:** 8-12 hours

---

## Bronze Tier Requirements

| # | Requirement | Status |
|---|-------------|--------|
| 1 | Obsidian vault with Dashboard.md and Company_Handbook.md | Done |
| 2 | One working Watcher script (FileSystem monitoring /Inbox) | Done |
| 3 | Claude Code reading from and writing to the vault | Done |
| 4 | Folder structure with HITL workflow | Done |
| 5 | All AI functionality implemented as Agent Skills | Done |

---

## Architecture

```
/Inbox --> Watcher --> /Needs_Action + /Archive
                           |
                           v
                    Orchestrator monitors:
                    - /Needs_Action (new tasks)
                    - /Approved (human approved)
                    - /Rejected (human rejected)
                           |
                           v
                    Claude Code processes
                           |
              +------------+------------+
              |                         |
         Routine?                  Sensitive?
              |                         |
              v                         v
           /Done              /Pending_Approval
                                        |
                                        v
                                  Human Reviews
                                        |
                        +---------------+---------------+
                        |                               |
                        v                               v
                   /Approved                      /Rejected
                        |                               |
                        v                               v
                 Claude Executes              Archived/Logged
                        |
                        v
                     /Done
```

---

## Project Structure

```
Bronze_Tier/
├── AI_Employee_Vault_FTE/      # Obsidian vault
│   ├── Dashboard.md            # Real-time system summary
│   ├── Company_Handbook.md     # Rules of Engagement
│   ├── Inbox/                  # Drop files here
│   ├── Archive/                # Original files stored
│   ├── Needs_Action/           # Action files waiting
│   ├── In_Progress/            # Files being processed
│   ├── Plans/                  # Plan.md files
│   ├── Pending_Approval/       # Items needing approval
│   ├── Approved/               # Human approved
│   ├── Rejected/               # Human rejected
│   └── Done/                   # Completed tasks
│
├── orchestrator/               # Main controller
├── watchers/                   # Perception layer
├── .claude/skills/             # Agent skills
├── pyproject.toml
├── README.md
└── CLAUDE.md
```

---

## Vault Folders

| Folder | Purpose | Who Writes |
|--------|---------|------------|
| `/Inbox` | Drop files here to trigger processing | USER |
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
2. Watcher creates action --> /Needs_Action
   Watcher moves original --> /Archive
3. Orchestrator detects /Needs_Action --> Triggers Claude
4. Claude claims file --> /In_Progress
5. Claude creates Plan.md --> /Plans
6. Claude determines: Routine action
7. Claude executes action
8. Claude moves to /Done
9. Claude updates Dashboard.md
```

### HITL Flow (Requires Approval)
```
1-5. Same as above
6. Claude determines: Sensitive action
7. Claude creates approval request --> /Pending_Approval
8. Human reviews /Pending_Approval:
   - APPROVE: Move to /Approved
   - REJECT: Move to /Rejected
9. Orchestrator detects /Approved --> Triggers Claude
10. Claude reads approval request + Plan.md
11. Claude executes approved action
12. Claude moves to /Done
13. Claude updates Dashboard.md
```

---

## Agent Skills

### `/process-inbox`
Process all files in `/Needs_Action`:
1. Move to `/In_Progress` (claim ownership)
2. Create Plan.md in `/Plans`
3. Read original from `/Archive`
4. Determine if routine or sensitive:
   - Routine: Execute, move to `/Done`
   - Sensitive: Create approval request, move to `/Pending_Approval`

### `/update-dashboard`
Update `Dashboard.md`:
- Count items in all folders
- Update tables (Pending, In Progress, Approval, Approved)
- Update statistics

---

## Quick Start

```bash
# 1. Install dependencies
cd Bronze_Tier
uv sync

# 2. Start orchestrator
uv run python -m orchestrator

# 3. Drop file in /Inbox
cp some_file.txt AI_Employee_Vault_FTE/Inbox/

# 4. For sensitive items, review /Pending_Approval
#    Approve: Move to /Approved
#    Reject: Move to /Rejected
```

---

## CLI Commands

| Command | Description |
|---------|-------------|
| `python -m orchestrator` | Full autonomous mode |
| `python -m watchers` | Watcher only (manual Claude) |
| `python -m orchestrator --status` | Show system status |

---

## HITL Rules

### For Claude
- Routine actions: Execute directly
- Sensitive actions: Flag for approval in `/Pending_Approval`
- Wait for human to move to `/Approved`
- Never execute sensitive actions without approval

### For Humans
- Review files in `/Pending_Approval`
- Check corresponding Plan.md in `/Plans`
- **Approve:** Move to `/Approved` (orchestrator will trigger execution)
- **Reject:** Move to `/Rejected` (will be archived)
- **Never** move directly from `/Pending_Approval` to `/Done`

---

## Next Steps

- **Silver Tier:** Add Gmail/WhatsApp watchers, MCP servers
- **Gold Tier:** Odoo integration, CEO Briefing, Ralph Wiggum loop
- **Platinum Tier:** Cloud deployment, work-zone specialization
