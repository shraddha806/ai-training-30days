# Day 19 — Enterprise API Contract (Draft v1)

**Service name:** `CorpOps HR & Knowledge Gateway`  
**Audience:** Internal integrators (portals, mobile, automation agents).  
**Base URL (example):** `https://corpops-api.internal.example.com/api/v1`  
**Serialization:** JSON (`application/json`; UTF-8).  
**Versioning:** URL path `/v1`. Breaking changes bump major version.

---

## 1. Cross-cutting rules

### 1.1 Authentication & authorization

| Mechanism | Usage |
|-----------|--------|
| `Authorization: Bearer <jwt>` | Required on all endpoints (machine or user-delegated token). |

Scopes (examples encoded in JWT `scp`):

- `hr.leave.submit` — call leave submission.
- `hr.entitlements.read` — read entitlement snapshot.
- `knowledge.search` — search policy corpus.

Missing scope → **403** with `FORBIDDEN` code.

### 1.2 Idempotency (where applicable)

`POST /requests/leave/submit` accepts optional header:

- `Idempotency-Key: <uuid>` — replays within 24h return the **same** `request_id` and **201 Created** semantics (same body as first success).

### 1.3 Standard error envelope

All non-2xx responses use:

```json
{
  "error": {
    "code": "STRING_MACHINE_CODE",
    "message": "Human-readable summary",
    "details": [{}],
    "request_id": "uuid",
    "doc_url": "https://intranet.example.com/docs/errors/STRING_MACHINE_CODE"
  }
}
```

| HTTP | Typical `code` |
|------|----------------|
| 400 | `VALIDATION_FAILED`, `INVALID_DATE_RANGE` |
| 401 | `UNAUTHORIZED` |
| 403 | `FORBIDDEN`, `BLACKOUT_BLOCKED` |
| 404 | `EMPLOYEE_NOT_FOUND` |
| 409 | `INSUFFICIENT_BALANCE`, `DUPLICATE_PENDING_REQUEST` |
| 429 | `RATE_LIMITED` |
| 500 | `INTERNAL_ERROR` |

### 1.4 Pagination & limits (when applicable)

`POST /knowledge/search` uses cursor fields in response; max `page.size` server-enforced at 50.

### 1.5 Time & locale

All timestamps **ISO 8601** in **UTC**, e.g. `2026-05-11T14:30:00Z`.

---

## 2. Endpoint 1 — Submit leave request

### 2.1 Operation

```
POST /requests/leave/submit
```

Creates a structured leave **request record** for workflow and notifies approvers asynchronously.

### 2.2 Request headers

| Header | Required | Description |
|--------|----------|-------------|
| `Authorization` | Yes | Bearer JWT |
| `Content-Type` | Yes | `application/json` |
| `Idempotency-Key` | No | UUID for safe retries |

### 2.3 Request JSON schema (`application/json`)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["employee_id", "leave_type", "start_date", "end_date"],
  "properties": {
    "employee_id": {
      "type": "string",
      "pattern": "^[A-Z0-9]{6,12}$",
      "description": "Corporate employee identifier"
    },
    "leave_type": {
      "type": "string",
      "enum": ["ANNUAL", "SICK", "UNPAID", "PARENTAL", "BEREAVEMENT"],
      "description": "Approved leave taxonomy"
    },
    "start_date": {
      "type": "string",
      "format": "date",
      "description": "First calendar day absent (employee local TZ stored server-side)"
    },
    "end_date": {
      "type": "string",
      "format": "date",
      "description": "Last calendar day absent (inclusive)"
    },
    "half_day_policy": {
      "type": "string",
      "enum": ["NONE", "FIRST_HALF", "SECOND_HALF"],
      "default": "NONE",
      "description": "Applied only when range is exactly one calendar day"
    },
    "reason_code": {
      "type": "string",
      "maxLength": 64,
      "description": "Optional HR taxonomy code"
    },
    "notes_visible_to_approver": {
      "type": "string",
      "maxLength": 2000,
      "description": "Sanitized plaintext; HTML stripped server-side"
    }
  },
  "additionalProperties": false
}
```

### 2.4 Response **`201 Created`**

Headers: `Location: /requests/leave/{request_id}`

Body schema:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["request_id", "status", "submitted_at", "approval_route"],
  "properties": {
    "request_id": { "type": "string", "format": "uuid" },
    "status": {
      "type": "string",
      "enum": ["PENDING_APPROVAL", "AUTO_APPROVED", "REJECTED_BY_POLICY_GATE"]
    },
    "submitted_at": { "type": "string", "format": "date-time" },
    "consumed_calendar_days": { "type": "number", "minimum": 0.5 },
    "approval_route": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["step", "role", "assigned_to_party_id"],
        "properties": {
          "step": { "type": "integer", "minimum": 1 },
          "role": { "type": "string", "examples": ["LINE_MANAGER"] },
          "assigned_to_party_id": { "type": "string" }
        },
        "additionalProperties": false
      }
    },
    "policy_gate_messages": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Human-readable validations (warnings only if 201)"
    }
  },
  "additionalProperties": false
}
```

### 2.5 Example (minimal)

**Request**

```json
{
  "employee_id": "E884211",
  "leave_type": "ANNUAL",
  "start_date": "2026-06-02",
  "end_date": "2026-06-06",
  "notes_visible_to_approver": "Family travel; reachable on Teams."
}
```

**Response**

```json
{
  "request_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "PENDING_APPROVAL",
  "submitted_at": "2026-05-11T10:05:03Z",
  "consumed_calendar_days": 5,
  "approval_route": [
    {
      "step": 1,
      "role": "LINE_MANAGER",
      "assigned_to_party_id": "mgr-9921"
    }
  ],
  "policy_gate_messages": []
}
```

---

## 3. Endpoint 2 — Employee leave entitlements snapshot

### 3.1 Operation

```
GET /employees/{employee_id}/leave/entitlements
```

Returns **read-only** accrued/consumed summaries and blackout flags visible to callers with entitlement scope. **Never** returns raw payroll fields.

### 3.2 Path parameters

| Name | Type | Pattern |
|------|------|---------|
| `employee_id` | string | Same as Endpoint 1 |

### 3.3 Query parameters

| Name | Required | Description |
|------|----------|-------------|
| `as_of` | No | ISO `date`; default server “today UTC” |

### 3.4 Response **`200 OK`**

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["employee_id", "as_of", "currency", "buckets"],
  "properties": {
    "employee_id": { "type": "string" },
    "as_of": { "type": "string", "format": "date" },
    "currency": { "type": "string", "const": "DAYS_DECIMAL" },
    "buckets": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["leave_type", "accrued", "consumed", "pending_reserved", "available"],
        "properties": {
          "leave_type": {
            "type": "string",
            "enum": ["ANNUAL", "SICK", "UNPAID", "PARENTAL", "BEREAVEMENT"]
          },
          "accrued": { "type": "number" },
          "consumed": { "type": "number" },
          "pending_reserved": { "type": "number", "minimum": 0 },
          "available": { "type": "number" },
          "policy_notes": { "type": "array", "items": { "type": "string" } }
        },
        "additionalProperties": false
      }
    },
    "calendar_flags": {
      "type": "object",
      "properties": {
        "probation_restricted_until": {
          "oneOf": [
            { "type": "string", "format": "date" },
            { "type": "null" }
          ]
        },
        "blackout_window_ids": {
          "type": "array",
          "items": { "type": "string" }
        }
      },
      "additionalProperties": false
    }
  },
  "additionalProperties": false
}
```

### 3.5 Example

```json
{
  "employee_id": "E884211",
  "as_of": "2026-05-11",
  "currency": "DAYS_DECIMAL",
  "buckets": [
    {
      "leave_type": "ANNUAL",
      "accrued": 22.5,
      "consumed": 8.0,
      "pending_reserved": 5.0,
      "available": 9.5,
      "policy_notes": []
    }
  ],
  "calendar_flags": {
    "probation_restricted_until": null,
    "blackout_window_ids": ["Q4_EMBARGO_NA"]
  }
}
```

---

## 4. Endpoint 3 — Policy & knowledge article search

### 4.1 Operation

```
POST /knowledge/search
```

Hybrid **keyword + snippet retrieval** gateway (underlying engine may be OpenSearch + vector DB). Returns **citability metadata** only; bulk document download is separate.

### 4.2 Request schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["query"],
  "properties": {
    "query": {
      "type": "string",
      "minLength": 3,
      "maxLength": 400,
      "description": "Natural language or quoted keywords"
    },
    "corpus_filters": {
      "type": "object",
      "properties": {
        "audience_roles": {
          "type": "array",
          "items": {
            "type": "string",
            "enum": ["EMPLOYEE", "MANAGER", "HR_BP"]
          },
          "default": ["EMPLOYEE"]
        },
        "jurisdiction": {
          "type": "array",
          "items": {
            "type": "string",
            "examples": ["IN-KA", "US-CA"]
          }
        },
        "doc_sources": {
          "type": "array",
          "items": {
            "type": "string",
            "enum": ["HANDBOOK", "FAQ", "SECURITY", "BENEFITS"]
          },
          "default": ["HANDBOOK", "FAQ"]
        },
        "effective_before": {
          "type": "string",
          "format": "date",
          "description": "Prefer policies effective on/before date"
        }
      },
      "additionalProperties": false
    },
    "page": {
      "type": "object",
      "properties": {
        "cursor": { "type": "string", "description": "Opaque from prior response" },
        "size": { "type": "integer", "minimum": 1, "maximum": 50, "default": 10 }
      },
      "additionalProperties": false
    },
    "include_snippets": { "type": "boolean", "default": true }
  },
  "additionalProperties": false
}
```

### 4.3 Response **`200 OK`**

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["hits", "search_request_id"],
  "properties": {
    "search_request_id": { "type": "string", "format": "uuid" },
    "hits": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["doc_ref", "title", "confidence", "effective_window"],
        "properties": {
          "doc_ref": {
            "type": "string",
            "description": "Stable internal document key"
          },
          "title": { "type": "string", "maxLength": 280 },
          "confidence": {
            "type": "number",
            "minimum": 0,
            "maximum": 1
          },
          "effective_window": {
            "type": "object",
            "required": ["start", "end"],
            "properties": {
              "start": { "type": "string", "format": "date" },
              "end": {
                "oneOf": [{ "type": "string", "format": "date" }, { "type": "null" }]
              }
            },
            "additionalProperties": false
          },
          "snippets": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["text", "char_span"],
              "properties": {
                "text": { "type": "string", "maxLength": 500 },
                "char_span": {
                  "type": "array",
                  "minItems": 2,
                  "maxItems": 2,
                  "items": { "type": "integer" }
                }
              },
              "additionalProperties": false
            }
          },
          "source": {
            "type": "string",
            "enum": ["HANDBOOK", "FAQ", "SECURITY", "BENEFITS"]
          }
        },
        "additionalProperties": false
      }
    },
    "next_page_cursor": {
      "type": ["string", "null"]
    },
    "degraded_modes": {
      "type": "array",
      "items": {
        "type": "string",
        "examples": ["VECTOR_INDEX_WARM"]
      },
      "description": "Operational transparency when partial availability"
    }
  },
  "additionalProperties": false
}
```

### 4.4 Example (abbreviated)

**Request**

```json
{
  "query": "manager approval consecutive annual leave more than three days",
  "corpus_filters": {
    "audience_roles": ["EMPLOYEE"],
    "doc_sources": ["HANDBOOK", "FAQ"],
    "effective_before": "2026-05-11"
  },
  "page": { "size": 5 },
  "include_snippets": true
}
```

**Response**

```json
{
  "search_request_id": "b2c91e4a-d2f1-4c4b-a3fa-019e3d441200",
  "hits": [
    {
      "doc_ref": "HANDBOOK-2025-LEAVE-03",
      "title": "Annual leave approval thresholds",
      "confidence": 0.91,
      "effective_window": { "start": "2025-01-01", "end": null },
      "snippets": [
        {
          "text": "Requests exceeding three consecutive business days require line manager approval.",
          "char_span": [120, 198]
        }
      ],
      "source": "HANDBOOK"
    }
  ],
  "next_page_cursor": null,
  "degraded_modes": []
}
```

---

## 5. Contract summary table

| Method & path | Purpose | Auth scope |
|---------------|---------|------------|
| `POST /requests/leave/submit` | Create leave request + route | `hr.leave.submit` |
| `GET /employees/{id}/leave/entitlements` | Balances & flags | `hr.entitlements.read` |
| `POST /knowledge/search` | Policy article discovery | `knowledge.search` |

---

## 6. Out of scope (v1)

- Webhooks / event subscriptions (future `.../subscriptions`).
- Bulk export of full PDFs (separate media download API).
- GraphQL or gRPC (REST only in this contract).

This document is sufficient for **OpenAPI 3.1** generation as a follow-on task; schemas above are the **authoritative payload shapes** for Day 19.
