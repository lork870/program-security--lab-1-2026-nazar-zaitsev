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