# Odoo 19 Setup Instructions - Gold Tier

## Prerequisites
- Docker Desktop installed and running
- At least 4GB of free disk space for the database and Odoo data
- 5-10 minutes for initial setup

---

## Quick Start (First Time Setup)

### Step 1: Start Services
```bash
cd odoo
docker-compose up -d
```

Wait 30 seconds for PostgreSQL to be ready.

### Step 2: Initialize Database (CRITICAL - Required First Time Only!)

**This step is REQUIRED** because Odoo's Docker image skips automatic initialization when the database already exists.

```bash
docker-compose run --rm odoo odoo -d odoo_db -i base --stop-after-init
```

**What this does:**
- `-d odoo_db` : Specifies database name
- `-i base` : Installs base module (and dependencies: web, bus, etc.)
- `--stop-after-init` : Stops after initialization completes

**Expected output:**
```
2026-03-08 INFO odoo_db odoo.modules.loading: Modules loaded.
2026-03-08 INFO odoo_db odoo.registry: Registry loaded in 55.2s
2026-03-08 INFO odoo_db odoo.service.server: Initiating shutdown
Database initialization complete.
```

This takes **2-5 minutes** on first run.

### Step 3: Start Odoo Normally
```bash
docker-compose up -d
```

Wait 30-60 seconds for Odoo to fully start.

### Step 4: Access Odoo
Open your browser: **http://localhost:8069**

You should see the **Odoo login page** (not an error page).

---

## Login Credentials

| Field | Value |
|-------|-------|
| **Database** | `odoo_db` |
| **Email/Login** | `admin` |
| **Password** | `admin` |

**⚠️ IMPORTANT:** Change the password immediately after first login!

---

## Complete Setup Script (One Command)

For convenience, run all steps at once:

```bash
cd odoo

# 1. Clean start (optional, if restarting)
docker-compose down -v

# 2. Start database
docker-compose up -d db

# 3. Wait for database
sleep 10

# 4. Initialize database with base modules
docker-compose run --rm odoo odoo -d odoo_db -i base --stop-after-init

# 5. Start all services
docker-compose up -d

echo "Odoo is ready! Access at http://localhost:8069"
echo "Login: admin / Password: admin"
```

---

## Windows Automated Setup

Use the included batch file:

```cmd
cd odoo
setup.bat
```

This script will:
1. Clean up existing containers
2. Start services
3. Initialize the database
4. Display login information

---

## Troubleshooting

### Problem: "Internal Server Error" or KeyError 'ir.http'

**Cause:** Database exists but is empty (no tables/modules installed).

**Solution:** Run the initialization command:
```bash
docker-compose run --rm odoo odoo -d odoo_db -i base --stop-after-init
```

### Problem: Connection refused or database not ready

**Cause:** PostgreSQL hasn't finished starting.

**Solution:** Wait and check status:
```bash
docker-compose ps
# Wait until db shows "(healthy)"
docker-compose logs db
```

### Problem: Container won't start

**Solution:** Complete reset:
```bash
docker-compose down -v
docker volume prune -f
docker-compose up -d
# Then run initialization again
```

### Problem: Can't access http://localhost:8069

**Check:**
1. Is Odoo running? `docker-compose ps`
2. Check logs: `docker-compose logs odoo --tail=50`
3. Wait 60 seconds after starting

---

## Common Commands

### Daily Use (After First Setup)

| Command | When to Use |
|---------|-------------|
| `docker-compose up -d` | **Normal startup** - Use this 99% of the time (after reboot, shutdown, restart) |
| `docker-compose down` | Stop Odoo temporarily |
| `docker-compose ps` | Check if Odoo is running |
| `docker-compose logs -f` | View live logs |

### First Time Setup Only

| Command | When to Use |
|---------|-------------|
| `docker-compose run --rm odoo odoo -d odoo_db -i base --stop-after-init` | **First time only!** Initializes database with tables and modules. Run once, never again (unless you delete volumes). |

### Emergency/Reset Only

| Command | When to Use |
|---------|-------------|
| `docker-compose down -v` | **Complete reset** - Deletes ALL data (invoices, customers, settings). Use only if you want to start fresh. |
| `docker volume prune -f` | Clean up unused Docker volumes |

---

## ⚠️ IMPORTANT: When to Use Initialization Command

### ❌ DO NOT Run Initialization (Normal Restart)

Use **only** `docker-compose up -d` when:

- ✅ You restarted your computer
- ✅ You closed Docker Desktop
- ✅ You ran `docker-compose down` earlier
- ✅ Odoo was working before shutdown

**Your data is saved in Docker volumes - no need to re-initialize!**

### ✅ DO Run Initialization (First Time or Reset)

Run `docker-compose run --rm odoo odoo -d odoo_db -i base --stop-after-init` when:

- ✅ **First time setup** (brand new installation)
- ✅ You ran `docker-compose down -v` (deleted volumes)
- ✅ You see "Internal Server Error" or "KeyError: ir.http"
- ✅ Database is empty/corrupted

**This command is for ONE-TIME setup only!**

---

## Architecture

```
┌─────────────────┐
│   Browser       │
│ localhost:8069  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Odoo 19.0     │
│  (AI Employee)  │
│  Port: 8069     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  PostgreSQL 15  │
│  Database:      │
│  odoo_db        │
│  User: odoo     │
│  Pass: odoo123  │
└─────────────────┘
```

---

## Default Credentials Summary

| Component | Credential | Value |
|-----------|------------|-------|
| **Odoo Login** | Email/Login | `admin` |
| **Odoo Login** | Password | `admin` |
| **Odoo Login** | Database | `odoo_db` |
| **Database** | User | `odoo` |
| **Database** | Password | `odoo123` |
| **Database** | Name | `odoo_db` |
| **Master Password** | Database Manager | `admin` |

---

## Volumes and Data Persistence

Data is stored in Docker volumes:

| Volume | Purpose |
|--------|---------|
| `odoo_data` | Odoo application data, sessions, filestore |
| `postgres_data` | PostgreSQL database (all Odoo data) |

**To backup:**
```bash
docker run --rm -v odoo_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/odoo-db-backup.tar.gz /data
```

**To restore:**
```bash
docker run --rm -v odoo_postgres_data:/data -v $(pwd):/backup alpine tar xzf /backup/odoo-db-backup.tar.gz -C /
```

---

## Next Steps After Login

1. **Change admin password** (Settings → Users & Companies)
2. **Install additional modules** (Apps menu):
   - Accounting (for Gold Tier integration)
   - Invoicing
   - Sales
   - Purchase
   - CRM
   - HR
   - Inventory
3. **Configure company settings**
4. **Set up MCP server connection** for AI Employee integration

---

## Gold Tier Integration

After Odoo is running:

1. **Configure Odoo MCP Server:**
   - Update `.env` with Odoo credentials
   - Set `ODOO_URL=http://localhost:8069`
   - Set `ODOO_USERNAME=admin`
   - Set `ODOO_PASSWORD=admin` (or your changed password)

2. **Test Connection:**
   ```bash
   cd Gold_Tier
   uv run python -c "from mcp_server.odoo_service import OdooService; s = OdooService(); print('Connected:', s._connect())"
   ```

3. **Use Odoo Tools via MCP:**
   - `create_invoice` - Create customer invoices
   - `record_payment` - Record payments
   - `get_financial_report` - Get P&L reports
   - `list_unpaid_invoices` - List outstanding invoices

---

## Support

For issues:
1. Check logs: `docker-compose logs -f`
2. Verify containers: `docker-compose ps`
3. Review this README
4. Check Odoo documentation: https://www.odoo.com/documentation/

---

*Last Updated: March 2026*
*Odoo Version: 19.0*
*Gold Tier - AI Employee Project*
