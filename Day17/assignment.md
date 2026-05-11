# Day 17 — Agentic AI Business Use Cases

## Objective

Understand where **agentic AI** provides more business value than **traditional chatbots**.

- A **chatbot** typically answers questions or follows fixed scripts; it does not reliably *complete* work across systems.
- An **agent** reasons over goals, **uses tools** (APIs, databases, email), **branches** on results, and can run **multi-step workflows** with policies and human approval where needed.

---

## 1. HR Leave Management Agent

### Business task

Automatically process employee leave requests end-to-end: validate eligibility and dates, check balance, enforce policy rules, route for approval when required, persist the request in the HR system, block calendar time, and confirm back to the employee and manager.

### Why agentic AI is better than a chatbot

A chatbot can **explain** leave policy or FAQs. An agent can **execute** the workflow: query live balances, evaluate blackout dates or minimum notice rules, create records, send approvals, and update calendars. Value comes from **fewer manual handoffs**, **consistent policy application**, and **traceable audit steps**.

### Tools needed

| Tool | Role |
|------|------|
| HR database / HRIS API | Employee profile, grade, location, approval chain |
| PostgreSQL (or transactional store) | Authoritative balances, requests, audit log |
| Calendar API | Propose accepted time off; avoid double-booking |
| Email API | Notify employee, manager, HR; approval links |
| LLM API | Parse natural-language requests; plan steps; summarize errors |

*(Optional additions: SSO/identity for who is requesting; document RAG over employee handbook.)*

### Decision steps

1. **Intake** — Parse request (dates, type: sick/annual/unpaid). If ambiguous, ask a targeted clarification or use defaults per policy.
2. **Authenticate context** — Bind request to employee ID and employment status (active, probation, etc.).
3. **Check balance** — Read accrued/consumed leave; if insufficient for paid leave, branch to unpaid or rejection path.
4. **Validate dates** — Business calendar, blackout periods, minimum notice, overlap with existing approved leave.
5. **Approval routing** — If within auto-approval rules, mark approved; else create approval task and email approver.
6. **Persist** — Create or update leave request row; write audit event (who, what, when).
7. **Side effects** — On approval: update balance, create calendar holds, send confirmation email to employee.
8. **Confirm** — Send final status (approved / pending / rejected) with reason codes.

**Decision branches (summary):** insufficient balance → suggest alternatives or reject; needs approval → wait or timeout escalation; policy exception → flag HR review.

---

## 2. Customer Support Ticket Resolution Agent

### Business task

When a customer raises an issue (ticket, chat, or email), automatically **triage**, **investigate** using CRM and knowledge sources, **propose or apply** a resolution within allowed actions, **update the ticket**, and **reply** to the customer with a clear next step.

### Why agentic AI is better than a chatbot

A chatbot **answers** generic questions. An agent **owns the ticket**: it classifies severity, pulls account and order history, searches runbooks, may issue refunds or resets *only if* policy allows, escalates to humans for edge cases, and keeps the ticket system as the source of truth. Value is **faster mean time to resolve**, **consistent handling**, and **scalable L1 capacity**.

### Tools needed

| Tool | Role |
|------|------|
| Ticketing API | Create/update ticket, SLA fields, assignments |
| CRM system | Account health, subscriptions, contacts, recent cases |
| Knowledge base | Articles, FAQs, known-error database (often RAG) |
| Email API | Outbound replies; optional inbound parsing |
| LLM API | Classification, retrieval planning, drafted reply, tool-call orchestration |

*(Optional: billing/refund API, product admin APIs, Slack for internal escalation.)*

### Decision steps

1. **Normalize intake** — Map channel to ticket; dedupe if same customer/thread.
2. **Classify** — Category (billing, access, bug, how-to), severity, language.
3. **Retrieve context** — Customer tier, open orders, past tickets, churn risk flags.
4. **Search knowledge** — Top articles and internal notes; check for known outage.
5. **Resolution path** — If high-confidence match: draft fix (steps, links, credential reset).
6. **Action gate** — If resolution requires writes (refund, license reset): verify policy limits; otherwise escalate.
7. **Update ticket** — Status, resolution code, internal summary for future searches.
8. **Respond** — Send customer-facing message; if unresolved, set expectation and escalate queue.

**Decision branches (summary):** sensitive or high-severity → human required; ambiguous → ask one clarifying question; repeated failures → escalate with full timeline.

---

## 3. AI Sales Lead Qualification Agent

### Business task

When a lead arrives (web form, email, event scan), **enrich** the record, **score** fit and intent, **book** meetings for qualified leads, send **personalized follow-up**, and **update CRM** so sales works the right opportunities first.

### Why agentic AI is better than a chatbot

A chatbot **converses** on the website. An agent **operates on the funnel**: merges data from CRM and public signals, applies scoring rules, avoids double-booking, writes structured CRM fields for reporting, and sequences outreach. Value is **higher conversion**, **better rep time allocation**, and **cleaner pipeline data**.

### Tools needed

| Tool | Role |
|------|------|
| CRM database / API | Leads, contacts, accounts, owners, stages |
| Web search / enrichment APIs | Firmographic data, news, tech stack signals (where permitted) |
| Calendar API | Find slots, create holds, send invites |
| Email API | Sequences, meeting confirmations, handoff to AE |
| LLM API | Summarize lead, draft email, explain score drivers |

### Decision steps

1. **Capture** — Ingest form fields, source campaign, UTM, referrer.
2. **Dedupe** — Match to existing account/contact; merge or link.
3. **Enrich** — Company size, industry, geography, role seniority; flag missing required fields.
4. **Score** — ICP fit + intent signals; threshold for MQL vs nurture vs disqualify.
5. **Routing** — Assign owner by territory/segment/rules of engagement.
6. **Schedule** — If qualified and interested: propose times; book when accepted.
7. **Follow-up** — Send email with recap, agenda, and resources.
8. **CRM update** — Stage, score, tasks, timestamps, and rationale for auditing.

**Decision branches (summary):** below threshold → long-term nurture; duplicate open opp → notify owner; compliance block (region/industry) → no automated outreach.

---

## Final observation

Agentic AI delivers more business value than traditional chatbots when the job requires **multi-step reasoning**, **tool use** across real systems, **branching decisions** based on fresh data, and **completion** of a workflow—not just better conversational answers. Successful deployments add **policy gates**, **human approval** for risky actions, and **audit logs** so outcomes stay trustworthy and compliant.
