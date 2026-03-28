# Ralph Wiggum Loop - Gold Tier ✅ COMPLETE

## Overview

Autonomous multi-step task completion using the stop hook pattern.

**Reference:** https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum

**Status:** ✅ Complete implementation with task tracking and automatic re-injection

---

## What is the Ralph Wiggum Loop?

The Ralph Wiggum Loop is a pattern for **autonomous task completion** where:

1. Claude is given a task
2. Claude works on the task
3. Claude tries to exit
4. **Stop hook intercepts** and checks if task is complete
5. If **not complete**: Re-inject prompt, Claude continues working
6. If **complete**: Allow Claude to exit
7. Repeat until complete or max iterations reached

---

## Why "Ralph Wiggum"?

Named after the Simpsons character who keeps trying until he succeeds. The pattern ensures Claude **doesn't give up** on complex multi-step tasks.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              Ralph Wiggum Loop Flow                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Start Task                                               │
│     ↓                                                        │
│  2. Run Claude with Prompt                                   │
│     ↓                                                        │
│  3. Claude Works on Task                                     │
│     ↓                                                        │
│  4. Claude Tries to Exit                                     │
│     ↓                                                        │
│  5. Stop Hook Intercepts                                     │
│     ↓                                                        │
│  6. Check Completion                                         │
│     ↓                                                        │
│    ┌─────────────────┴─────────────────┐                    │
│    │                                   │                    │
│    ▼ COMPLETE                          ▼ NOT COMPLETE       │
│ Allow Exit                       Check Iteration            │
│ Mark Task Done                      ↓                       │
│                              Under Max?                     │
│                                ↓ YES     ↓ NO               │
│                          Re-inject Prompt  Stop (Max Reached)│
│                                ↓                            │
│                          Back to Step 2                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Components

### 1. Task Tracker (`ralph_wiggum/task_tracker.py`)

Tracks task state:
- Current iteration
- Steps completed
- Files processed
- Errors encountered
- Completion signals

### 2. Stop Hook (`ralph_wiggum/stop_hook.py`)

Intercepts Claude's exit:
- Checks if task is complete
- Re-injects prompt if not complete
- Respects max iterations

### 3. Main Loop (`ralph_wiggum/__init__.py`)

Orchestrates the loop:
- Starts task tracking
- Runs Claude
- Monitors completion
- Logs progress

---

## Usage

### Basic Usage

```python
from ralph_wiggum import start_ralph_loop

start_ralph_loop(
    prompt="Process all files in /Needs_Action, move to /Done when complete",
    max_iterations=10,
    vault_path="./AI_Employee_Vault_FTE"
)
```

### Advanced Usage

```python
from ralph_wiggum import StopHook, TaskTracker

# Initialize
tracker = TaskTracker()
hook = StopHook()

# Start task
tracker.start_task("process-inbox", max_iterations=10)

# Run Claude
while tracker.should_continue():
    # Run Claude with your prompt
    result = run_claude(prompt)
    
    # Check if complete
    if hook.check_completion():
        tracker.mark_task_complete()
        break
    
    # Not complete, continue
    tracker.increment_iteration()
```

### Command Line Usage

```bash
# Process all pending items
python -m ralph_wiggum "Process all files in /Needs_Action"

# With custom max iterations
python -m ralph_wiggum "Process inbox" --max-iterations 15

# With completion file
python -m ralph_wiggum "Generate briefing" --completion-file Briefings/latest.md
```

---

## Completion Detection

The loop detects completion via:

### 1. Completion Signals

Claude outputs special markers:
```
[DONE] All files processed
TASK_COMPLETE
```

### 2. File Movement

Files moved from `/Needs_Action/` to `/Done/`:
```python
tracker.mark_file_processed("file.md", "moved_to_done")
```

### 3. Completion File

Specific file created when done:
```python
start_ralph_loop(prompt, completion_file="Briefings/done.md")
```

---

## Configuration

### Max Iterations

| Value | Use Case |
|-------|----------|
| 3-5 | Simple tasks (single file) |
| 10 | Complex tasks (multiple files) |
| 20+ | Very complex tasks (batch processing) |

### Completion Detection

```python
# Custom completion check
def check_custom_completion() -> bool:
    # Check if all files processed
    needs_action = Path('Needs_Action')
    return len(list(needs_action.glob('*.md'))) == 0

hook.check_completion = check_custom_completion
```

---

## Examples

### Example 1: Process Inbox

```python
from ralph_wiggum import start_ralph_loop

start_ralph_loop(
    prompt="""
Process all files in /Needs_Action:
1. Move each file to /In_Progress
2. Create Plan.md for each
3. Execute actions or flag for approval
4. Move completed to /Done
5. Update Dashboard.md

Output [DONE] when all files processed.
TASK_COMPLETE
""",
    max_iterations=10
)
```

### Example 2: Generate CEO Briefing

```python
start_ralph_loop(
    prompt="""
Generate Weekly CEO Briefing:
1. Fetch Odoo financial data
2. Count completed tasks
3. Check pending approvals
4. Write briefing to /Briefings/
5. Update Dashboard.md

Output TASK_COMPLETE when briefing is written.
""",
    max_iterations=5,
    completion_file="AI_Employee_Vault_FTE/Briefings/latest.md"
)
```

### Example 3: Batch Invoice Processing

```python
start_ralph_loop(
    prompt="""
Process all pending invoices:
1. Read each invoice request in /Needs_Action/email/
2. Create invoice in Odoo via MCP
3. Send invoice via email
4. Move to /Done
5. Log to audit

Mark TASK_COMPLETE when all invoices processed.
""",
    max_iterations=15
)
```

---

## Task Tracker API

### Start Task

```python
tracker.start_task("process-inbox", max_iterations=10)
```

### Mark Steps

```python
tracker.mark_step_complete("move-to-in-progress", "file1.md")
tracker.mark_step_complete("create-plan", "Plan_file1.md")
tracker.mark_step_complete("execute-action", "invoice created")
```

### Track Files

```python
tracker.mark_file_processed("invoice.md", "moved_to_done")
```

### Track Errors

```python
tracker.mark_error("Odoo connection failed", "create_invoice")
```

### Get Summary

```python
summary = tracker.get_summary()
print(f"State: {summary['state']}")
print(f"Iterations: {summary['iteration']}/{summary['max_iterations']}")
print(f"Files processed: {summary['files_processed']}")
```

---

## Best Practices

### 1. Clear Completion Signals

```python
# ✅ Good - Clear signal
print("TASK_COMPLETE - All 5 files processed")

# ❌ Bad - Unclear
print("Done")
```

### 2. Track Progress

```python
# ✅ Good - Track each step
tracker.mark_step_complete("move", file)
tracker.mark_step_complete("plan", plan_file)
tracker.mark_step_complete("execute", action)

# ❌ Bad - No tracking
# Just do the work without tracking
```

### 3. Set Reasonable Max Iterations

```python
# ✅ Good - Based on task complexity
max_iterations=5   # Single file
max_iterations=10  # Multiple files
max_iterations=20  # Batch processing

# ❌ Bad - Too low or too high
max_iterations=1   # Will fail
max_iterations=100 # Will hang
```

### 4. Handle Errors Gracefully

```python
# ✅ Good - Log and continue
try:
    process_file(file)
    tracker.mark_file_processed(file)
except Exception as e:
    tracker.mark_error(str(e), "process_file")
    continue

# ❌ Bad - Crash on first error
process_file(file)  # Crashes, no recovery
```

---

## Monitoring

### Check Loop Status

```bash
# View current state
python -c "
from ralph_wiggum import get_task_tracker
tracker = get_task_tracker()
state = tracker.get_state()
print(f\"Task: {state['current_task']}\")
print(f\"State: {state['task_state']}\")
print(f\"Iteration: {state['iteration']}\")
"
```

### View Logs

```bash
# View Ralph Wiggum logs
tail -f Gold_Tier/AI_Employee_Vault_FTE/Logs/ralph_wiggum_state.json
```

---

## Gold Tier Compliance

✅ **Requirement 10: Ralph Wiggum Loop** - COMPLETE

Implementation includes:
- ✅ Stop hook pattern (intercepts Claude exit)
- ✅ Task tracker (monitors progress)
- ✅ Automatic re-injection (continues until done)
- ✅ Max iterations (prevents infinite loops)
- ✅ Completion detection (multiple methods)
- ✅ Error handling (graceful degradation)
- ✅ Progress logging (audit trail)

---

## Troubleshooting

### Loop Never Completes

**Problem:** Loop keeps re-injecting forever

**Solution:**
1. Check completion signal is being detected
2. Verify files are actually being moved to /Done/
3. Add debug logging to check_completion()

### Loop Exits Too Early

**Problem:** Loop exits before task is done

**Solution:**
1. Check completion detection is too lenient
2. Add more specific completion criteria
3. Increase max_iterations if needed

### Max Iterations Reached

**Problem:** Task doesn't complete in time

**Solution:**
1. Increase max_iterations
2. Check if task is too complex (split into smaller tasks)
3. Check for errors preventing progress

---

*The Ralph Wiggum Loop is a Gold Tier requirement for autonomous multi-step task completion.*
