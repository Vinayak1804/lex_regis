# Software Requirements Specification (SRS)
## LEX REGIS: Enterprise-Grade AI-Powered Legal Technology Platform

### Document Control
- **Document Version:** 1.0.0
- **Status:** Approved / Ready for Academic & Industrial Submission
- **Target Platform:** Python 3.13+, Django 5.x, ASGI Channels, PostgreSQL/SQLite, Groq AI LLM

---

## 1. Introduction

### 1.1 Purpose
This Software Requirements Specification (SRS) document details the complete functional and non-functional requirements for the **LEX REGIS** Legal Technology Platform. It defines the operational requirements for citizen legal intake, AI analysis, advocate matching, enterprise case lifecycle tracking, hearing scheduling, document verification, real-time messaging, and judicial analytics.

### 1.2 Scope of the System
LEX REGIS provides a secure, multi-tenant digital ecosystem uniting:
1. **Citizens / Litigants:** Seeking affordable, structured legal triage and consultation.
2. **Advocates / Legal Practitioners:** Requiring high-efficiency matter management, hearing calendars, and client communication.
3. **Law Firms:** Requiring enterprise oversight, partner-associate delegations, and corporate billing.
4. **Judicial & Platform Administrators:** Overseeing compliance, verification, and audit telemetry.

---

## 2. Overall Description

### 2.1 Product Perspective
LEX REGIS operates as a modular web application powered by Django and ASGI WebSockets. It acts as an intermediary intelligence and management layer connecting citizens to certified legal counsel and maintaining tamper-evident audit trails.

### 2.2 User Characteristics
- **Citizens:** Non-technical individuals requiring simple grievance submission, plain-language legal explanations, and clear next steps.
- **Advocates:** Professional practitioners requiring high-density data tables, statutory references, calendar synchronizations, and compliance verification.
- **Administrators:** Technical operators conducting identity audits, monitoring AI request token loads, and maintaining master court entities.

---

## 3. Specific Requirements

### 3.1 Functional Requirements (FR)

#### FR-01: User Authentication & Role-Based Access Control
- The system shall support four distinct roles: `CLIENT`, `ADVOCATE`, `LAW_FIRM`, `ADMIN`.
- The system shall authenticate users via unique email addresses and passwords hashed using PBKDF2/SHA-256.
- The system shall provide a multi-step registration wizard for advocates capturing Bar Council enrollment numbers, practice specializations, and office locations.

#### FR-02: AI Legal Intake Wizard
- The system shall provide a dynamic multi-step wizard capturing:
  - Incident narrative / grievance description.
  - Incident date and geographic jurisdiction (State and District).
  - Urgency level (`ROUTINE`, `URGENT`, `EMERGENCY`).
  - Supporting documentary evidence.
- The system shall transmit the grievance to the Groq LLM API (`openai/gpt-oss-120b`) with a structured JSON schema.

#### FR-03: Statutory AI Analysis & Scoring
- The AI engine shall extract and return:
  - Broad legal category and specific practice area.
  - Case complexity (`Low`, `Medium`, `High`, `Critical`).
  - Suggested evidentiary documents.
  - Applicable legal enactments and statutory sections.
  - Key legal terms and step-by-step procedural recommendations.
  - Estimated timeline (e.g. "6-12 Months") and estimated cost.
  - Risk index (0-100) and confidence score (0-100).

#### FR-04: Intelligent Lawyer Matchmaking
- The system shall evaluate the generated `AIAnalysis` against registered `ProfessionalProfile` records.
- The matchmaker shall rank lawyers according to domain expertise, geographic jurisdiction, years of experience, and consultation fees.
- The system shall allow the citizen to submit a `ConsultationRequest` directly to the selected advocate.

#### FR-05: 13-Stage Enterprise Case State Engine
- The system shall support a 13-stage lifecycle state machine:
  `DRAFT` → `AI_ANALYSED` → `PENDING_ACCEPTANCE` → `LAWYER_ASSIGNED` → `CONSULTATION` → `EVIDENCE` → `LEGAL_NOTICE` → `PETITION` → `FILED` → `HEARINGS` → `JUDGEMENT` → `CLOSED` → `ARCHIVED`.
- All state transitions shall generate an immutable `CaseTimeline` audit record capturing event code, timestamp, and actor ID.

#### FR-06: Cryptographic Document Vault
- The system shall compute a SHA-256 cryptographic checksum for every uploaded file binary stream.
- The system shall maintain an immutable history of document updates through `DocumentVersion`.
- The system shall record document verification snapshots in `BlockchainRecord` storing simulated Ethereum transaction hashes and IPFS CIDs.

#### FR-07: Court Hearing & Adjournment Management
- The system shall support hearing scheduling with court room assignment, presiding judge, and scheduled start time.
- The system shall log hearing outcomes, actual durations, delay discrepancies, and formal adjournment records with reason codes.

#### FR-08: Real-Time WebSocket Communication
- The system shall provide bidirectional chat rooms over ASGI WebSockets (`ws://.../ws/chat/<conversation_id>/`).
- The system shall verify user participation permissions asynchronously prior to WebSocket connection acceptance.
- Chat messages shall be broadcast across Redis channel layers and persisted in the database.

---

## 4. Non-Functional Requirements (NFR)

### 4.1 Performance Requirements
- **Page Response Time:** Average server response time shall remain under 250ms for read requests.
- **AI Triage Latency:** Groq API inference round-trip shall complete within 2.5 seconds.
- **WebSocket Throughput:** Real-time message broadcast latency shall remain under 50ms.

### 4.2 Security Requirements
- **Session Protection:** Enforce 8-hour session lifetime and browser closure expiry.
- **Input Validation:** Enforce regex validation for Indian identity documents (Aadhaar, PAN) and Bar Council enrollment numbers.
- **Cross-Site Request Forgery:** CSRF protection shall be enforced on all non-idempotent HTTP requests.

### 4.3 Reliability & Maintainability
- The system shall maintain zero database corruption through atomic transactions (`@transaction.atomic`).
- Soft delete operations (`SoftDeleteMixin`) shall ensure historical auditability without physical row deletion.

---
*End of SRS — LEX REGIS Enterprise LegalTech Platform*
