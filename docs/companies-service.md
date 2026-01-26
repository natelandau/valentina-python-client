# Companies Service

The Companies Service provides methods to create, retrieve, update, and delete companies, as well as manage developer access permissions.

## Usage

```python
from vclient import companies_service

companies = companies_service()
```

## Available Methods

This service supports all [common CRUD and pagination methods](../README.md#common-service-methods):

- `get(company_id)` - Retrieve a company by ID
- `create(name, email, description?, settings?)` - Create a new company
- `update(company_id, name?, email?, description?, settings?)` - Update a company
- `delete(company_id)` - Delete a company
- `get_page(limit?, offset?)` - Get a paginated page of companies
- `list_all()` - Get all companies
- `iter_all(limit?)` - Iterate through all companies

## Service-Specific Methods

### `grant_access()`

Add, update, or revoke a developer's permission level for a company.

**Parameters:**

| Parameter      | Type              | Description                                                  |
| -------------- | ----------------- | ------------------------------------------------------------ |
| `company_id`   | `str`             | The ID of the company                                        |
| `developer_id` | `str`             | The ID of the developer to grant/modify access for           |
| `permission`   | `PermissionLevel` | The permission level (`USER`, `ADMIN`, `OWNER`, or `REVOKE`) |

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

| Field           | Type                      | Description                                  |
| --------------- | ------------------------- | -------------------------------------------- |
| `id`            | `str`                     | MongoDB document ObjectID                    |
| `date_created`  | `datetime`                | Timestamp when the company was created       |
| `date_modified` | `datetime`                | Timestamp when the company was last modified |
| `name`          | `str`                     | Company name                                 |
| `description`   | `str \| None`             | Company description                          |
| `email`         | `str`                     | Company contact email                        |
| `user_ids`      | `list[str]`               | List of user IDs associated with the company |
| `settings`      | `CompanySettings \| None` | Company settings and configuration           |

### `CompanySettings`

Configuration options for a company. Import with `from vclient.models import CompanySettings`.

| Field | Type | Description |
| --- | --- | --- |
| `character_autogen_xp_cost` | `int \| None` | Cost to autogen XP for a character (0-100) |
| `character_autogen_num_choices` | `int \| None` | Number of characters generated for selection (1-10) |
| `permission_manage_campaign` | `ManageCampaignPermission \| None` | Permission level for managing campaigns |
| `permission_grant_xp` | `GrantXPPermission \| None` | Permission level for granting XP |
| `permission_free_trait_changes` | `FreeTraitChangesPermission \| None` | Permission level for free trait changes |

### `CompanyPermissions`

Response from granting or modifying developer access.

| Field        | Type              | Description                  |
| ------------ | ----------------- | ---------------------------- |
| `company_id` | `str`             | The company ID               |
| `name`       | `str \| None`     | The company name             |
| `permission` | `PermissionLevel` | The permission level granted |

## Permission Levels

| Level    | Description                                 |
| -------- | ------------------------------------------- |
| `USER`   | Basic access to view company data           |
| `ADMIN`  | Can modify company settings and data        |
| `OWNER`  | Full control including managing permissions |
| `REVOKE` | Removes all access to the company           |
