# REST API & WebSocket Protocol Specification
## LEX REGIS: Communication & Integration Contracts

---

## 1. RESTful Web Services

### 1.1 Authentication & Security
- **Authentication Standard:** JSON Web Tokens (JWT) using `rest_framework_simplejwt` and Session Cookies.
- **Authorization Header:** `Authorization: Bearer <access_token>`

### 1.2 Case Management Endpoints
- `GET /api/v1/cases/`: List all cases accessible to the authenticated user.
  - Query parameters: `?status=HEARINGS&q=search_term&practice_area=Corporate`
- `POST /api/v1/cases/`: Create a new case docket.
- `GET /api/v1/cases/{id}/`: Retrieve case details including parties, financials, and timeline.
- `PATCH /api/v1/cases/{id}/`: Update case metadata or status.

### 1.3 Document Vault Endpoints
- `GET /api/v1/documents/?case_id={id}`: List documents for a given case.
- `POST /api/v1/documents/upload/`: Multipart upload with automatic SHA-256 calculation.
- `POST /api/v1/documents/{id}/verify_blockchain/`: Trigger blockchain notarization and receipt creation.

### 1.4 Court Hearing Endpoints
- `GET /api/v1/hearings/`: Retrieve hearing schedule.
- `POST /api/v1/hearings/schedule/`: Schedule a new hearing with judge availability check.
- `POST /api/v1/hearings/{id}/adjourn/`: Record an adjournment with reason code.

---

## 2. Real-Time WebSocket Protocol

### 2.1 Connection URL
`ws://<domain>/ws/chat/<conversation_id>/`

### 2.2 Client Message Payload (JSON)
```json
{
  "message": "The written arguments have been uploaded to the document vault."
}
```

### 2.3 Server Broadcast Payload (JSON)
```json
{
  "message": "The written arguments have been uploaded to the document vault.",
  "sender_id": "8a32b21c-59f1-4712-9c3e-d901a8123456",
  "sender_name": "Adv. Rajesh Iyer",
  "created_at": "02:30 PM"
}
```

---
*End of API Specification — LEX REGIS*
