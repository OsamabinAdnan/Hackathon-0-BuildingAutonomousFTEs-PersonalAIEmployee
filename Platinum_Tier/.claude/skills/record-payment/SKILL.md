---
name: record-payment
description: Record customer payments in Odoo accounting system. Use when a customer pays an invoice, when bank transfer is received, or when marking invoices as paid.
---

# Record Payment - Gold Tier

Record payments against invoices in Odoo via MCP server.

---

## When to Use

Use this skill when:
- Customer pays an invoice (bank transfer, check, cash)
- Payment notification received via email
- Bank statement shows payment received
- Manually marking invoice as paid

---

## Instructions

### Step 1: Gather Payment Details

Collect the following information:
- **Invoice ID** or invoice number
- **Payment amount**
- **Payment date** (optional, defaults to today)
- **Payment reference** (optional, e.g., "Bank Transfer", "Check #123")

### Step 2: Check DRY_RUN Mode

Before recording payment:
- If `DRY_RUN=true`: Log what would be recorded, don't create real payment
- If `DRY_RUN=false`: Proceed with recording payment

### Step 3: Record Payment via MCP

Use the MCP tool to record the payment:

```
mcp__ai-employee__record_payment(
    invoice_id=123,
    amount=5000,
    payment_date="2026-03-09",  # optional
    reference="Bank Transfer"  # optional
)
```

### Step 4: Log the Action

Print action tags for logging:
```
[SKILL] Using skill: /record-payment
[MCP] Calling mcp__ai-employee__record_payment
[DONE] Payment recorded: $5,000 for invoice INV/2026/0001
```

### Step 5: Update Records

1. Update invoice status in Odoo (automatically done by MCP)
2. Log payment in vault `/Done/payments/`
3. Update Dashboard.md via /update-dashboard skill

---

## Examples

### Example 1: Simple Payment

**User:** Record payment of $5,000 for invoice INV/2026/0001

**AI:**
```
[SKILL] Using skill: /record-payment
[INFO] Recording payment: $5,000 for INV/2026/0001
[MCP] Calling mcp__ai-employee__record_payment(invoice_id=123, amount=5000)
[DONE] Payment recorded: ID 456, $5,000 for invoice INV/2026/0001
```

### Example 2: Payment from Email Notification

**Email:** "Payment of $10,000 has been transferred for invoice INV/2026/0002"

**AI:**
```
[SKILL] Using skill: /record-payment
[READ] Reading payment notification email
[MOVE] Moving to /In_Progress/email/
[INFO] Recording payment: $10,000 for INV/2026/0002
[MCP] Calling mcp__ai-employee__record_payment(invoice_id=124, amount=10000, reference="Bank Transfer")
[DONE] Payment recorded successfully
[MOVE] Moving to /Done/email/
[SKILL] Using skill: /update-dashboard
```

### Example 3: Dry Run Mode

**If DRY_RUN=true:**
```
[SKILL] Using skill: /record-payment
[DRY RUN] Would record payment: $5,000 for invoice INV/2026/0001
[DRY RUN] Payment date: 2026-03-09
[DRY RUN] Reference: Bank Transfer
[DONE] Dry run complete - no real payment recorded
```

---

## MCP Tool Reference

| Tool | Parameters | Returns |
|------|------------|---------|
| `mcp__ai-employee__record_payment` | invoice_id (int), amount (float), payment_date (str, optional), reference (str, optional) | Payment ID, success status |

---

## Error Handling

| Error | Action |
|-------|--------|
| Invoice not found | Ask for correct invoice number |
| Payment amount mismatch | Verify amount with user |
| Invoice already paid | Report error, invoice already settled |
| Odoo not connected | Report error, suggest checking Odoo connection |

---

## Related Skills

- `/create-invoice` - Create the invoice that was paid
- `/get-financial-report` - View payment in financial report
- `/send-email` - Send payment confirmation to customer
- `/generate-briefing` - Include in weekly CEO briefing

---

## Completion Checklist

- [ ] Gathered payment details (invoice ID, amount)
- [ ] Checked DRY_RUN mode
- [ ] Called MCP tool: mcp__ai-employee__record_payment
- [ ] Logged result with payment ID
- [ ] Updated invoice status (automatic)
- [ ] Updated Dashboard.md
