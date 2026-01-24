# Global Admin Service

The Global Admin Service provides methods to manage developer accounts and API keys. All operations require global admin privileges.

## Usage

```python
from vclient import global_admin_service

admins = global_admin_service()
```

## Available Methods

This service supports all [common CRUD and pagination methods](../README.md#common-service-methods):

- `get(developer_id)` - Retrieve a developer by ID
- `create(username, email, is_global_admin?)` - Create a new developer account
- `update(developer_id, username?, email?, is_global_admin?)` - Update a developer
- `delete(developer_id)` - Delete a developer account
- `get_page(limit?, offset?, is_global_admin?)` - Get a paginated page of developers
- `list_all(is_global_admin?)` - Get all developers
- `iter_all(limit?, is_global_admin?)` - Iterate through all developers

The pagination methods accept an optional `is_global_admin` filter parameter.

## Service-Specific Methods

### `create_api_key()`

Generate a new API key for a developer. The current key will be immediately invalidated.

**Parameters:**

| Parameter      | Type  | Description                                   |
| -------------- | ----- | --------------------------------------------- |
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

| Field            | Type                             | Description                                         |
| ---------------- | -------------------------------- | --------------------------------------------------- |
| `id`             | `str`                            | MongoDB document ObjectID                           |
| `date_created`   | `datetime`                       | Timestamp when the developer was created            |
| `date_modified`  | `datetime`                       | Timestamp when the developer was last modified      |
| `username`       | `str`                            | Developer username                                  |
| `email`          | `str`                            | Developer email address                             |
| `key_generated`  | `datetime \| None`               | Timestamp when the API key was last generated       |
| `is_global_admin`| `bool`                           | Whether the developer has global admin privileges   |
| `companies`      | `list[DeveloperCompanyPermission]`| List of company permissions for this developer     |

### `DeveloperWithApiKey`

Developer response that includes the generated API key. Only returned when generating a new API key.

| Field     | Type           | Description                                   |
| --------- | -------------- | --------------------------------------------- |
| *(inherits all fields from `Developer`)* | | |
| `api_key` | `str \| None`  | The newly generated API key (save immediately)|

### `DeveloperCompanyPermission`

Company permission entry for a developer.

| Field        | Type              | Description                                       |
| ------------ | ----------------- | ------------------------------------------------- |
| `company_id` | `str`             | The company ID                                    |
| `name`       | `str \| None`     | The company name                                  |
| `permission` | `PermissionLevel` | The permission level (`USER`, `ADMIN`, or `OWNER`)|
