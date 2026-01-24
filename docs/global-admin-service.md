# Global Admin Service

The Global Admin Service provides methods to manage developer accounts and API keys. All operations require global admin privileges.

## Usage

```python
from vclient import global_admin_service

admins = global_admin_service()
```

## Methods

### `get_page()`

Retrieve a paginated page of developer accounts.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | `int` | `10` | Maximum number of items to return (0-100) |
| `offset` | `int` | `0` | Number of items to skip from the beginning |
| `is_global_admin` | `bool \| None` | `None` | Optional filter by global admin status |

**Returns:** `PaginatedResponse[Developer]`

**Example:**

```python
# Get all developers
page = await admins.get_page(limit=10, offset=0)

# Filter by admin status
admin_page = await admins.get_page(is_global_admin=True)
```

---

### `list_all()`

Retrieve all developer accounts. Automatically paginates through all results.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `is_global_admin` | `bool \| None` | `None` | Optional filter by global admin status |

**Returns:** `list[Developer]`

**Example:**

```python
# Get all developers
all_developers = await admins.list_all()

# Get only global admins
global_admins = await admins.list_all(is_global_admin=True)
```

---

### `iter_all()`

Iterate through all developer accounts with memory-efficient streaming.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | `int` | `100` | Items per page |
| `is_global_admin` | `bool \| None` | `None` | Optional filter by global admin status |

**Yields:** `Developer`

**Example:**

```python
async for developer in admins.iter_all():
    print(f"{developer.username}: {developer.email}")
```

---

### `get()`

Retrieve detailed information about a specific developer.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `developer_id` | `str` | The ID of the developer to retrieve |

**Returns:** `Developer`

**Raises:**

- `NotFoundError`: If the developer does not exist
- `AuthorizationError`: If you don't have global admin privileges

**Example:**

```python
developer = await admins.get("507f1f77bcf86cd799439011")
print(f"Username: {developer.username}")
print(f"Email: {developer.email}")
print(f"Global Admin: {developer.is_global_admin}")
```

---

### `create()`

Create a new developer account. This creates the account but does not generate an API key.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `username` | `str` | Yes | Developer username |
| `email` | `str` | Yes | Developer email address |
| `is_global_admin` | `bool` | No | Whether the developer should have global admin privileges (default: `False`) |

**Returns:** `Developer`

**Raises:**

- `ValidationError`: If the request data is invalid
- `AuthorizationError`: If you don't have global admin privileges

**Example:**

```python
# Create a regular developer
developer = await admins.create(
    username="newuser",
    email="user@example.com",
)

# Create a global admin
admin = await admins.create(
    username="adminuser",
    email="admin@example.com",
    is_global_admin=True,
)
```

---

### `update()`

Modify a developer account's properties. Only include fields that need to be changed.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `developer_id` | `str` | Yes | The ID of the developer to update |
| `username` | `str \| None` | No | New developer username |
| `email` | `str \| None` | No | New developer email address |
| `is_global_admin` | `bool \| None` | No | New global admin status |

**Returns:** `Developer`

**Raises:**

- `NotFoundError`: If the developer does not exist
- `AuthorizationError`: If you don't have global admin privileges
- `ValidationError`: If the request data is invalid

**Example:**

```python
updated = await admins.update(
    "507f1f77bcf86cd799439011",
    username="newusername",
    is_global_admin=True,
)
```

---

### `delete()`

Remove a developer account from the system. The developer's API key will be invalidated immediately.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `developer_id` | `str` | The ID of the developer to delete |

**Returns:** `None`

**Raises:**

- `NotFoundError`: If the developer does not exist
- `AuthorizationError`: If you don't have global admin privileges

**Example:**

```python
await admins.delete("507f1f77bcf86cd799439011")
```

---

### `create_api_key()`

Generate a new API key for a developer. The current key will be immediately invalidated.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `developer_id` | `str` | The ID of the developer to generate a key for |

**Returns:** `DeveloperWithApiKey`

**Raises:**

- `NotFoundError`: If the developer does not exist
- `AuthorizationError`: If you don't have global admin privileges

**Example:**

```python
dev_with_key = await admins.create_api_key("507f1f77bcf86cd799439011")
print(f"New API Key: {dev_with_key.api_key}")  # Save this - only shown once!
```

## Response Models

### `Developer`

Represents a developer account returned from the API.

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | MongoDB document ObjectID |
| `date_created` | `datetime` | Timestamp when the developer was created |
| `date_modified` | `datetime` | Timestamp when the developer was last modified |
| `username` | `str` | Developer username |
| `email` | `str` | Developer email address |
| `key_generated` | `datetime \| None` | Timestamp when the API key was last generated |
| `is_global_admin` | `bool` | Whether the developer has global admin privileges |
| `companies` | `list[DeveloperCompanyPermission]` | List of company permissions for this developer |

### `DeveloperWithApiKey`

Developer response that includes the generated API key. Only returned when generating a new API key.

| Field | Type | Description |
|-------|------|-------------|
| *All fields from `Developer`* | | |
| `api_key` | `str \| None` | The newly generated API key (save immediately) |

### `DeveloperCompanyPermission`

Company permission entry for a developer.

| Field | Type | Description |
|-------|------|-------------|
| `company_id` | `str` | The company ID |
| `name` | `str \| None` | The company name |
| `permission` | `PermissionLevel` | The permission level (`USER`, `ADMIN`, or `OWNER`) |

### `PaginatedResponse[Developer]`

Paginated response structure for developer listings.

| Field | Type | Description |
|-------|------|-------------|
| `items` | `list[Developer]` | The requested page of results |
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
