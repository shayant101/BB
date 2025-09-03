# New User Sign-Up & Role Selection Flow

This diagram illustrates the end-to-end process for a new user signing up and selecting their role as either a Vendor or a Restaurant.

```mermaid
sequenceDiagram
    actor User
    participant FE_Clerk as Frontend (Clerk UI)
    participant Clerk
    participant BE_Webhook as Backend (Webhook)
    participant DB as Database
    participant FE_Role as Frontend (Role Selection Page)
    participant BE_API as Backend (API)

    User->>FE_Clerk: Fills out sign-up form
    FE_Clerk->>Clerk: Submits sign-up data
    Clerk-->>BE_Webhook: Fires "user.created" event
    BE_Webhook->>DB: Creates new User record (role is NULL)
    Clerk-->>FE_Clerk: Sign-up successful
    FE_Clerk->>FE_Role: Redirects user to /sign-up/role-selection

    User->>FE_Role: Clicks "I'm a Vendor"
    FE_Role->>BE_API: POST /api/profiles/set-role with {role: "vendor"}
    BE_API->>DB: Updates User record, sets role="vendor"
    BE_API-->>FE_Role: Returns success message
    FE_Role->>User: Redirects to /dashboard