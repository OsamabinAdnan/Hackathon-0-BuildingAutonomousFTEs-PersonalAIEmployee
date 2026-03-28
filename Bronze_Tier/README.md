# Personal AI Employee - Bronze Tier

**Tagline:** *Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.*

Bronze Tier is the **minimum viable deliverable** for the Personal AI Employee hackathon. It establishes the foundational architecture for an autonomous AI assistant with proper Human-in-the-Loop (HITL) workflow.

---

## Features

- **Obsidian Vault** - Local knowledge base with Dashboard and Company Handbook
- **FileSystem Watcher** - Monitors `/Inbox` folder for new files
- **Auto-Archive** - Moves processed files to `/Archive` to prevent re-detection
- **Orchestrator** - Monitors multiple folders and triggers Claude Code
- **Human-in-the-Loop (HITL)** - Proper approval workflow with `/Approved` and `/Rejected`
- **Agent Skills** - `process-inbox` and `update-dashboard` skills with real-time action tags
- **Color-Coded Logging** - Component-specific colors (Blue: Orchestrator, Yellow: Watcher, Cyan: Claude)
- **Local Time Sync** - Dashboard updates automatically using local system time
- **Clean Rejection** - Deletes action files on rejection while preserving audit trail in `/Rejected`

---

## Architecture

```
USER drops file
       |
       v
    /Inbox/
       |
       v
+---------------------------+
| FileSystem Watcher        |
+---------------------------+
       |
       +---> /Needs_Action/ (action files)
       +---> /Archive/       (original files)
       |
       v
+---------------------------+
| Orchestrator              |
| Monitors:                 |
| - /Needs_Action           |
| - /Approved               |
| - /Rejected               |
+---------------------------+
       |
       v
+---------------------------+
| Claude Code               |
+---------------------------+
       |
       +---> Routine? --> /Done
       |
       +---> Sensitive? --> /Pending_Approval
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
      Claude Executes                 Archived/Logged
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
│   ├── __init__.py
│   ├── __main__.py
│   └── main.py
│
├── watchers/                   # Perception layer
│   ├── __init__.py
│   ├── __main__.py
│   ├── base_watcher.py
│   └── filesystem_watcher.py
│
├── .claude/
│   └── skills/
│       ├── process-inbox/
│       └── update-dashboard/
│
├── pyproject.toml
└── README.md
```

---

## Vault Folders

| Folder | Purpose | Who Writes |
|--------|---------|------------|
| `/Inbox` | Drop files here | USER |
| `/Archive` | Original files stored | Watcher |
| `/Needs_Action` | Action files waiting | Watcher |
| `/In_Progress` | Files being processed | Claude |
| `/Plans` | Plan.md files | Claude |
| `/Pending_Approval` | Items needing approval | Claude |
| `/Approved` | Human approved | USER |
| `/Rejected` | Human rejected | USER |
| `/Done` | Completed tasks | Claude |

---

## Workflow

### Standard Flow (Auto-Approved)
```
1. USER drops file --> /Inbox
2. Watcher --> /Needs_Action + /Archive
3. Orchestrator triggers Claude
4. Claude claims --> /In_Progress
5. Claude plans --> /Plans
6. Claude executes (routine)
7. Claude --> /Done
```

### HITL Flow (Requires Approval)
```
1-5. Same as above
6. Claude flags sensitive --> /Pending_Approval
7. Human reviews:
   - APPROVE: Move to /Approved
   - REJECT: Move to /Rejected
8a. If Approved: Orchestrator detects /Approved --> Claude executes --> /Done
8b. If Rejected: Orchestrator deletes action file, adds REJECTED_ prefix, keeps in /Rejected
```

---

## Quick Start

### 1. Install Dependencies

```bash
cd Bronze_Tier
uv sync
```

### 2. Open Obsidian Vault

1. Open Obsidian
2. Open folder as vault: `Bronze_Tier/AI_Employee_Vault_FTE`

### 3. Start the Orchestrator

```bash
uv run python -m orchestrator
```

### 4. Test the System

Drop any file into `/Inbox`:

```bash
cp some_file.txt AI_Employee_Vault_FTE/Inbox/
```

---

## CLI Commands

```bash
# Full autonomous mode
uv run python -m orchestrator

# Watcher only
uv run python -m watchers

# System status
uv run python -m orchestrator --status
```

---

## Human-in-the-Loop (HITL)

### For Humans

**When Claude flags an item for approval:**

1. Open `/Pending_Approval` folder
2. Read the approval request
3. Check corresponding Plan.md in `/Plans`
4. Make decision:
   - **Approve:** Move file to `/Approved`
   - **Reject:** Move file to `/Rejected`

**Important:** Never move directly from `/Pending_Approval` to `/Done`

### For Claude

- Routine actions: Execute directly
- Sensitive actions: Create approval request in `/Pending_Approval`
- Approved actions: Execute when file appears in `/Approved`
- Rejected actions: Orchestrator handles - deletes action file, archives rejection with audit info

---

## Logging Features

The orchestrator provides color-coded, real-time logging:

- **Orchestrator logs** - Light Blue color
- **Watcher logs** - Light Yellow color
- **Claude logs** - Light Cyan color

Claude outputs action tags during execution:
- `>>> SKILL USED:` - When invoking skills
- `>>> READ:` - Reading files
- `>>> WRITE:` - Writing/creating files
- `>>> MOVE:` - Moving files between folders
- `>>> DONE:` - Task completion

---

## Agent Skills

### `/process-inbox`
- Read files in `/Needs_Action`
- Move to `/In_Progress` (claim)
- Create Plan.md in `/Plans`
- Execute or flag for approval
- Move to `/Done` or `/Pending_Approval`

### `/update-dashboard`
- Count items in all folders
- Update all tables
- Update statistics

---

## Requirements

- Python 3.13+
- Claude Code installed and in PATH
- Obsidian (optional)

---

## Next Steps

- **Silver Tier:** Gmail/WhatsApp watchers, MCP servers
- **Gold Tier:** Odoo, CEO Briefing, Ralph Wiggum
- **Platinum Tier:** Cloud deployment
