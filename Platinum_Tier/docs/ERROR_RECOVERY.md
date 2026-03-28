# Error Recovery & Graceful Degradation - Gold Tier ✅ COMPLETE

## Overview

Automatic error recovery and graceful degradation for all AI Employee services.

**Status:** ✅ All services protected with retry, circuit breaker, and health checks

---

## Features

| Feature | Description | Status |
|---------|-------------|--------|
| **Retry with Exponential Backoff** | Automatically retry failed operations (3 attempts) | ✅ Complete |
| **Circuit Breaker** | Stop calling failing services temporarily (5 min timeout) | ✅ Complete |
| **Health Checks** | Check service health before making requests | ✅ Complete |
| **Graceful Degradation** | Continue operating with reduced functionality | ✅ Complete |
| **Error Notifications** | Log all errors and recovery attempts | ✅ Complete |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Request Flow                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Health Check                                             │
│     ↓                                                        │
│  Is service healthy? ──NO──> Use fallback or notify         │
│     │ YES                                                    │
│     ↓                                                        │
│  2. Circuit Breaker                                          │
│     ↓                                                        │
│  Circuit closed? ──NO──> Block request (retry later)        │
│     │ YES                                                    │
│     ↓                                                        │
│  3. Retry Decorator                                          │
│     ↓                                                        │
│  Try request ──FAIL──> Retry (up to 3 times with backoff)   │
│     │ SUCCESS                                                │
│     ↓                                                        │
│  4. Return result                                            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Retry with Exponential Backoff

### How It Works

```
Attempt 1: Fail → Wait 1s
Attempt 2: Fail → Wait 2s
Attempt 3: Fail → Wait 4s
Attempt 4: Fail → Give up and report error
```

### Usage

```python
from audit import retry

@retry(max_attempts=3, delay=1, backoff=2)
async def create_invoice(...):
    # Automatically retries on failure
    result = await odoo_service.create_invoice(...)
    return result
```

### Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `max_attempts` | 3 | Number of retry attempts |
| `delay` | 1.0 | Initial delay in seconds |
| `backoff` | 2.0 | Multiplier for each retry |
| `exceptions` | `Exception` | Which exceptions trigger retry |

---

## Circuit Breaker

### How It Works

```
CLOSED (Normal) → 3 failures → OPEN (Blocked for 5 min)
                              ↓
                    5 min timeout → HALF-OPEN (Test 1 request)
                              ↓
                    Success → CLOSED | Failure → OPEN
```

### States

| State | Behavior |
|-------|----------|
| **CLOSED** | Normal operation, all requests allowed |
| **OPEN** | Requests blocked, service assumed down |
| **HALF-OPEN** | Testing if service recovered (1 request allowed) |

### Usage

```python
from audit import get_circuit_breaker

circuit_breaker = get_circuit_breaker()

@circuit_breaker
async def create_invoice(...):
    # Will stop calling if Odoo fails 3 times
    # Will try again after 5 minutes
    result = await odoo_service.create_invoice(...)
    return result
```

### Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `failure_threshold` | 3 | Failures before opening circuit |
| `recovery_timeout` | 300 (5 min) | Seconds before testing recovery |
| `half_open_max_calls` | 1 | Test calls in half-open state |

---

## Health Checks

### Available Health Checks

```python
from audit import (
    check_odoo_health,
    check_facebook_health,
    check_email_health,
    check_linkedin_health,
    check_whatsapp_health
)

# Check individual services
odoo_healthy = await check_odoo_health()
facebook_healthy = await check_facebook_health()

# Get all health statuses
all_statuses = get_all_health_statuses()
# Returns: {'odoo': True, 'facebook': False, ...}
```

### Health Check Logic

| Service | Check Method | Cache TTL |
|---------|--------------|-----------|
| **Odoo** | Try to connect | 60 seconds |
| **Facebook** | Get page info | 60 seconds |
| **Email** | Authenticate | 60 seconds |
| **LinkedIn** | Get profile | 60 seconds |
| **WhatsApp** | Check session exists | 60 seconds |

---

## Graceful Degradation

### How It Works

When a service fails:

1. **Retry automatically** (up to 3 times)
2. **Open circuit breaker** (stop calling for 5 minutes)
3. **Use fallback** (if available)
4. **Continue operating** (with reduced functionality)
5. **Log error** (for later review)

### Example: Odoo Down

```
Scenario: Odoo is down

1. User requests invoice creation
2. Health check fails → Odoo is unhealthy
3. Circuit breaker opens → Stop calling Odoo
4. Fallback: Queue invoice for later
5. Notify user: "Odoo is temporarily unavailable, invoice queued"
6. System continues operating (email, WhatsApp, LinkedIn still work)
7. After 5 minutes: Test Odoo again
8. If healthy: Close circuit, resume normal operation
```

---

## Integration with Services

### Odoo Service

```python
from audit import retry, get_circuit_breaker, check_odoo_health

circuit_breaker = get_circuit_breaker()

@retry(max_attempts=3, delay=1, backoff=2)
@circuit_breaker
async def create_invoice(...):
    # Check health first
    if not await check_odoo_health():
        raise ServiceUnavailableError("Odoo is unhealthy")
    
    # Create invoice with retry and circuit breaker
    result = await odoo_service.create_invoice(...)
    return result
```

### Facebook Service

```python
@retry(max_attempts=3, delay=1, backoff=2)
@circuit_breaker
async def post_facebook(...):
    if not await check_facebook_health():
        raise ServiceUnavailableError("Facebook is unhealthy")
    
    result = await facebook_service.post_facebook(...)
    return result
```

---

## Error Handling Flow

```
User Request
    ↓
Health Check → FAIL → Use fallback, notify user
    ↓ PASS
Circuit Breaker → OPEN → Queue request, notify user
    ↓ CLOSED
Execute with Retry → FAIL (3x) → Open circuit, use fallback
    ↓ SUCCESS
Return Result
    ↓
Log to Audit
```

---

## Monitoring & Alerts

### Check Service Health

```bash
# Python
python -c "
from audit import get_all_health_statuses
statuses = get_all_health_statuses()
for service, healthy in statuses.items():
    status = '✅' if healthy else '❌'
    print(f'{status} {service}')
"
```

### View Error Logs

```bash
# View error logs from today
python -c "
from audit import get_audit_logger
logger = get_audit_logger()
errors = logger.get_error_logs()
for error in errors:
    print(f\"{error['timestamp']} - {error['component']}.{error['action']}: {error['error']}\")
"
```

### Get Circuit Breaker Status

```bash
# Check circuit breaker states
python -c "
from audit import get_circuit_breaker
cb = get_circuit_breaker()
for func_name in cb._function_states:
    state = cb.get_state(func_name)
    print(f'{func_name}: {state}')
"
```

---

## Configuration

### Environment Variables

```bash
# Retry configuration
RETRY_MAX_ATTEMPTS=3
RETRY_DELAY=1.0
RETRY_BACKOFF=2.0

# Circuit breaker configuration
CIRCUIT_FAILURE_THRESHOLD=3
CIRCUIT_RECOVERY_TIMEOUT=300

# Health check configuration
HEALTH_CHECK_CACHE_TTL=60
```

### Customize Defaults

```python
# Custom circuit breaker
from audit import CircuitBreaker

custom_cb = CircuitBreaker(
    failure_threshold=5,      # 5 failures before opening
    recovery_timeout=600,     # 10 minutes recovery
    half_open_max_calls=3     # 3 test calls
)
```

---

## Best Practices

### 1. Always Use Retry for External Services

```python
# ✅ Good
@retry(max_attempts=3)
async def send_email(...):
    ...

# ❌ Bad - No retry
async def send_email(...):
    ...
```

### 2. Check Health Before Critical Operations

```python
# ✅ Good
if await check_odoo_health():
    await create_invoice(...)
else:
    # Use fallback
    ...

# ❌ Bad - No health check
await create_invoice(...)  # Might fail if Odoo is down
```

### 3. Respect Circuit Breaker

```python
# ✅ Good
@circuit_breaker
async def post_facebook(...):
    ...

# ❌ Bad - Bypasses circuit breaker
async def post_facebook(...):
    ...
```

### 4. Log All Errors

```python
# ✅ Good - Audit logger logs automatically
try:
    result = await service.create_invoice(...)
except Exception as e:
    audit_logger.log_action(..., status='error', error=str(e))
    raise

# ❌ Bad - Silent failure
try:
    result = await service.create_invoice(...)
except:
    pass
```

---

## Gold Tier Compliance

✅ **Requirement 8: Error Recovery & Graceful Degradation** - COMPLETE

All services now have:
- ✅ Automatic retry (3 attempts with exponential backoff)
- ✅ Circuit breaker (opens after 3 failures, recovers after 5 min)
- ✅ Health checks (before making requests)
- ✅ Graceful degradation (continues with reduced functionality)
- ✅ Error logging (all errors tracked in audit log)

---

## Testing Error Recovery

### Test Retry

```python
from audit import retry

@retry(max_attempts=3, delay=0.1, backoff=2)
async def test_retry():
    raise Exception("Test failure")

# Will retry 3 times with delays: 0.1s, 0.2s, 0.4s
try:
    await test_retry()
except Exception as e:
    print(f"Failed after retries: {e}")
```

### Test Circuit Breaker

```python
from audit import get_circuit_breaker

cb = get_circuit_breaker()

@cb
async def test_circuit():
    raise Exception("Test failure")

# Trigger 3 failures
for i in range(3):
    try:
        await test_circuit()
    except:
        pass

# Check state
print(cb.get_state('test_circuit'))  # Should be 'open'
```

### Test Health Check

```python
from audit import check_odoo_health

# With Odoo running
healthy = await check_odoo_health()
print(f"Odoo healthy: {healthy}")  # True

# Stop Odoo, then check
healthy = await check_odoo_health()
print(f"Odoo healthy: {healthy}")  # False
```

---

*Error Recovery & Graceful Degradation is a Gold Tier requirement for production-ready reliability.*
