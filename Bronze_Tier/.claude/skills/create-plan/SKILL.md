# create-plan

Generate execution plans for tasks in /Needs_Action folder.

## When to Use

Invoke this skill when:
- User asks to "create a plan" or "plan tasks"
- Items exist in /Needs_Action folder
- After running process-inbox skill
- Starting complex multi-step tasks

## Description

Analyzes task files in `/Needs_Action` and generates detailed execution plans in `/Plans` folder including:
- Step-by-step actionable checklist
- HITL (Human-in-the-Loop) approval markers
- Risk assessment
- Time estimates

## Workflow

```
Needs_Action/EMAIL_client_invoice.md
              ↓
Plans/PLAN_invoice_client_20260218.md
```

## Instructions

1. Scan `AI_Employee_Vault/Needs_Action/` for task files
2. For each task file:
   a. Read task content and metadata
   b. Analyze requirements and context
   c. Check `Company_Handbook.md` for approval thresholds
   d. Identify if HITL approval is required
   e. Generate step-by-step plan with phases
   f. Write plan to `AI_Employee_Vault/Plans/`
3. Report summary of created plans

## Approval Check Rules

Based on `Company_Handbook.md`:

| Action | Requires Approval |
|--------|-------------------|
| File delete | Yes |
| Email to new contact | Yes |
| Payment > $100 | Yes |
| Payment to new payee | Yes |
| External API write | Yes |
| File read/create | No |
| Email to known contact | No |

## Plan Template

Create files with this structure:

```markdown
---
created: <timestamp>
status: pending
source_task: <original_task_file>
requires_approval: <true/false>
---

# Plan: <Task Name>

## Objective
<Clear statement of what needs to be achieved>

## Context
- <Relevant background info>
- <Dependencies>

## Steps

### Phase 1: <Phase Name>
- [ ] Step 1
- [ ] Step 2

### Phase 2: <Phase Name>
- [ ] Step 1
- [ ] ⚠️ APPROVAL REQUIRED (if applicable)

## Risks
- <Potential issues>

## Estimated Time
<Time estimate>
```

## Output Format

Report results as:

```
Created X execution plans:

1. PLAN_<task>_<date>.md
   Source: <source_file>
   Steps: <count> | Requires Approval: <yes/no>

2. PLAN_<task>_<date>.md
   Source: <source_file>
   Steps: <count> | Requires Approval: <yes/no>

Plans written to /Plans folder.
```

## Notes

- Mark approval steps clearly with ⚠️ symbol
- Break complex tasks into logical phases
- Include context from Company_Handbook.md
- Plans are reference documents, not executable code
