---
icon: lucide/search
---

# User Lookup Models

Models for cross-company user lookup responses.

## UserLookupResult

Each result represents a company where the looked-up person has a user record.

| Field          | Type       | Description                                         |
| -------------- | ---------- | --------------------------------------------------- |
| `company_id`   | `str`      | Company identifier                                  |
| `company_name` | `str`      | Company display name                                |
| `user_id`      | `str`      | User identifier within the company                  |
| `role`         | `UserRole` | User's role (ADMIN, STORYTELLER, PLAYER, UNAPPROVED, DEACTIVATED) |
