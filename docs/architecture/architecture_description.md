# LiberInk Architecture Description

## 1. General Architecture
The project is built using a client-server architecture.
- **Backend:** ASP.NET Core Web API.
- **Frontend:** React.js, Kotlin.
- **Database:** MySQL.

## 2. Data Integrity Strategy
Data integrity is verified for user drafts and notes (`BookElement` model). Since users form requests on the client side, there is a risk of traffic interception or unauthorized data modification. To protect against tampering, the backend implements **AES-GCM (256-bit)** authenticated encryption via `EncryptionService`. During every database read operation, the algorithm validates the authentication tag (`Tag`/MAC) and initialization vector (`Nonce`). Any unauthorized modification of the ciphertext triggers a `CryptographicException`, immediately blocking access to compromised data.

## 3. Distribution and Licensing Model
- **Model:** SaaS (Software as a Service) — currently distributed as **Freeware** (MVP stage) with architectural readiness for **Freemium**.
- **Protection Mechanisms:** Critical business logic, data storage, and cryptographic keys reside exclusively on the server side (`ASP.NET Core Web API`). Access is controlled via Firebase JWT authentication and Discretionary Access Control (DAC) based on `UserId` ownership.
- **Justification for omitting local/hardcoded license checks:** Implementing local license files, hardware binding, or artificial hardcoded limits (such as capping the number of book elements) is impractical for a SaaS MVP, as it degrades user experience without adding real security. Because all operations are validated server-side, future Freemium restrictions (e.g., `is_premium` flags for export formats or cloud storage quotas) can be enabled directly in the database and API without risking client-side reverse engineering or bypass.

## 4. Client-Server Trust Model and Network Authorization
- **Distribution of Responsibilities:**
  - **Client Side (React.js, Kotlin):** Handles UI rendering, user input, local draft formatting, and secure storage of the authentication token. The client is treated as an untrusted environment; no cryptographic keys or final access control decisions reside on the client.
  - **Server Side (ASP.NET Core Web API):** Acts as the single source of truth. Handles database access (MySQL), AES-GCM encryption/decryption, input validation, and all authorization checks.
- **Network Authentication & Session State:** Stateless token-based authentication delegated to **Firebase Auth**. After login, the client receives a signed **JWT (JSON Web Token)** and attaches it to every API request via the `Authorization: Bearer <token>` HTTP header over HTTPS (TLS).
- **Server-Side Authorization:** On every protected endpoint, the ASP.NET Core middleware validates the JWT signature, expiration (`exp`), and issuer. The `UserId` is extracted exclusively from the verified token claims (never trusted from the request body) to enforce **Discretionary Access Control (DAC)**, ensuring users can only read or modify their own `BookElement` resources.

## 5. Logging, Monitoring, Backup, and Disaster Recovery
- **Structured Logging:** Backend services emit structured JSON logs with UTC ISO-8601 timestamps, severity levels (`INFO`, `WARNING`, `ERROR`, `CRITICAL`), component name, `request_id` for correlation, `user_id`, client IP, action, and result.
- **Logged Events & Data Sanitization:** Logs cover authentication (success/failure), access denials, CRUD operations on `BookElement`, database errors, and backup/recovery events. Passwords, JWT tokens, and encryption keys are strictly masked (`***REDACTED***`) before writing. Log rotation is configured by size/age with a 30-day retention policy.
- **Monitoring:** Key metrics include failed login rate per IP (brute-force threshold alert), HTTP 5xx error rate, API latency, and DB availability.
- **Backup Strategy (3-2-1 Principle):**
  - *Critical Data:* Production database (`MySQL` / `BookElements`, user metadata), server configuration, and encryption keys (stored separately in a secure vault). Caches and build artifacts are excluded.
  - *Schedule & Type:* Daily full backups + hourly incremental backups; stored in an isolated off-site cloud storage with 14-day retention.
  - *Integrity & Objectives:* Every backup is verified via **SHA-256** checksums and periodic test restores. Target **RPO = 1 hour**, **RTO = 30 minutes**.