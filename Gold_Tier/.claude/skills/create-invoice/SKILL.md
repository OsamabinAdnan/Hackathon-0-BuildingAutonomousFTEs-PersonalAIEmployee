---
name: create-invoice
description: Create customer invoices in Odoo accounting system. Use when a customer requests an invoice, after completing work for a client, or when recording sales.
---

# Create Invoice - Gold Tier

Create customer invoices in Odoo via MCP server.

---

## When to Use

Use this skill when:
- Customer requests an invoice via email/WhatsApp
- Work is completed and needs to be billed
- Recording a sale in Odoo
- Follow-up on unpaid invoices

---

## Instructions

### Step 1: Gather Invoice Details

Collect the following information:
- **Customer name** (or create new customer)
- **Amount** (without tax)
- **Description** of products/services
- **Due date** (optional, defaults to 30 days)

### Step 2: Check DRY_RUN Mode

Before creating invoice, check if DRY_RUN is enabled:
- If `DRY_RUN=true`: Log what would be created, don't create real invoice
- If `DRY_RUN=false`: Proceed with creating invoice

### Step 3: Create Invoice via MCP

Use the MCP tool to create the invoice:

```
mcp__ai-employee__create_invoice(
    partner_name="Customer Name",
    amount=5000,
    description="Consulting Services",
    due_date="2026-04-01"  # optional
)
```

### Step 4: Log the Action

Print action tags for logging:
```
[SKILL] Using skill: /create-invoice
[MCP] Calling mcp__ai-employee__create_invoice
[DONE] Invoice created: INV/2026/0001 for $5,000
```

### Step 5: Move to /Done/

If this was triggered from /Needs_Action/:
1. Move action file to /Done/email/ or /Done/whatsapp/
2. Update Dashboard.md via /update-dashboard skill

---

## Examples

### Example 1: Simple Invoice

**User:** Create invoice for Client ABC for $5,000 consulting work

**AI:**
```
[SKILL] Using skill: /create-invoice
[INFO] Creating invoice for Client ABC: $5,000
[MCP] Calling mcp__ai-employee__create_invoice(partner_name="Client ABC", amount=5000, description="Consulting Services")
[DONE] Invoice created: INV/2026/0001 for $5,000 (Due: 2026-04-01)
```

### Example 2: Invoice from Email Request

**Email:** "Please send invoice for the website design project. Amount: $10,000"

**AI:**
```
[SKILL] Using skill: /create-invoice
[READ] Reading email request
[MOVE] Moving EMAIL_20260309_client_request.md to /In_Progress/email/
[INFO] Creating invoice for website design: $10,000
[MCP] Calling mcp__ai-employee__create_invoice(partner_name="Client Name", amount=10000, description="Website Design Project")
[DONE] Invoice created: INV/2026/0002 for $10,000
[MOVE] Moving to /Done/email/
[SKILL] Using skill: /update-dashboard
```

### Example 3: Dry Run Mode

**If DRY_RUN=true:**
```
[SKILL] Using skill: /create-invoice
[DRY RUN] Would create invoice for Client ABC: $5,000
[DRY RUN] Description: Consulting Services
[DRY RUN] Due date: 2026-04-01
[DONE] Dry run complete - no real invoice created
```

---

## MCP Tool Reference

| Tool | Parameters | Returns |
|------|------------|---------|
| `mcp__ai-employee__create_invoice` | partner_name (str), amount (float), description (str), due_date (str, optional) | Invoice ID, success status |

---

## Error Handling

| Error | Action |
|-------|--------|
| Customer not found | Create customer first or ask for details |
| Odoo not connected | Report error, suggest checking Odoo connection |
| Invalid amount | Ask user for correct amount |
| DRY_RUN mode | Log what would be done, don't create invoice |

---

## Related Skills

- `/record-payment` - Record payment for this invoice
- `/send-email` - Send invoice to customer
- `/get-financial-report` - View invoice in financial report
- `/generate-briefing` - Include in weekly CEO briefing

---

## Completion Checklist

- [ ] Gathered invoice details (customer, amount, description)
- [ ] Checked DRY_RUN mode
- [ ] Called MCP tool: mcp__ai-employee__create_invoice
- [ ] Logged result with invoice ID
- [ ] Moved action file to /Done/ (if applicable)
- [ ] Updated Dashboard.md
