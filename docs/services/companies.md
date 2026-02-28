---
icon: lucide/building-2
---

# Companies Service

Manage companies and developer access permissions.

## Usage

```python
from vclient import companies_service

companies = companies_service()
```

## Methods

### CRUD Operations

| Method                                        | Returns              | Description          |
| --------------------------------------------- | -------------------- | -------------------- |
| `get(company_id)`                             | `Company`            | Get a company by ID  |
| `create(CompanyCreate, **kwargs)`             | `NewCompanyResponse` | Create a new company |
| `update(company_id, CompanyUpdate, **kwargs)` | `Company`            | Update a company     |
| `delete(company_id)`                          | `None`               | Delete a company     |

### Pagination

| Method                      | Returns                      | Description                   |
| --------------------------- | ---------------------------- | ----------------------------- |
| `get_page(limit?, offset?)` | `PaginatedResponse[Company]` | Get a page of companies       |
| `list_all()`                | `list[Company]`              | Get all companies             |
| `iter_all(limit?)`          | `AsyncIterator[Company]`     | Iterate through all companies |

### Permissions

| Method                                               | Returns              | Description                               |
| ---------------------------------------------------- | -------------------- | ----------------------------------------- |
| `grant_access(company_id, developer_id, permission)` | `CompanyPermissions` | Grant, modify, or revoke developer access |

### Statistics

| Method                                         | Returns          | Description                    |
| ---------------------------------------------- | ---------------- | ------------------------------ |
| `get_statistics(company_id, num_top_traits=5)` | `RollStatistics` | Retrieve aggregated roll stats |

## Permission Levels

| Level    | Description                                 |
| -------- | ------------------------------------------- |
| `USER`   | View company data                           |
| `ADMIN`  | Modify company settings and data            |
| `OWNER`  | Full control including managing permissions |
| `REVOKE` | Remove all access                           |

!!! warning "Permission Considerations"

    Only company owners can grant or revoke permissions. You cannot revoke access from the last remaining owner of a company.

## Example

```python
from vclient.models import CompanyCreate, CompanyUpdate

# Create a company (preferred method: use model object)
request = CompanyCreate(
    name="Dark Haven Games",
    email="contact@darkhaven.com"
)
result = await companies.create(request)
company = result.company
admin_user = result.admin_user

# Alternative: pass fields as keyword arguments
result = await companies.create(
    name="Dark Haven Games",
    email="contact@darkhaven.com"
)

# Update company details
update = CompanyUpdate(name="Dark Haven Gaming")
updated = await companies.update(company.id, update)

# Grant admin access to another developer
permissions = await companies.grant_access(
    company_id=company.id,
    developer_id="507f1f77bcf86cd799439012",
    permission="ADMIN"
)
print(f"Granted {permissions.permission} access")
```

## Statistics

View aggregated dice roll statistics for a company.

```python
stats = await companies.get_statistics(company.id, num_top_traits=10)

print(f"Total rolls: {stats.total_rolls}")
print(f"Success rate: {stats.success_percentage:.1f}%")
print(f"Critical rate: {stats.criticals_percentage:.1f}%")
print(f"Botch rate: {stats.botch_percentage:.1f}%")
```

See [Response Models](../models/companies.md) for `Company`, `CompanySettings`, and related types.
