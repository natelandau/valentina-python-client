# Options Service

Retrieve all available options and enumerations for the API.

## Usage

```python
from vclient import options_service

options = options_service(company_id="COMPANY_ID")
```

## Methods

| Method          | Returns | Description                      |
| --------------- | ------- | -------------------------------- |
| `get_options()` | `dict`  | Get all options and enumerations |

## Example

```python
options_data = await options.get_options()

# Access company permission options
print(options_data["companies"]["PermissionManageCampaign"])
# Output: ["UNRESTRICTED", "STORYTELLER"]

print(options_data["companies"]["PermissionsGrantXP"])
# Output: ["UNRESTRICTED", "PLAYER", "STORYTELLER"]
```
