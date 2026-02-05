# Global Admin Service

Manage developer accounts and API keys. All operations require global admin privileges.

## Usage

```python
from vclient import global_admin_service

admins = global_admin_service()
```

## Methods

### CRUD Operations

| Method                                            | Returns     | Description                |
| ------------------------------------------------- | ----------- | -------------------------- |
| `get(developer_id)`                               | `Developer` | Get a developer by ID      |
| `create(DeveloperCreate, **kwargs)`               | `Developer` | Create a developer account |
| `update(developer_id, DeveloperUpdate, **kwargs)` | `Developer` | Update a developer         |
| `delete(developer_id)`                            | `None`      | Delete a developer account |

### Pagination

| Method                                        | Returns                        | Description                    |
| --------------------------------------------- | ------------------------------ | ------------------------------ |
| `get_page(limit?, offset?, is_global_admin?)` | `PaginatedResponse[Developer]` | Get a page of developers       |
| `list_all(is_global_admin?)`                  | `list[Developer]`              | Get all developers             |
| `iter_all(limit?, is_global_admin?)`          | `AsyncIterator[Developer]`     | Iterate through all developers |

### API Keys

| Method                         | Returns               | Description                            |
| ------------------------------ | --------------------- | -------------------------------------- |
| `create_api_key(developer_id)` | `DeveloperWithApiKey` | Generate a new API key for a developer |

## Example

```python
from vclient.models import DeveloperCreate, DeveloperUpdate

# Create a new developer (preferred: use model object)
request = DeveloperCreate(
    username="newdev",
    email="dev@example.com"
)
dev = await admins.create(request)

# Alternative: pass fields as kwargs
dev = await admins.create(
    username="newdev",
    email="dev@example.com"
)

# Update a developer
update = DeveloperUpdate(email="newemail@example.com")
updated = await admins.update(dev.id, update)

# Generate new API key for existing developer
dev_with_key = await admins.create_api_key(dev.id)
print(f"New API Key: {dev_with_key.api_key}")  # Save this - only shown once
```

See [Response Models](models.md) for `Developer`, `DeveloperWithApiKey`, and related types.
