# OpenStocki Gateway API 接口文档

**Base URL:** `https://api.stocki.com.cn`

## 1. 通用约定

### 鉴权

所有需要鉴权的接口使用统一的 Bearer Token 方式：

```
Authorization: Bearer <token>
```

Token 由用户在 H5 管理页生成，格式为 `sk_` 前缀 + 随机字符串（如 `sk_abc123def456...`）。

Token 类型：
- **API Key**: `sk_` 前缀，用于 `/v1/*` 业务接口
- **Session Token**: `sess_` 前缀，用于 `/user/*` 用户管理接口，通过微信 OAuth 登录获取

| 适用范围 | 说明 |
|---|---|
| `/v1/*` 业务接口 | 需要 API Key（`sk_xxx`） |
| `/user/*` 用户管理接口 | 需要 Session Token（`sess_xxx`） |
| `/auth/*` 微信登录接口 | 无需鉴权 |
| `/share/{id}` 公开分享页 | 无需鉴权 |

### 通用请求头

```
Content-Type: application/json
Authorization: Bearer <token>
```

### 错误响应格式

所有错误响应遵循统一信封结构：

```json
{
  "error": "<machine-readable-code>",
  "message": "人类可读的错误说明",
  "details": {}
}
```

### 错误码表

| 错误码 | HTTP 状态码 | 说明 |
|---|---|---|
| `auth_missing` | 401 | 未提供鉴权凭证 |
| `auth_invalid` | 401 | 凭证无效或已过期 |
| `quota_exceeded` | 403 | 今日额度已用完 |
| `task_not_found` | 404 | task_id 不存在 |
| `run_not_found` | 404 | run_id 不存在 |
| `run_error` | 200 | Quant 运行失败（在 status response body 中，非 HTTP 错误） |
| `report_not_found` | 404 | 报告文件不存在 |
| `rate_limited` | 429 | 请求频率超限（`details` 含 `retry_after`）；或全局 quant 队列满 |
| `timezone_invalid` | 400 | 非法 IANA 时区名称 |
| `stocki_unavailable` | 503 | 后端分析服务不可用 |

---

## 2. 业务 API（/v1）

### POST /v1/instant

提交即时查询。同步阻塞，超时 120 秒。

**请求：**

```json
POST /v1/instant
Authorization: Bearer sk_abc123def456
Content-Type: application/json

{
  "question": "A股半导体行业前景如何？",
  "timezone": "Asia/Shanghai"
}
```

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `question` | string | 是 | 查询内容 |
| `timezone` | string | 否 | IANA 时区名，默认 `"Asia/Shanghai"` |

**成功响应：**

```json
HTTP/1.1 200 OK

{
  "answer": "## A股半导体行业前景分析\n\n### 当前市场表现\n半导体板块近期受益于国产替代加速...",
  "share_url": "https://stocki.com.cn/s/x7k9m2",
  "usage": {
    "used_today": 3,
    "daily_quota": 8
  }
}
```

| 字段 | 类型 | 说明 |
|---|---|---|
| `answer` | string | Markdown 格式的回答 |
| `share_url` | string | 自动生成的分享短链接 |
| `usage.used_today` | int | 今日已用次数 |
| `usage.daily_quota` | int | 每日总额度 |

**错误响应示例：**

```json
// 额度不足
HTTP/1.1 403 Forbidden

{
  "error": "quota_exceeded",
  "message": "今日免费查询次数已用完",
  "details": {
    "used_today": 8,
    "daily_quota": 8,
    "invite_url": "https://stocki.com.cn/r/STOCK8K"
  }
}
```

```json
// 服务不可用
HTTP/1.1 503 Service Unavailable

{
  "error": "stocki_unavailable",
  "message": "分析服务暂时不可用，请稍后重试",
  "details": {}
}
```

---

### POST /v1/quant

提交异步量化分析。立即返回，不阻塞。

- 不传 `task_id`：Gateway 自动创建新 task 并提交首次 run
- 传 `task_id`：向已有 task 追加新 run（迭代分析）

Gateway 根据 `question` 自动生成 `task_name`。

> **全局串行约束：** 同一时间只允许一个 quant run 运行。如果已有运行中的 quant，新提交会被拒绝（429），而非排队等待。

**请求（新任务）：**

```json
POST /v1/quant
Authorization: Bearer sk_abc123def456
Content-Type: application/json

{
  "question": "回测沪深300动量策略，回看期60天，2024年至今",
  "timezone": "Asia/Shanghai"
}
```

**请求（追加迭代）：**

```json
POST /v1/quant
Authorization: Bearer sk_abc123def456
Content-Type: application/json

{
  "question": "增加小盘股过滤器，回看期改为90天",
  "task_id": "t_8f3a1b2c",
  "timezone": "Asia/Shanghai"
}
```

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `question` | string | 是 | 分析问题 |
| `task_id` | string | 否 | 已有任务 ID；不传则自动创建新 task |
| `timezone` | string | 否 | IANA 时区名，默认 `"Asia/Shanghai"` |

**成功响应（新任务）：**

```json
HTTP/1.1 201 Created

{
  "task_id": "t_8f3a1b2c",
  "task_name": "A股动量策略回测"
}
```

**成功响应（追加迭代）：**

```json
HTTP/1.1 201 Created

{
  "task_id": "t_8f3a1b2c",
  "task_name": "A股动量策略回测"
}
```

| 字段 | 类型 | 说明 |
|---|---|---|
| `task_id` | string | 任务 ID（新建或已有） |
| `task_name` | string | 任务名称（新建时自动生成，已有时返回原名称） |

**错误响应示例：**

```json
// 全局 quant 队列满
HTTP/1.1 429 Too Many Requests

{
  "error": "rate_limited",
  "message": "已有量化分析正在运行，请稍后重试",
  "details": {
    "retry_after": 60,
    "active_task_id": "t_other123",
    "active_run_id": "run_003"
  }
}
```

```json
// 额度不足
HTTP/1.1 403 Forbidden

{
  "error": "quota_exceeded",
  "message": "今日额度已用完",
  "details": {
    "used_today": 8,
    "daily_quota": 8,
    "invite_url": "https://stocki.com.cn/r/STOCK8K"
  }
}
```

```json
// task_id 不存在
HTTP/1.1 404 Not Found

{
  "error": "task_not_found",
  "message": "任务不存在",
  "details": {}
}
```

---

### GET /v1/tasks

列出当前用户的所有量化任务，按最近更新时间倒序。

**请求：**

```
GET /v1/tasks
Authorization: Bearer sk_abc123def456
```

**成功响应：**

```json
HTTP/1.1 200 OK

{
  "tasks": [
    {
      "task_id": "t_8f3a1b2c",
      "name": "A股动量策略回测",
      "description": null,
      "created_at": "2026-03-23T14:30:00+08:00",
      "updated_at": "2026-03-23T15:45:00+08:00",
      "message_count": 4
    },
    {
      "task_id": "t_5e2d1a0b",
      "name": "US Macro Outlook",
      "description": "2026 Q1 美国宏观经济展望",
      "created_at": "2026-03-20T09:00:00+08:00",
      "updated_at": "2026-03-21T10:30:00+08:00",
      "message_count": 6
    }
  ]
}
```

| 字段 | 类型 | 说明 |
|---|---|---|
| `tasks[].task_id` | string | 任务 ID |
| `tasks[].name` | string | 任务名称 |
| `tasks[].description` | string? | 描述，可为 null |
| `tasks[].created_at` | string | ISO-8601 创建时间 |
| `tasks[].updated_at` | string | ISO-8601 最近更新时间 |
| `tasks[].message_count` | int | 消息数（human + ai） |

**无任务时返回空数组：**

```json
HTTP/1.1 200 OK

{
  "tasks": []
}
```

---

### GET /v1/tasks/{task_id}

查询任务详情和运行状态。

**请求：**

```
GET /v1/tasks/t_8f3a1b2c
Authorization: Bearer sk_abc123def456
```

**成功响应（有运行中的 run）：**

```json
HTTP/1.1 200 OK

{
  "task_id": "t_8f3a1b2c",
  "name": "A股动量策略回测",
  "created_at": "2026-03-23T14:30:00+08:00",
  "updated_at": "2026-03-23T15:45:00+08:00",
  "current_run": {
    "run_id": "run_002",
    "query": "增加小盘股过滤器，回看期改为90天",
    "status": "running",
    "started_at": "2026-03-23T15:40:00+08:00"
  },
  "runs": [
    {
      "run_id": "run_001",
      "query": "回测沪深300动量策略，回看期60天，2024年至今",
      "status": "success",
      "summary": "沪深300动量策略年化收益18.3%，夏普比率1.2，最大回撤-15%",
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
      "query": "增加小盘股过滤器，回看期改为90天",
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

**成功响应（run 失败）：**

```json
HTTP/1.1 200 OK

{
  "task_id": "t_8f3a1b2c",
  "name": "A股动量策略回测",
  "created_at": "2026-03-23T14:30:00+08:00",
  "updated_at": "2026-03-23T16:00:00+08:00",
  "current_run": null,
  "runs": [
    {
      "run_id": "run_003",
      "query": "使用无效参数进行回测",
      "status": "error",
      "summary": null,
      "started_at": "2026-03-23T15:50:00+08:00",
      "completed_at": "2026-03-23T16:00:00+08:00",
      "error_message": "回测参数无效：回看期不能为负数",
      "report": null,
      "files": []
    }
  ]
}
```

| 字段 | 类型 | 说明 |
|---|---|---|
| `task_id` | string | 任务 ID |
| `name` | string | 任务名称 |
| `created_at` | string | ISO-8601 创建时间 |
| `updated_at` | string | ISO-8601 更新时间 |
| `current_run` | object? | 当前运行中的 run，无则为 null |
| `runs[]` | array | 全部 run 列表 |
| `runs[].run_id` | string | 运行 ID |
| `runs[].query` | string | 查询内容 |
| `runs[].status` | string | `"queued"` / `"running"` / `"success"` / `"error"` |
| `runs[].summary` | string? | 结果摘要（成功时有值） |
| `runs[].started_at` | string | ISO-8601 开始时间 |
| `runs[].completed_at` | string? | ISO-8601 完成时间，未完成为 null |
| `runs[].error_message` | string? | 错误信息（status=error 时有值） |
| `runs[].report` | string? | 主报告 COS 路径 |
| `runs[].files` | array | 结果文件路径列表 |

**错误响应：**

```json
HTTP/1.1 404 Not Found

{
  "error": "task_not_found",
  "message": "任务不存在",
  "details": {}
}
```

---

### GET /v1/tasks/{task_id}/files/{path}

下载任务结果文件（报告、图表等）。Gateway 从 Tencent COS 代理返回。

**请求（Markdown 报告）：**

```
GET /v1/tasks/t_8f3a1b2c/files/runs/run_001/report.md
Authorization: Bearer sk_abc123def456
```

**成功响应：**

```
HTTP/1.1 200 OK
Content-Type: text/markdown; charset=utf-8

# 沪深300动量策略回测报告

## 策略参数
- 标的：沪深300成分股
- 回看期：60天
- 回测区间：2024-01-01 至 2026-03-23

## 回测结果
| 指标 | 值 |
|---|---|
| 年化收益率 | 18.3% |
| 夏普比率 | 1.2 |
| 最大回撤 | -15.2% |
| 胜率 | 58.7% |

## 收益曲线
![收益曲线](images/chart_001.png)
```

**请求（图片文件）：**

```
GET /v1/tasks/t_8f3a1b2c/files/runs/run_001/images/chart_001.png
Authorization: Bearer sk_abc123def456
```

**成功响应：**

```
HTTP/1.1 200 OK
Content-Type: image/png
Content-Length: 45678

<binary PNG data>
```

**错误响应：**

```json
HTTP/1.1 404 Not Found

{
  "error": "report_not_found",
  "message": "文件 'runs/run_001/report.md' 不存在",
  "details": {}
}
```

---

## 3. 用户 API（/user）

### `GET /user/me`

获取当前用户信息（需要 Session Token 鉴权）。

**响应 200：**
```json
{
  "id": "u_abc123",
  "nickname": "微信用户昵称",
  "avatar_url": "https://...",
  "api_key": "sk_test1234..."
}
```

`api_key` 为遮罩显示（前缀 + `...`），完整 Key 仅在创建时展示一次。

---

## 4. 微信登录 API（/auth/wechat）

### `POST /auth/wechat/mp/login`

公众号 OAuth 登录（微信内浏览器）。无需鉴权。

**请求：**
```json
{
  "code": "微信回调的授权 code"
}
```

**响应 200：**
```json
{
  "session_token": "sess_xxx",
  "user": {
    "id": "u_xxx",
    "nickname": "微信昵称",
    "avatar_url": "头像 URL"
  },
  "api_key": "sk_xxx（仅首次注册时返回完整值，否则为 null）",
  "is_new_user": true
}
```

### `POST /auth/wechat/open/login`

开放平台 OAuth 登录（微信外扫码）。请求/响应格式同 `/auth/wechat/mp/login`，区别在于使用开放平台 AppID/AppSecret。

**错误码：**

| 错误码 | HTTP 状态码 | 说明 |
|--------|-------------|------|
| `wechat_code_invalid` | 400 | 微信授权码无效或已过期 |
| `wechat_unavailable` | 503 | 微信服务异常 |
| `wechat_unionid_missing` | 400 | 无法获取 unionid |
| `session_expired` | 401 | Session 已过期，需重新登录 |

---

## 5. 分享 API（/share）

> **待定** — 分享相关接口设计中，后续补充。
