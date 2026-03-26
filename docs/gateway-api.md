# OpenStocki Gateway API Reference

**Base URL:** `https://api.stocki.com.cn`

## 1. General Conventions

### Authentication

All authenticated endpoints use Bearer Token:

```
Authorization: Bearer <token>
```

Token types:
- **API Key**: `sk_` prefix, for `/v1/*` business endpoints
- **Session Token**: `sess_` prefix, for `/user/*` management endpoints (via WeChat OAuth)

| Scope | Auth |
|---|---|
| `/v1/*` business API | API Key (`sk_xxx`) |
| `/user/*` user management | Session Token (`sess_xxx`) |
| `/auth/*` WeChat login | No auth required |
| `/share/{id}` public share page | No auth required |

### Common Headers

```
Content-Type: application/json
Authorization: Bearer <token>
```

### Error Response Format

All errors follow a standard envelope:

```json
{
  "error": "<machine-readable-code>",
  "message": "Human-readable error description",
  "details": {}
}
```

### Error Codes

| Error Code | HTTP Status | Description |
|---|---|---|
| `auth_missing` | 401 | No auth credentials provided |
| `auth_invalid` | 401 | Credentials invalid or expired |
| `quota_exceeded` | 403 | Daily quota exhausted |
| `task_not_found` | 404 | task_id does not exist |
| `run_not_found` | 404 | run_id does not exist |
| `run_error` | 200 | Quant run failed (in status response body, not HTTP error) |
| `report_not_found` | 404 | Report file does not exist |
| `rate_limited` | 429 | Rate exceeded (`details` contains `retry_after`); or global quant queue full |
| `timezone_invalid` | 400 | Invalid IANA timezone name |
| `stocki_unavailable` | 503 | Backend analysis service unavailable |

---

## 2. Business API (/v1)

### POST /v1/instant

Submit an instant query. Synchronous, blocks until response. Timeout: 120s.

**Request:**

```json
POST /v1/instant
Authorization: Bearer sk_abc123def456
Content-Type: application/json

{
  "question": "What is the outlook for A-share semiconductor sector?",
  "timezone": "Asia/Shanghai"
}
```

| Parameter | Type | Required | Description |
|---|---|---|---|
| `question` | string | yes | Query content |
| `timezone` | string | no | IANA timezone, default `"Asia/Shanghai"` |

**Success Response:**

```json
HTTP/1.1 200 OK

{
  "answer": "## A-Share Semiconductor Analysis\n\n...",
  "share_url": "https://stocki.com.cn/s/x7k9m2",
  "usage": {
    "used_today": 3,
    "daily_quota": 8
  }
}
```

| Field | Type | Description |
|---|---|---|
| `answer` | string | Markdown-formatted answer |
| `share_url` | string | Auto-generated share short link |
| `usage.used_today` | int | Queries used today |
| `usage.daily_quota` | int | Total daily quota |

**Error Examples:**

```json
// Quota exceeded
HTTP/1.1 403 Forbidden

{
  "error": "quota_exceeded",
  "message": "Daily free query limit reached",
  "details": {
    "used_today": 8,
    "daily_quota": 8,
    "invite_url": "https://stocki.com.cn/r/STOCK8K"
  }
}
```

```json
// Service unavailable
HTTP/1.1 503 Service Unavailable

{
  "error": "stocki_unavailable",
  "message": "Analysis service temporarily unavailable, please retry later",
  "details": {}
}
```

---

### POST /v1/quant

Submit async quantitative analysis. Returns immediately, does not block.

- Without `task_id`: Gateway auto-creates a new task and submits the first run
- With `task_id`: Appends a new run to an existing task (iterative analysis)

Gateway auto-generates `task_name` from the `question`.

> **Global serial constraint:** Only one quant run can execute at a time. If another is already running, the new submission is rejected (429), not queued.

**Request (new task):**

```json
POST /v1/quant
Authorization: Bearer sk_abc123def456
Content-Type: application/json

{
  "question": "Backtest CSI 300 momentum strategy, lookback 60 days, 2024 to present",
  "timezone": "Asia/Shanghai"
}
```

**Request (iterate on existing task):**

```json
POST /v1/quant
Authorization: Bearer sk_abc123def456
Content-Type: application/json

{
  "question": "Add small-cap filter, change lookback to 90 days",
  "task_id": "t_8f3a1b2c",
  "timezone": "Asia/Shanghai"
}
```

| Parameter | Type | Required | Description |
|---|---|---|---|
| `question` | string | yes | Analysis question |
| `task_id` | string | no | Existing task ID; omit to auto-create new task |
| `timezone` | string | no | IANA timezone, default `"Asia/Shanghai"` |

**Success Response:**

```json
HTTP/1.1 201 Created

{
  "task_id": "t_8f3a1b2c",
  "task_name": "CSI 300 Momentum Backtest"
}
```

| Field | Type | Description |
|---|---|---|
| `task_id` | string | Task ID (new or existing) |
| `task_name` | string | Task name (auto-generated for new, existing name for iterations) |

**Error Examples:**

```json
// Global quant queue full
HTTP/1.1 429 Too Many Requests

{
  "error": "rate_limited",
  "message": "A quant analysis is already running, please retry later",
  "details": {
    "retry_after": 60,
    "active_task_id": "t_other123",
    "active_run_id": "run_003"
  }
}
```

```json
// Quota exceeded
HTTP/1.1 403 Forbidden

{
  "error": "quota_exceeded",
  "message": "Daily quota exhausted",
  "details": {
    "used_today": 8,
    "daily_quota": 8,
    "invite_url": "https://stocki.com.cn/r/STOCK8K"
  }
}
```

```json
// task_id not found
HTTP/1.1 404 Not Found

{
  "error": "task_not_found",
  "message": "Task does not exist",
  "details": {}
}
```

---

### GET /v1/tasks

List all quant tasks for the authenticated user, sorted by most recently updated.

**Request:**

```
GET /v1/tasks
Authorization: Bearer sk_abc123def456
```

**Success Response:**

```json
HTTP/1.1 200 OK

{
  "tasks": [
    {
      "task_id": "t_8f3a1b2c",
      "name": "CSI 300 Momentum Backtest",
      "description": null,
      "created_at": "2026-03-23T14:30:00+08:00",
      "updated_at": "2026-03-23T15:45:00+08:00",
      "message_count": 4
    }
  ]
}
```

| Field | Type | Description |
|---|---|---|
| `tasks[].task_id` | string | Task ID |
| `tasks[].name` | string | Task name |
| `tasks[].description` | string? | Description, may be null |
| `tasks[].created_at` | string | ISO-8601 creation time |
| `tasks[].updated_at` | string | ISO-8601 last update time |
| `tasks[].message_count` | int | Message count (human + ai) |

**Empty response:**

```json
{ "tasks": [] }
```

---

### GET /v1/tasks/{task_id}

Get task details and run statuses.

**Request:**

```
GET /v1/tasks/t_8f3a1b2c
Authorization: Bearer sk_abc123def456
```

**Success Response (with active run):**

```json
HTTP/1.1 200 OK

{
  "task_id": "t_8f3a1b2c",
  "name": "CSI 300 Momentum Backtest",
  "created_at": "2026-03-23T14:30:00+08:00",
  "updated_at": "2026-03-23T15:45:00+08:00",
  "current_run": {
    "run_id": "run_002",
    "query": "Add small-cap filter, change lookback to 90 days",
    "status": "running",
    "started_at": "2026-03-23T15:40:00+08:00"
  },
  "runs": [
    {
      "run_id": "run_001",
      "query": "Backtest CSI 300 momentum strategy, lookback 60 days",
      "status": "success",
      "summary": "CSI 300 momentum strategy: 18.3% annualized return, Sharpe 1.2, max drawdown -15%",
      "started_at": "2026-03-23T14:30:00+08:00",
      "completed_at": "2026-03-23T15:00:00+08:00",
      "error_message": null,
      "report": "runs/run_001/report.md",
      "files": [
        "runs/run_001/report.md",
        "runs/run_001/images/chart_001.png",
        "runs/run_001/images/chart_002.png"
      ]
    },
    {
      "run_id": "run_002",
      "query": "Add small-cap filter, change lookback to 90 days",
      "status": "running",
      "summary": null,
      "started_at": "2026-03-23T15:40:00+08:00",
      "completed_at": null,
      "error_message": null,
      "report": null,
      "files": []
    }
  ]
}
```

| Field | Type | Description |
|---|---|---|
| `task_id` | string | Task ID |
| `name` | string | Task name |
| `created_at` | string | ISO-8601 creation time |
| `updated_at` | string | ISO-8601 update time |
| `current_run` | object? | Currently active run, null if none |
| `runs[]` | array | All runs for this task |
| `runs[].run_id` | string | Run ID |
| `runs[].query` | string | Query content |
| `runs[].status` | string | `"queued"` / `"running"` / `"success"` / `"error"` |
| `runs[].summary` | string? | Result summary (present on success) |
| `runs[].started_at` | string | ISO-8601 start time |
| `runs[].completed_at` | string? | ISO-8601 completion time, null if not finished |
| `runs[].error_message` | string? | Error message (present when status=error) |
| `runs[].report` | string? | Main report COS path |
| `runs[].files` | array | Result file path list |

---

### GET /v1/tasks/{task_id}/files/{path}

Download task result files (reports, charts). Gateway proxies from Tencent COS.

**Request (markdown report):**

```
GET /v1/tasks/t_8f3a1b2c/files/runs/run_001/report.md
Authorization: Bearer sk_abc123def456
```

**Success Response:**

```
HTTP/1.1 200 OK
Content-Type: text/markdown; charset=utf-8

# CSI 300 Momentum Strategy Backtest Report
...
```

**Request (image file):**

```
GET /v1/tasks/t_8f3a1b2c/files/runs/run_001/images/chart_001.png
Authorization: Bearer sk_abc123def456
```

**Success Response:**

```
HTTP/1.1 200 OK
Content-Type: image/png
Content-Length: 45678

<binary PNG data>
```

**Error Response:**

```json
HTTP/1.1 404 Not Found

{
  "error": "report_not_found",
  "message": "File 'runs/run_001/report.md' does not exist",
  "details": {}
}
```

---

## 3. User API (/user)

### GET /user/me

Get current user info (requires Session Token).

**Response 200:**
```json
{
  "id": "u_abc123",
  "nickname": "WeChat Username",
  "avatar_url": "https://...",
  "api_key": "sk_test1234..."
}
```

`api_key` is masked (prefix + `...`). Full key is only shown once at creation.

---

## 4. WeChat Login API (/auth/wechat)

### POST /auth/wechat/mp/login

WeChat Official Account OAuth login (in-app browser). No auth required.

**Request:**
```json
{
  "code": "WeChat callback authorization code"
}
```

**Response 200:**
```json
{
  "session_token": "sess_xxx",
  "user": {
    "id": "u_xxx",
    "nickname": "WeChat Nickname",
    "avatar_url": "Avatar URL"
  },
  "api_key": "sk_xxx (full value only on first registration, otherwise null)",
  "is_new_user": true
}
```

### POST /auth/wechat/open/login

Open Platform OAuth login (QR code scan outside WeChat). Same request/response format as `/auth/wechat/mp/login`, uses Open Platform AppID/AppSecret.

**Error Codes:**

| Error Code | HTTP Status | Description |
|--------|-------------|------|
| `wechat_code_invalid` | 400 | WeChat authorization code invalid or expired |
| `wechat_unavailable` | 503 | WeChat service error |
| `wechat_unionid_missing` | 400 | Cannot obtain unionid |
| `session_expired` | 401 | Session expired, re-login required |

---

## 5. Share API (/share)

> **Pending** — Share-related endpoints are under design.
