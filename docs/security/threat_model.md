# LiberInk Project Threat Model

## 1. Scope of the Analyzed System
The threat model covers user authentication processes, API operations (ASP.NET Core), and access to the MySQL database where texts are stored.

## 2. Attacker Model
- **External Unauthenticated User:** Has access only to public endpoints (registration, login). Goal: password guessing, DDoS attacks.
- **Authenticated Legitimate User:** Has access to their own documents. Goal: attempting to access other users' documents or escalating privileges to Administrator.

## 3. Threat Analysis using the STRIDE Methodology

### S - Spoofing
- **Threat:** An attacker might attempt to guess a user's password and log in as that user.
- **Protection (Mitigation):** Implementation of a strict password policy (Option 5: mandatory inclusion of digits and punctuation marks); account lockout after 3 failed login attempts.

### T - Tampering
- **Threat:** An attacker or authorized user intercepts a request and attempts to modify the document ID (Text/Note) to edit another user's text.
- **Protection:** Access rights verification at the backend level (validating the JWT token and checking that the `UserId` matches the document owner in the database).

### R - Repudiation
- **Threat:** A user deletes an important shared document and denies having done so. - **Protection:** Logging of critical server events.

### I - Information Disclosure
- **Threat:** Database compromise and password leakage.
- **Protection:** Passwords are stored exclusively as secure hashes. HTTPS is used for data transmission between the client (React/Kotlin) and the API.

### D - Denial of Service
- **Threat:** Mass request submission to the login endpoint (brute-force attack) to overload the server.
- **Protection:** Rate limiting configured at the ASP.NET Core API level.

### E - Elevation of Privilege
- **Threat:** A regular user attempts to access an administrator endpoint (e.g., viewing all users).
- **Protection:** Use of Role-Based Access Control (RBAC). Role validation via the `[Authorize(Roles = "Admin")]` attribute.