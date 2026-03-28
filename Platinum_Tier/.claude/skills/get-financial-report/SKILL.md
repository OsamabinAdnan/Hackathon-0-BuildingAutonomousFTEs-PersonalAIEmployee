---
name: get-financial-report
description: Get financial reports from Odoo including revenue, expenses, and profit. Use for CEO briefings, financial reviews, weekly/monthly reports, or when asked about business performance.
---

# Get Financial Report - Gold Tier

Fetch financial data from Odoo via MCP server.

---

## When to Use

Use this skill when:
- Generating weekly CEO briefing
- User asks about revenue/profit
- Monthly/quarterly financial review
- Checking business performance
- Preparing financial summaries

---

## Instructions

### Step 1: Determine Report Period

Ask user or determine from context:
- **week** - Last 7 days
- **month** - Last 30 days (default)
- **quarter** - Last 3 months
- **year** - Last 12 months

### Step 2: Fetch Report via MCP

Use the MCP tool to get financial data:

```
mcp__ai-employee__get_financial_report(period="month")
```

### Step 3: Format and Present Data

Display the results clearly:

```
Financial Report (month):
- Revenue: $X,XXX.XX
- Expenses: $X,XXX.XX
- Profit: $X,XXX.XX
- Total Invoices: XX
```

### Step 4: Log the Action

Print action tags for logging:
```
[SKILL] Using skill: /get-financial-report
[MCP] Calling mcp__ai-employee__get_financial_report
[DONE] Report fetched: Revenue $X,XXX, Profit $XXX
```

---

## Examples

### Example 1: Monthly Report

**User:** Get financial report for this month

**AI:**
```
[SKILL] Using skill: /get-financial-report
[INFO] Fetching monthly financial report
[MCP] Calling mcp__ai-employee__get_financial_report(period="month")
[DONE] Report fetched:
- Revenue: $7,600.00
- Expenses: $0.00
- Profit: $7,600.00
- Invoices: 1
```

### Example 2: Weekly Report for CEO Briefing

**User:** Generate weekly CEO briefing

**AI:**
```
[SKILL] Using skill: /generate-briefing
[SKILL] Using skill: /get-financial-report
[INFO] Fetching weekly financial data
[MCP] Calling mcp__ai-employee__get_financial_report(period="week")
[DONE] Weekly revenue: $7,600.00
[WRITE] Writing CEO_Briefing_2026-03-09.md
```

### Example 3: Quarterly Review

**User:** How did we do last quarter?

**AI:**
```
[SKILL] Using skill: /get-financial-report
[INFO] Fetching quarterly financial report
[MCP] Calling mcp__ai-employee__get_financial_report(period="quarter")
[DONE] Q1 2026 Report:
- Revenue: $25,000.00
- Expenses: $8,500.00
- Profit: $16,500.00
- Invoices: 12
```

---

## MCP Tool Reference

| Tool | Parameters | Returns |
|------|------------|---------|
| `mcp__ai-employee__get_financial_report` | period (str: week/month/quarter/year), report_type (str: profit_loss/balance_sheet) | Revenue, expenses, profit, invoice count |

---

## Output Format

```markdown
## Financial Report ({period})

| Metric | Amount |
|--------|--------|
| Revenue | $X,XXX.XX |
| Expenses | $X,XXX.XX |
| **Profit** | **$X,XXX.XX** |
| Invoices | XX |

**Profit Margin:** XX%
```

---

## Error Handling

| Error | Action |
|-------|--------|
| Odoo not connected | Report error, suggest checking connection |
| No data for period | Report zeros, note "No invoices in this period" |
| Accounting module not installed | Report gracefully: "Invoicing module not installed" |

---

## Related Skills

- `/create-invoice` - Create invoices that appear in report
- `/record-payment` - Record payments that affect revenue
- `/generate-briefing` - Include report in CEO briefing
- `/update-dashboard` - Show financial metrics on dashboard

---

## Completion Checklist

- [ ] Determined report period
- [ ] Called MCP tool: mcp__ai-employee__get_financial_report
- [ ] Formatted results clearly
- [ ] Logged action with key metrics
- [ ] Included in briefing/dashboard (if applicable)
