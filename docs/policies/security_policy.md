# LiberInk Project Security Policy

## 1. Purpose
The purpose of this document is to establish a unified set of mandatory requirements, principles, and constraints to ensure the security of the LiberInk software throughout its development, operation, and maintenance.

## 2. Scope
This policy applies to:
- Backend (ASP.NET Core Web API) and frontend (React.js, Kotlin) source code.
- The database (MySQL).
- Authentication and authorization processes (including password validation).
- Code storage (GitHub repository).

## 3. Roles and Responsibilities
- **Developer:** Responsible for writing secure code, ensuring the absence of hardcoded secrets, and verifying dependencies.
- **DB Administrator / DevOps:** Responsible for secure database configuration, server access management, and encryption key management.

## 4. Security Principles
- **Least Privilege:** Users and system components possess only the level of access necessary for their operations.
- **Default Deny:** All actions not explicitly permitted are prohibited.
- **No Secrets in Code:** Tokens, database passwords, and API keys are stored exclusively in environment variables or secure vaults and are never committed to the repository.

## 5. Secure Development Environment
- Direct pushes to the `master`/`main` branch are prohibited. All changes must be submitted via Pull Requests. - Mandatory use of a `.gitignore` file to exclude configuration files containing secrets (e.g., `appsettings.json` with connection strings).