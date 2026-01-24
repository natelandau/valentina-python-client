# Developers Service

The Developers Service provides methods to manage your own developer profile. Use this service to view your account details, update your profile, and regenerate your API key.

## Usage

```python
from vclient import developer_service

developer = developer_service()
```

## Methods

### `get_me()`

Retrieve the current developer's profile associated with the API key.

**Returns:** `MeDeveloper`

**Example:**

```python
me = await developer.get_me()
print(f"Username: {me.username}")
print(f"Email: {me.email}")
print(f"Companies: {len(me.companies)}")
```

---

### `update_me()`

Update the current developer's profile. Only include fields that need to be changed.

**Parameters:**

| Parameter  | Type          | Description       |
| ---------- | ------------- | ----------------- |
| `username` | `str \| None` | New username      |
| `email`    | `str \| None` | New email address |

**Returns:** `MeDeveloper`

**Example:**

```python
updated = await developer.update_me(username="newusername")
```

---

### `regenerate_api_key()`

Generate a new API key for your account. The current key will be immediately invalidated.

**Be certain to save the API key from the response. It will not be displayed again.**

**Returns:** `MeDeveloperWithApiKey`

**Example:**

```python
result = await developer.regenerate_api_key()
print(f"New API Key: {result.api_key}")  # Save this immediately!
```

## Response Models

### `MeDeveloper`

Represents the current developer's account returned from the API.

| Field           | Type                                 | Description                                    |
| --------------- | ------------------------------------ | ---------------------------------------------- |
| `id`            | `str`                                | MongoDB document ObjectID                      |
| `date_created`  | `datetime`                           | Timestamp when the developer was created       |
| `date_modified` | `datetime`                           | Timestamp when the developer was last modified |
| `username`      | `str`                                | Developer username                             |
| `email`         | `str`                                | Developer email address                        |
| `key_generated` | `datetime \| None`                   | Timestamp when the API key was last generated  |
| `companies`     | `list[MeDeveloperCompanyPermission]` | List of company permissions for this developer |

### `MeDeveloperWithApiKey`

Developer response that includes the generated API key. Only returned when regenerating the API key.

| Field                                      | Type  | Description                                    |
| ------------------------------------------ | ----- | ---------------------------------------------- |
| _(inherits all fields from `MeDeveloper`)_ |       |                                                |
| `api_key`                                  | `str` | The newly generated API key (save immediately) |

### `MeDeveloperCompanyPermission`

Company permission entry for the developer.

| Field        | Type              | Description                                        |
| ------------ | ----------------- | -------------------------------------------------- |
| `company_id` | `str`             | The company ID                                     |
| `name`       | `str \| None`     | The company name                                   |
| `permission` | `PermissionLevel` | The permission level (`USER`, `ADMIN`, or `OWNER`) |
