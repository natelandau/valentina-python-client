# Options Service

The Options Service provides methods to retrieve all options and enumerations for the api.

## Usage

```python
from vclient import options_service

options = options_service("company123")

# Get all options and enumerations
options = await options.get_options()
```

## Available Methods

- `get_options()` - Retrieve all options and enumerations for the api.

## Response

A dictionary of options and enumerations for the api.

```json
{
    "companies": {
        "PermissionManageCampaign": ["UNRESTRICTED", "STORYTELLER"],
        "PermissionsGrantXP": ["UNRESTRICTED", "PLAYER", "STORYTELLER"],
        "PermissionsFreeTraitChanges": ["UNRESTRICTED", "WITHIN_24_HOURS", "STORYTELLER"]
    },
    ...
}
```
