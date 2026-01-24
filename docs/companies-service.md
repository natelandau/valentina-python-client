# Companies Service

The Companies Service provides methods to create, retrieve, update, and delete companies, as well as manage developer access permissions.

## Usage

```python
from vclient import companies_service

companies = companies_service()
```

## Methods

### `get_page()`

Retrieve a paginated page of companies you have access to.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | `int` | `10` | Maximum number of items to return (0-100) |
| `offset` | `int` | `0` | Number of items to skip from the beginning |

**Returns:** `PaginatedResponse[Company]`

**Example:**

```python
page = await companies.get_page(limit=10, offset=0)
print(f"Total companies: {page.total}")
print(f"Current page: {page.current_page} of {page.total_pages}")

for company in page.items:
    print(company.name)
```

---

### `list_all()`

Retrieve all companies you have access to. Automatically paginates through all results.

**Returns:** `list[Company]`

**Example:**

```python
all_companies = await companies.list_all()
for company in all_companies:
    print(company.name)
```

---

### `iter_all()`

Iterate through all companies with memory-efficient streaming.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | `int` | `100` | Items per page |

**Yields:** `Company`

**Example:**

```python
async for company in companies.iter_all():
    print(company.name)
```

---

### `get()`

Retrieve detailed information about a specific company.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `company_id` | `str` | The ID of the company to retrieve |

**Returns:** `Company`

**Raises:**

- `NotFoundError`: If the company does not exist
- `AuthorizationError`: If you don't have access to the company

**Example:**

```python
company = await companies.get("507f1f77bcf86cd799439011")
print(f"Name: {company.name}")
print(f"Email: {company.email}")
print(f"Created: {company.date_created}")
```

---

### `create()`

Create a new company. You are automatically granted OWNER permission for the new company.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | `str` | Yes | Company name (3-50 characters) |
| `email` | `str` | Yes | Company contact email |
| `description` | `str \| None` | No | Company description (min 3 characters) |
| `settings` | `CompanySettings \| None` | No | Company settings configuration |

**Returns:** `Company`

**Raises:**

- `ValidationError`: If the request data is invalid

**Example:**

```python
from vclient.api.models import CompanySettings

# Create with minimal fields
company = await companies.create(
    name="My Company",
    email="contact@example.com",
)

# Create with all fields
settings = CompanySettings(
    character_autogen_xp_cost=15,
    permission_manage_campaign="STORYTELLER",
)
company = await companies.create(
    name="My Company",
    email="contact@example.com",
    description="A great company",
    settings=settings,
)
```

---

### `update()`

Modify a company's properties. Only include fields that need to be changed.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `company_id` | `str` | Yes | The ID of the company to update |
| `name` | `str \| None` | No | New company name (3-50 characters) |
| `email` | `str \| None` | No | New company contact email |
| `description` | `str \| None` | No | New company description |
| `settings` | `CompanySettings \| None` | No | New company settings |

**Returns:** `Company`

**Raises:**

- `NotFoundError`: If the company does not exist
- `AuthorizationError`: If you don't have admin-level access
- `ValidationError`: If the request data is invalid

**Example:**

```python
updated = await companies.update(
    "507f1f77bcf86cd799439011",
    name="New Company Name",
)
```

---

### `delete()`

Delete a company from the system. This is a destructive action that archives the company and all associated data.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `company_id` | `str` | The ID of the company to delete |

**Returns:** `None`

**Raises:**

- `NotFoundError`: If the company does not exist
- `AuthorizationError`: If you don't have owner-level access

**Example:**

```python
await companies.delete("507f1f77bcf86cd799439011")
```

---

### `grant_access()`

Add, update, or revoke a developer's permission level for a company.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `company_id` | `str` | The ID of the company |
| `developer_id` | `str` | The ID of the developer to grant/modify access for |
| `permission` | `PermissionLevel` | The permission level (`USER`, `ADMIN`, `OWNER`, or `REVOKE`) |

**Returns:** `CompanyPermissions`

**Raises:**

- `NotFoundError`: If the company or developer does not exist
- `AuthorizationError`: If you don't have owner-level access
- `ValidationError`: If trying to remove the last owner

**Example:**

```python
permissions = await companies.grant_access(
    company_id="507f1f77bcf86cd799439011",
    developer_id="507f1f77bcf86cd799439012",
    permission="ADMIN",
)
print(f"Granted {permissions.permission} access to {permissions.name}")
```

## Response Models

### `Company`

Represents a company entity returned from the API.

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | MongoDB document ObjectID |
| `date_created` | `datetime` | Timestamp when the company was created |
| `date_modified` | `datetime` | Timestamp when the company was last modified |
| `name` | `str` | Company name |
| `description` | `str \| None` | Company description |
| `email` | `str` | Company contact email |
| `user_ids` | `list[str]` | List of user IDs associated with the company |
| `settings` | `CompanySettings \| None` | Company settings and configuration |

### `CompanySettings`

Configuration options for a company.

| Field | Type | Description |
|-------|------|-------------|
| `character_autogen_xp_cost` | `int \| None` | Cost to autogen XP for a character (0-100) |
| `character_autogen_num_choices` | `int \| None` | Number of characters generated for selection (1-10) |
| `permission_manage_campaign` | `ManageCampaignPermission \| None` | Permission level for managing campaigns |
| `permission_grant_xp` | `GrantXPPermission \| None` | Permission level for granting XP |
| `permission_free_trait_changes` | `FreeTraitChangesPermission \| None` | Permission level for free trait changes |

### `CompanyPermissions`

Response from granting or modifying developer access.

| Field | Type | Description |
|-------|------|-------------|
| `company_id` | `str` | The company ID |
| `name` | `str \| None` | The company name |
| `permission` | `PermissionLevel` | The permission level granted |

### `PaginatedResponse[Company]`

Paginated response structure for company listings.

| Field | Type | Description |
|-------|------|-------------|
| `items` | `list[Company]` | The requested page of results |
| `limit` | `int` | The limit that was applied |
| `offset` | `int` | The offset that was applied |
| `total` | `int` | Total number of items across all pages |

**Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `has_more` | `bool` | Whether there are more pages available |
| `next_offset` | `int` | The offset for the next page |
| `total_pages` | `int` | Total number of pages |
| `current_page` | `int` | Current page number (1-indexed) |

## Permission Levels

| Level | Description |
|-------|-------------|
| `USER` | Basic access to view company data |
| `ADMIN` | Can modify company settings and data |
| `OWNER` | Full control including managing permissions |
| `REVOKE` | Removes all access to the company |
