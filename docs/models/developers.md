---
icon: lucide/code
---

# Developer Models

Models for developer accounts, API key management, and company permission grants.

## Developer

| Field                | Type                               | Description                                                 |
| -------------------- | ---------------------------------- | ----------------------------------------------------------- |
| `id`                 | `str`                              | Unique identifier                                           |
| `date_created`       | `datetime`                         | Creation timestamp                                          |
| `date_modified`      | `datetime`                         | Last modified timestamp                                     |
| `username`           | `str`                              | Username                                                    |
| `email`              | `str`                              | Email address                                               |
| `key_generated`      | `datetime \| None`                 | API key generation time                                     |
| `is_global_admin`    | `bool`                             | Global admin status                                         |
| `companies`          | `list[DeveloperCompanyPermission]` | Company permissions                                         |
| `provider_audiences` | `ProviderAudiences`                | Per-provider OIDC audience allowlists (defaults to `{}`)    |

## MeDeveloper

Your own developer profile. Contains the same fields as `Developer` but excludes the `is_global_admin` field for security. The `provider_audiences` field defaults to `{}` when absent from older API responses.

## MeDeveloperWithApiKey

Extends `MeDeveloper` with the generated API key. Only returned when regenerating your API key — save it immediately as it can't be retrieved again.

| Field     | Type  | Description                                    |
| --------- | ----- | ---------------------------------------------- |
| `api_key` | `str` | Generated API key (shown only at creation time) |

All other fields are inherited from `MeDeveloper`.

## MeDeveloperUpdate

Request body for updating your developer profile.

| Field                | Type                        | Description                                         |
| -------------------- | --------------------------- | --------------------------------------------------- |
| `username`           | `str \| None`               | Updated username                                    |
| `email`              | `str \| None`               | Updated email                                       |
| `provider_audiences` | `ProviderAudiences \| None` | Per-provider OIDC audience allowlists to register   |

See [ProviderAudiences](#provideraudiences) below.

## ProviderAudiences

A `dict` mapping OIDC provider keys (`"apple"` or `"google"`) to a list of audience strings. Lets a developer register their own client app identifiers so the API resolves tokens issued to those apps.

```python
ProviderAudiences = dict[
    Literal["apple", "google"],
    list[str],  # max 20 per provider; each 1-255 chars
]
```

**Constraints enforced client-side:**

- Keys must be `"apple"` or `"google"` (the `OIDCProvider` type).
- Each provider may have at most 20 audience strings.
- Each audience string must be 1-255 characters.

## DeveloperUpdate

Admin-side request body for updating any developer account. Used with `GlobalAdminService.update_developer()`.

| Field                | Type                        | Description                                         |
| -------------------- | --------------------------- | --------------------------------------------------- |
| `username`           | `str \| None`               | Updated username                                    |
| `email`              | `str \| None`               | Updated email                                       |
| `is_global_admin`    | `bool \| None`              | Grant or revoke global admin status                 |
| `provider_audiences` | `ProviderAudiences \| None` | Per-provider OIDC audience allowlists to register   |

All fields are optional. See [ProviderAudiences](#provideraudiences) for the audience format and constraints.

## ServerLogEntry

A single parsed server log entry returned by `tail_logs()` on the [Global Admin Service](../services/global_admin.md). Every field is nullable because individual log lines may omit values or fail to parse as structured JSON. When a line is not valid JSON, the original text is available on `raw`.

| Field       | Type             | Description                                  |
| ----------- | ---------------- | -------------------------------------------- |
| `timestamp` | `str \| None`    | Log entry timestamp                          |
| `level`     | `str \| None`    | Log level                                    |
| `name`      | `str \| None`    | Logger name                                  |
| `message`   | `str \| None`    | Log message                                  |
| `exception` | `str \| None`    | Formatted exception traceback, if any        |
| `extra`     | `dict[str, Any]` | Additional structured fields (defaults to `{}`) |
| `raw`       | `str \| None`    | Original line when the entry is not valid JSON |

## ServerLogArchive

A downloaded server-log zip archive returned by `download_logs()` on the [Global Admin Service](../services/global_admin.md). This is a frozen dataclass rather than a Pydantic model. Pair the server-provided filename with the raw zip bytes to write the archive straight to disk.

| Field      | Type    | Description                                          |
| ---------- | ------- | --------------------------------------------------- |
| `filename` | `str`   | Filename parsed from the server's `Content-Disposition` |
| `content`  | `bytes` | Raw zip archive bytes                               |
