# Gold Tier Quick Reference

## Quick Start

### 1. Start Odoo (Docker Compose)
```bash
cd Gold_Tier/odoo
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### 2. Access Odoo
- **URL:** http://localhost:8069
- **Master Password:** admin
- **Database:** odoo_db
- **DB User:** odoo
- **DB Password:** odoo_password

### 3. Configure Odoo Credentials
After creating Odoo database and user, update `.env`:
```bash
ODOO_USERNAME=your_email@example.com
ODOO_PASSWORD=your_odoo_password
```

### 4. Test MCP Tools
```bash
# Test Odoo connection
python -m mcp_server.odoo_mcp

# Test main MCP server (includes Odoo + Facebook)
python -m mcp_server
```

---

## MCP Tools Available

### Odoo Tools (4)
| Tool | Description |
|------|-------------|
| `create_invoice` | Create customer invoice |
| `record_payment` | Record payment for invoice |
| `get_financial_report` | Get P&L report |
| `list_unpaid_invoices` | List outstanding invoices |

### Facebook Tools (3)
| Tool | Description |
|------|-------------|
| `post_facebook` | Post to Facebook Page |
| `send_facebook_message` | Send Facebook message |
| `get_facebook_insights` | Get Page insights |

### Existing Tools (Silver Tier)
- Email, WhatsApp, LinkedIn tools (unchanged)

---

## Agent Skills (Gold Tier)

### New Skills to Create
- `/create-invoice` - Create Odoo invoice
- `/record-payment` - Record payment
- `/get-financial-report` - Get financial report
- `/post-facebook` - Post to Facebook
- `/generate-briefing` - Generate CEO briefing

### Existing Skills (Updated)
- `/process-inbox` - Now supports Odoo/Facebook
- `/update-dashboard` - Now shows Odoo/Facebook metrics

---

## File Structure

```
Gold_Tier/
├── odoo/                       # NEW: Odoo Docker setup
│   ├── docker-compose.yml
│   ├── README.md
│   ├── data/                   # Odoo data
│   ├── db-data/                # Database
│   └── logs/                   # Logs
├── mcp_server/
│   ├── odoo_service.py         # NEW: Odoo client
│   ├── odoo_mcp.py             # NEW: Odoo MCP server
│   ├── facebook_service.py     # NEW: Facebook client
│   └── server.py               # Updated: All tools
├── AI_Employee_Vault_FTE/
│   ├── Needs_Action/odoo/      # NEW: Odoo actions
│   └── Accounting/             # NEW: Financial reports
└── docs/
    └── GOLD_TIER_PROGRESS.md   # Implementation status
```

---

## Environment Variables

### Odoo
```bash
ODOO_URL=http://localhost:8069
ODOO_DB=odoo_db
ODOO_USERNAME=your_email
ODOO_PASSWORD=your_password
ODOO_DRY_RUN=false
```

### Facebook (Already configured)
```bash
FACEBOOK_APP_ID=...
FACEBOOK_APP_SECRET=...
FACEBOOK_ACCESS_TOKEN=...
FACEBOOK_PAGE_ID=...
```

---

## Common Commands

### Odoo Docker
```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Restart
docker-compose restart

# Backup data
docker-compose run --rm odoo backup
```

### Testing
```bash
# Test Odoo service
python -c "from mcp_server.odoo_service import OdooService; s = OdooService(); print(s._connect())"

# Test Facebook service  
python -c "from mcp_server.facebook_service import FacebookService; s = FacebookService(); print(s._check_credentials())"
```

---

## Troubleshooting

### Odoo Won't Start
```bash
# Check if port 8069 is in use
netstat -ano | findstr :8069

# Change port in docker-compose.yml
ports:
  - "8070:8069"  # Use 8070 instead
```

### MCP Tools Not Working
```bash
# Check credentials in .env
# Ensure ODOO_USERNAME and ODOO_PASSWORD are set
# Ensure Facebook tokens are valid

# Test connection
cd Gold_Tier
uv run python -m mcp_server.odoo_mcp
```

### Database Connection Failed
```bash
# Restart database
docker-compose restart db

# Check database logs
docker-compose logs db
```

---

## Next Steps

1. ✅ Docker Compose setup
2. ✅ Odoo service created
3. ✅ Facebook service created
4. ✅ MCP tools registered
5. ⏳ Configure Odoo credentials
6. ⏳ Test Odoo connection
7. ⏳ Test Facebook posting
8. ⏳ Create new agent skills
9. ⏳ Implement Ralph Wiggum loop
10. ⏳ Update CEO briefing script

---

## Documentation

- `GOLD_TIER_PROGRESS.md` - Implementation status
- `odoo/README.md` - Odoo setup guide
- `docs/` - Additional documentation (WIP)
