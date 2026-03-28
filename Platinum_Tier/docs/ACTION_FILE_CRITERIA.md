# Action File Creation Criteria

**Silver Tier - Personal AI Employee**

This document defines the complete criteria and process for creating action files in the `/Needs_Action/` folder.

---

## 📋 Overview

Action files are created by **4 WATCHERS** (Perception Layer) that monitor external sources and convert incoming items into standardized markdown action files.

| Watcher | File | Category Folder | Check Interval |
|---------|------|-----------------|----------------|
| **FileSystemWatcher** | `watchers/filesystem_watcher.py` | `/Needs_Action/files/` | Real-time (watchdog) |
| **GmailWatcher** | `watchers/gmail_watcher.py` | `/Needs_Action/email/` | 120 seconds |
| **WhatsAppWatcher** | `watchers/whatsapp_watcher.py` | `/Needs_Action/whatsapp/` | 30 seconds |
| **LinkedInWatcher** | `watchers/linkedin_watcher.py` | `/Needs_Action/linkedin/` | 300 seconds |

---

## 🎯 Action File Creation Criteria by Watcher

### 1. FileSystem Watcher

**File:** `watchers/filesystem_watcher.py`

#### Trigger Criteria

Action files are created when:

1. **File Creation Event** (`on_created`):
   - A new file is created directly in `/Inbox/` folder
   - Directories are ignored
   - `.md` files are ignored

2. **File Move Event** (`on_moved`):
   - A file is moved into `/Inbox/` folder from elsewhere
   - Directories are ignored

3. **Existing Files on Startup** (`scan_existing_files`):
   - Files already present in `/Inbox/` when watcher starts
   - Excludes `.md` files and directories

#### Exclusion Criteria

- ❌ Directories (only files are processed)
- ❌ `.md` files (markdown files ignored)
- ❌ Already processed files (tracked by filename in state file)

#### Action File Format

**Location:** `/Needs_Action/files/FILE_{timestamp}_{stem}.md`

```markdown
---
type: file_drop
category: files
original_name: example.pdf
archive_path: /Archive/20260303_120000_example.pdf
size_bytes: 1024
extension: .pdf
created: 2026-03-03T12:00:00
priority: medium
status: pending
---

# File Detected in /Inbox

## File Information
- **Original Name:** example.pdf
- **Size:** 1.0 KB
- **Extension:** .pdf
- **Archived At:** /Archive/20260303_120000_example.pdf

## Suggested Actions
- [ ] Read the archived file
- [ ] Process according to file type
- [ ] Move to /Done when complete

## Notes
_Add any notes about this file here_
```

#### Implementation Details

- **Handler Class:** `InboxHandler` (extends `FileSystemEventHandler`)
- **State Tracking:** `.watcher_state/filesystem_processed.json`
- **Archive Location:** `/Archive/{timestamp}_{original_name}`
- **Duplicate Prevention:** Filename-based tracking
- **State Save Interval:** Every 30 seconds (in `run()` method)
- **Recursive Watching:** `False` (only watches `/Inbox/` root, not subfolders)
- **Logger Name:** `FILES` (for colored logging)

**Code Reference:** Lines 95-165 (process_file method)

---

### 2. Gmail Watcher

**File:** `watchers/gmail_watcher.py`

#### Trigger Criteria

Action files are created when:

1. **Unread Emails Detected**:
   - Query: `is:unread` (all unread emails)
   - Maximum 20 emails per check cycle
   - Email not already processed (tracked by Gmail message ID)

2. **Authentication Required**:
   - OAuth2 authentication performed automatically if needed
   - Token refreshed if expired

#### Exclusion Criteria

- ❌ Already processed emails (tracked by Gmail message ID in state file)
- ❌ Authentication failures (logged and skipped)

#### Action File Format

**Location:** `/Needs_Action/email/EMAIL_{timestamp}_{sender}.md`

```markdown
---
type: email
category: email
message_id: 19abc123def456
thread_id: 19abc123def456
from_name: "John Doe"
from_email: john@example.com
to: me
subject: "Project Update"
date: Mon, 3 Mar 2026 10:30:00 +0000
created: 2026-03-03T12:00:00
priority: high
status: pending
---

# Email from John Doe

## Email Details
- **From:** John Doe <john@example.com>
- **To:** me
- **Subject:** Project Update
- **Date:** Mon, 3 Mar 2026 10:30:00 +0000
- **Message ID:** 19abc123def456

## Snippet
{email snippet preview - first 500 characters}

## Suggested Actions
- [ ] Read full email in Gmail
- [ ] Reply if needed
- [ ] Archive after processing
- [ ] Move to /Done when complete

## Notes
_Add any notes about this email here_
```

#### Implementation Details

- **Authentication:** OAuth2 with Google
- **Scopes:** `https://www.googleapis.com/auth/gmail.readonly`
- **State Tracking:** `.watcher_state/gmail_processed.json`
- **Duplicate Prevention:** Gmail message ID tracking
- **Credentials:** `credentials/gmail_credentials.json` and `credentials/gmail_token.json`
- **Query:** `is:unread` (can be customized to `is:unread is:important`)
- **Max Results:** 20 emails per check cycle
- **Logger Name:** `GMAIL` (for colored logging)
- **State Save:** After every check cycle

**Code Reference:** Lines 178-243 (create_action_file method)

---

### 3. WhatsApp Watcher

**File:** `watchers/whatsapp_watcher.py`

#### Trigger Criteria

Action files are created when:

1. **Unread Messages Detected**:
   - Browser navigates to WhatsApp Web
   - Checks all chats for unread indicators
   - Opens each chat and reads last 10 messages

2. **Keyword Matching**:
   - Messages must contain at least one keyword from the list:
     - `urgent`, `asap`, `important`, `invoice`, `payment`
     - `deadline`, `meeting`, `call`, `help`, `action`
     - `confirm`, `approve`, `decision`, `question`
   - Keywords are case-insensitive

3. **Session Management**:
   - Uses persistent browser context (Chrome)
   - Session stored in `sessions/whatsapp/`
   - QR code scan required on first run

#### Exclusion Criteria

- ❌ Messages without keywords (ignored)
- ❌ Already processed messages (tracked by hash-based ID)
- ❌ Browser initialization failures (logged and skipped)

#### Action File Format

**Location:** `/Needs_Action/whatsapp/WHATSAPP_{timestamp}_{chat_name}.md`

```markdown
---
type: whatsapp
category: whatsapp
chat_name: "John Doe"
message_id: wa_123456789
created: 2026-03-03T12:00:00
priority: high
status: pending
---

# WhatsApp Message from John Doe

## Message Details
- **Chat:** John Doe
- **Received:** 2026-03-03 12:00:00
- **Keywords Matched:** This message contains important keywords

## Message Content
{message text - limited to 500 characters}

## Suggested Actions
- [ ] Read full message in WhatsApp
- [ ] Reply if needed
- [ ] Archive after processing
- [ ] Move to /Done when complete

## Notes
_Add any notes about this message here_
```

#### Implementation Details

- **Browser:** Playwright with Chromium
- **Session:** Persistent context in `sessions/whatsapp/`
- **State Tracking:** `.watcher_state/whatsapp_processed.json`
- **Duplicate Prevention:** Hash-based message ID (`wa_{hash}`)
- **Headless Mode:** Must be `false` (WhatsApp blocks headless)
- **Logger Name:** `WHATSAPP` (for colored logging)
- **State Save:** After every check cycle
- **Login Timeout:** 120 seconds for QR code scan
- **Chat Selectors:** Multiple fallback selectors for robustness
- **Message Limit:** Last 10 messages per chat checked

**Code Reference:** Lines 470-520 (create_action_file method)

---

### 4. LinkedIn Watcher

**File:** `watchers/linkedin_watcher.py`

#### Trigger Criteria

Action files are created when:

1. **New Messages** (`check_messages`):
   - API endpoint: `messaging/conversations`
   - Fallback: `networkUpdates` endpoint
   - Maximum 10 conversations per check

2. **New Notifications** (`check_notifications`):
   - API endpoint: `notificationsV2`
   - Fallback: `networkUpdates` endpoint
   - Maximum 10 notifications per check

3. **API Authentication**:
   - Access token from environment variable
   - LinkedIn API v2 with proper headers

#### Exclusion Criteria

- ❌ Already processed items (tracked by ID in state file)
- ❌ API authentication failures (logged and skipped)
- ❌ Missing access token (error logged, watcher exits)

#### Action File Format

**Location:** `/Needs_Action/linkedin/LINKEDIN_MSG_{timestamp}.md` or `LINKEDIN_NOTIF_{timestamp}.md`

```markdown
---
type: linkedin_message
category: linkedin
conversation_id: ACME123
created: 2026-03-03T12:00:00
priority: medium
status: pending
---

# LinkedIn Message

## Details
- **Conversation ID:** ACME123
- **Received:** 2026-03-03 12:00:00

## Message Summary
A new LinkedIn message requires your attention.

## Suggested Actions
- [ ] Read message on LinkedIn
- [ ] Reply if needed
- [ ] Archive after processing
- [ ] Move to /Done when complete

## Notes
_Add any notes here_
```

#### Implementation Details

- **API Base:** `https://api.linkedin.com/v2`
- **Headers:** `Authorization: Bearer {token}`, `LinkedIn-Version: 202305`, `X-Restli-Protocol-Version: 2.0.0`
- **State Tracking:** `.watcher_state/linkedin_processed.json`
- **Duplicate Prevention:** LinkedIn item ID tracking
- **Token:** `LINKEDIN_ACCESS_TOKEN` environment variable
- **Logger Name:** `LINKEDIN` (for colored logging)
- **State Save:** After every check cycle
- **Max Results:** 10 conversations/notifications per check
- **Fallback Endpoints:** `networkUpdates` if primary endpoints fail
- **API Timeout:** 30 seconds per request

**Code Reference:** Lines 280-350 (create_action_file method)

---

## 📁 Universal Action File Structure

Every action file contains:

### 1. YAML Frontmatter

```yaml
---
type: {source_type}           # email, whatsapp, linkedin, file_drop
category: {category_folder}   # email, whatsapp, linkedin, files
created: {ISO_timestamp}
priority: {high|medium|low}
status: pending
# Source-specific fields below
{additional_fields}
---
```

### 2. Markdown Content

```markdown
# {Descriptive Title}

## {Section Name}
- **Field:** Value
- **Field:** Value

## Suggested Actions
- [ ] Action item 1
- [ ] Action item 2
- [ ] Move to /Done when complete

## Notes
_Add any notes here_
```

---

## 🔄 Complete Workflow

```
┌─────────────────┐
│ External Source │
│ (Gmail, WA, LI, │
│  Files)         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     WATCHER     │
│  (Perception    │
│     Layer)      │
└────────┬────────┘
         │
         │ Detects new item
         ▼
┌─────────────────┐
│  Create Action  │
│     File        │
│  (.md format)   │
└────────┬────────┘
         │
         │ Moves to
         ▼
┌─────────────────────────────────┐
│  /Needs_Action/{category}/      │
│  - /Needs_Action/email/         │
│  - /Needs_Action/whatsapp/      │
│  - /Needs_Action/linkedin/      │
│  - /Needs_Action/files/         │
└────────────────┬────────────────┘
                 │
                 │ Orchestrator detects
                 ▼
        ┌────────────────┐
        │  Claude Code   │
        │  (Reasoning)   │
        └────────────────┘
```

---

## 📊 State Management

Each watcher maintains a state file to prevent duplicate processing:

| Watcher | State File | Tracking Field |
|---------|------------|----------------|
| FileSystem | `.watcher_state/filesystem_processed.json` | `processed_files` (array of filenames) |
| Gmail | `.watcher_state/gmail_processed.json` | `processed_ids` (array of Gmail message IDs) |
| WhatsApp | `.watcher_state/whatsapp_processed.json` | `processed_messages` (array of hash-based IDs) |
| LinkedIn | `.watcher_state/linkedin_processed.json` | `processed_ids` (array of LinkedIn item IDs) |

### State File Format

```json
{
  "processed_{field}": ["id1", "id2", "id3"],
  "last_updated": "2026-03-03T12:00:00.000000",
  "total_processed": 3
}
```

---

## 🎯 Priority Assignment

| Watcher | Priority Logic |
|---------|----------------|
| FileSystem | Always `medium` |
| Gmail | Always `high` |
| WhatsApp | Always `high` (keyword-matched) |
| LinkedIn | Always `medium` |

---

## ⚠️ Error Handling

Each watcher handles errors gracefully:

| Watcher | Error Handling |
|---------|----------------|
| **FileSystem** | Logs error, continues watching, state saved periodically |
| **Gmail** | Logs error, resets service on auth errors (401/403), retries on next cycle |
| **WhatsApp** | Logs error, continues monitoring, browser reinitialized on crash |
| **LinkedIn** | Logs error, continues monitoring, exits if token missing |

### Specific Error Scenarios

**FileSystem Watcher:**
- File locked/in-use: Logs error, skips file
- Archive move fails: Logs error, action file still created
- State file corrupt: Clears processed set, starts fresh

**Gmail Watcher:**
- Credentials missing: Logs error, watcher exits
- Token expired: Auto-refreshes using refresh token
- API quota exceeded: Logs error, retries on next cycle

**WhatsApp Watcher:**
- Browser crash: Auto-reinitializes browser
- Session expired: Shows QR code for re-scan
- WhatsApp Web changes: Multiple fallback selectors

**LinkedIn Watcher:**
- Token missing: Logs error, watcher exits
- Token expired (401): Logs error, user must refresh token
- Permission denied (403): Logs error, check app permissions
- Endpoint not found (404): Logs debug, tries fallback endpoint

---

## 📍 Documentation References

| Document | Section |
|----------|---------|
| `CLAUDE.md` | Architecture diagram, Vault Folders table, Watcher Configuration |
| `README.md` | Features, Architecture, Vault Folders, Watcher Configuration |
| `watchers/filesystem_watcher.py` | Full implementation (Lines 1-280) |
| `watchers/gmail_watcher.py` | Full implementation (Lines 1-463) |
| `watchers/whatsapp_watcher.py` | Full implementation (Lines 1-682) |
| `watchers/linkedin_watcher.py` | Full implementation (Lines 1-499) |

---

## ✅ Summary

| Criteria | FileSystem | Gmail | WhatsApp | LinkedIn |
|----------|------------|-------|----------|----------|
| **Trigger** | File in /Inbox/ | Unread email | Keyword message | Message/Notification |
| **Interval** | Real-time | 120s | 30s | 300s |
| **Category** | `files` | `email` | `whatsapp` | `linkedin` |
| **State File** | `filesystem_processed.json` | `gmail_processed.json` | `whatsapp_processed.json` | `linkedin_processed.json` |
| **Duplicate Prevention** | Filename | Message ID | Hash ID | Item ID |
| **Priority** | medium | high | high | medium |
| **Logger Name** | `FILES` | `GMAIL` | `WHATSAPP` | `LINKEDIN` |
| **State Save** | Every 30s | Every cycle | Every cycle | Every cycle |
| **Max Per Cycle** | All files | 20 emails | All keyword messages | 10 items |
| **Error Behavior** | Continue | Retry/Reset | Reinit browser | Continue/Exit |

---

*Document Version: 1.1*
*Last Updated: 2026-03-03*
*Silver Tier - Personal AI Employee*
