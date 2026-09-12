# System Architecture Document (SAD)
## LEX REGIS: Modular Monolithic Architecture & Layered Domain Design

---

## 1. Architectural Philosophy

LEX REGIS is architected around the **Modular Monolith** pattern with strict **Service-Selector Layering**. This architecture balances ease of deployment, cohesive data modeling, and low latency while maintaining strict domain encapsulation.

```mermaid
graph TD
    subgraph Client Layer
        WebBrowser[Modern Web Browser - HTML5 / HTMX / Alpine.js]
        MobileBrowser[Mobile Web Client]
    end

    subgraph Edge & Reverse Proxy Layer
        Nginx[Nginx Reverse Proxy & SSL Termination]
    end

    subgraph Application Server Layer (ASGI / WSGI)
        DaphneCluster[Daphne ASGI Web & WebSocket Server Cluster]
    end

    subgraph Service & Domain Layer
        AccountsApp[apps.accounts: RBAC & Profiles]
        IntakeApp[apps.intake: Citizen Intake & Matchmaker]
        CasesApp[apps.cases: State Machine & Financials]
        DocsApp[apps.documents: SHA-256 Document Vault]
        HearingsApp[apps.hearings: Courtroom Scheduling]
        AIApp[apps.ai: Groq LLM Client & Telemetry]
        BlockchainApp[apps.blockchain: Ledger Immutability Engine]
        CommsApp[apps.communication: WebSocket Consumers]
        AnalyticsApp[apps.analytics: Judicial Statistics Engine]
    end

    subgraph Data & Storage Layer
        PostgresDB[(PostgreSQL / SQLite Database)]
        RedisLayer[(Redis In-Memory Channel Layer & Cache)]
        MediaVault[Encrypted File Storage: Evidence & Documents]
    end

    subgraph External Intelligence
        GroqAPI[Groq Cloud LLM API: openai/gpt-oss-120b]
    end

    Client Layer <--> Nginx
    Nginx <--> DaphneCluster
    
    DaphneCluster --> Service & Domain Layer
    Service & Domain Layer <--> PostgresDB
    Service & Domain Layer <--> RedisLayer
    Service & Domain Layer <--> MediaVault
    AIApp <--> GroqAPI
```

---

## 2. The Service-Selector Pattern

To maintain clean separation between business logic and database queries, each app defines:

1. **`services/` (Mutations):**
   - Implements transactional state changes.
   - Interacts with external systems (Groq API, file hashing, blockchain receipts).
   - Wrapped in `@transaction.atomic`.
2. **`selectors/` (Queries):**
   - Returns optimized `QuerySet` instances.
   - Applies prefetching (`select_related`, `prefetch_related`) to prevent N+1 query problems.
   - Enforces user isolation filters for multi-tenant data access.
3. **`presentation/` (Views & Presenters):**
   - Class-based views that orchestrate selectors and services.
   - Uses `DashboardPresenter`, `CasePresenter`, and `AuthPresenter` to construct view-models.

---

## 3. Base Model Layer & Cross-Cutting Concerns

All domain models inherit from `apps.common.models.base.BaseModel`, inheriting:
- `UUIDMixin`: Globally unique 128-bit UUID primary keys.
- `TimestampMixin`: Indexed `created_at` and `updated_at` timestamps.
- `SoftDeleteMixin`: `is_deleted`, `deleted_at`, `deleted_by` fields, preventing accidental data loss.
- `OwnershipMixin`: `created_by` and `updated_by` user foreign keys.
- `AuditMixin`: `is_active` status flag.

---
*End of Architecture Specification — LEX REGIS*
