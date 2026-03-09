---
icon: lucide/test-tubes
---

# Testing

The `vclient.testing` module provides a fake client that you can drop into your test suite as a replacement for the real `VClient`. It lets you verify that your application code works correctly against the vclient contract without making HTTP calls.

If the shape of a vclient response model changes in a future release, tests using the fake client will break — giving you early warning before the change reaches production.

## Installation

The testing module requires the `testing` extra:

```bash
# Using uv
uv add valentina-python-client[testing]

# Using pip
pip install valentina-python-client[testing]
```

## Quick Start

Replace `VClient` with `FakeVClient` in your tests. Factory functions like `campaigns_service()` work automatically because `FakeVClient` registers itself as the default client.

```python
import asyncio
from vclient import campaigns_service
from vclient.testing import FakeVClient

async def main():
    async with FakeVClient() as client:
        # Factory functions work without configuration
        campaigns = campaigns_service("user-123")
        result = await campaigns.list_all()

        # Each item is a real Campaign model instance
        for campaign in result:
            print(f"Campaign: {campaign.name}")

asyncio.run(main())
```

Every endpoint returns auto-generated data that conforms to the actual Pydantic model definitions. No manual fixtures to maintain.

## Sync Usage

Use `SyncFakeVClient` for synchronous applications. The API mirrors `SyncVClient`:

```python
from vclient._sync.registry import sync_campaigns_service
from vclient.testing import SyncFakeVClient

with SyncFakeVClient() as client:
    campaigns = sync_campaigns_service("user-123")
    result = campaigns.list_all()
    for campaign in result:
        print(f"Campaign: {campaign.name}")
```

## Customizing Responses

Use `set_response()` to control what a specific endpoint returns. Pass a route constant from the `Routes` class and provide either `items` (for paginated endpoints) or `model` (for single-object endpoints). The method handles JSON serialization and envelope wrapping automatically.

Return an empty list from a paginated endpoint:

```python
from vclient import users_service
from vclient.testing import FakeVClient, Routes

async with FakeVClient() as client:
    client.set_response(Routes.USERS_LIST, items=[])
    result = await users_service().list_all()
    assert result == []
```

Return a specific model instance from a single-object endpoint:

```python
from vclient import books_service
from vclient.testing import CampaignBookFactory, FakeVClient, Routes

async with FakeVClient() as client:
    book = CampaignBookFactory.build(number=5)
    client.set_response(Routes.BOOKS_RENUMBER, model=book)
    result = await books_service("user123", "campaign123").renumber("book-id", number=5)
    assert result.number == 5
```

### Matching by Path Parameter

By default, `set_response()` and `set_error()` apply to all requests that match the route, regardless of path parameter values. Use the `params` kwarg to return different responses for different IDs:

```python
from vclient import campaigns_service
from vclient.testing import CampaignFactory, FakeVClient, Routes

async with FakeVClient() as client:
    campaign_a = CampaignFactory.build()
    campaign_b = CampaignFactory.build()

    # Each campaign_id gets its own response
    client.set_response(
        Routes.CAMPAIGNS_GET,
        model=campaign_a,
        params={"campaign_id": campaign_a.id},
    )
    client.set_response(
        Routes.CAMPAIGNS_GET,
        model=campaign_b,
        params={"campaign_id": campaign_b.id},
    )

    svc = campaigns_service("user-123")
    result_a = await svc.get(campaign_a.id)  # returns campaign_a
    result_b = await svc.get(campaign_b.id)  # returns campaign_b
```

You can combine a parameterized override with a generic fallback. Parameterized overrides always take priority, regardless of the order you register them:

```python
async with FakeVClient() as client:
    generic = CampaignFactory.build()
    specific = CampaignFactory.build()

    # Generic fallback for any campaign_id
    client.set_response(Routes.CAMPAIGNS_GET, model=generic)

    # Specific override for one campaign_id
    client.set_response(
        Routes.CAMPAIGNS_GET,
        model=specific,
        params={"campaign_id": "target-id"},
    )

    svc = campaigns_service("user-123")
    await svc.get("target-id")   # returns specific
    await svc.get("anything")    # returns generic
```

The `params` kwarg works with `set_error()` too:

```python
async with FakeVClient() as client:
    # Only this specific campaign returns a 404
    client.set_error(
        Routes.CAMPAIGNS_GET,
        status_code=404,
        params={"campaign_id": "missing-id"},
    )

    svc = campaigns_service("user-123")
    await svc.get("missing-id")  # raises NotFoundError
    await svc.get("other-id")    # returns auto-generated data
```

The parameter names in `params` correspond to the `{placeholders}` in the endpoint URL patterns. For example, `Routes.CAMPAIGNS_GET` matches the pattern `/api/v1/companies/{company_id}/users/{user_id}/campaigns/{campaign_id}`, so valid keys are `company_id`, `user_id`, and `campaign_id`.

### Simulating Errors

Use `set_error()` to make an endpoint return an HTTP error. This is useful for testing error-handling paths in your application:

```python
from vclient.testing import FakeVClient, Routes

async with FakeVClient() as client:
    client.set_error(Routes.CAMPAIGNS_GET, status_code=404)
```

You can include a custom error message with the `detail` parameter:

```python
client.set_error(Routes.USERS_GET, status_code=403, detail="Insufficient permissions")
```

### Route Constants

Every API endpoint has a named constant on the `Routes` class, exported from `vclient.testing`. Constants follow the naming convention `{SERVICE}_{OPERATION}` -- for example, `USERS_LIST`, `BOOKS_RENUMBER`, `CHAPTERS_NOTES_CREATE`. Nested resources include the parent in the name (e.g., `CHARACTERS_INVENTORY_LIST`, `CHAPTERS_ASSETS_UPLOAD`).

### Advanced: Low-Level Route Overrides

For cases that `set_response()` and `set_error()` don't cover, use `add_route()` to register a raw override. Pass an HTTP method, an endpoint pattern from `vclient.endpoints.Endpoints`, and a JSON body:

```python
from vclient.endpoints import Endpoints
from vclient.testing import FakeVClient

async with FakeVClient() as client:
    client.add_route(
        "GET",
        Endpoints.OPTIONS,
        json={"game_systems": ["VTM5e", "WTA5e"]},
    )
```

### Building Override Data with Factories

Instead of writing JSON by hand, use the included model factories to generate valid data and customize only the fields you care about. Factories pair well with `set_response()` -- build one or more model instances and pass them directly:

```python
from vclient.testing import CampaignFactory, FakeVClient

campaign = CampaignFactory.build(name="Test Campaign")
print(campaign.name)       # "Test Campaign"
print(campaign.id)         # auto-generated valid string
print(campaign.game_system) # auto-generated valid Literal value
```

Factories support batch creation:

```python
campaigns = CampaignFactory.batch(5)
# Returns a list of 5 Campaign instances with random valid data
```

## Available Factories

Every public response model has a corresponding factory. All factories are exported from `vclient.testing`:

| Factory                                        | Model                                |
| ---------------------------------------------- | ------------------------------------ |
| `AssetFactory`                                 | `Asset`                              |
| `CampaignFactory`                              | `Campaign`                           |
| `CampaignBookFactory`                          | `CampaignBook`                       |
| `CampaignChapterFactory`                       | `CampaignChapter`                    |
| `CampaignExperienceFactory`                    | `CampaignExperience`                 |
| `CharacterFactory`                             | `Character`                          |
| `CharacterConceptFactory`                      | `CharacterConcept`                   |
| `CharacterTraitFactory`                        | `CharacterTrait`                     |
| `CharacterTraitValueOptionsResponseFactory`    | `CharacterTraitValueOptionsResponse` |
| `ChargenSessionResponseFactory`                | `ChargenSessionResponse`             |
| `CompanyFactory`                               | `Company`                            |
| `CompanyPermissionsFactory`                    | `CompanyPermissions`                 |
| `DeveloperFactory`                             | `Developer`                          |
| `DeveloperWithApiKeyFactory`                   | `DeveloperWithApiKey`                |
| `DicerollFactory`                              | `Diceroll`                           |
| `DictionaryTermFactory`                        | `DictionaryTerm`                     |
| `EdgeAndPerksFactory`                          | `EdgeAndPerks`                       |
| `HunterEdgeFactory`                            | `HunterEdge`                         |
| `HunterEdgePerkFactory`                        | `HunterEdgePerk`                     |
| `InventoryItemFactory`                         | `InventoryItem`                      |
| `MeDeveloperFactory`                           | `MeDeveloper`                        |
| `MeDeveloperWithApiKeyFactory`                 | `MeDeveloperWithApiKey`              |
| `NewCompanyResponseFactory`                    | `NewCompanyResponse`                 |
| `NoteFactory`                                  | `Note`                               |
| `PerkFactory`                                  | `Perk`                               |
| `QuickrollFactory`                             | `Quickroll`                          |
| `RollStatisticsFactory`                        | `RollStatistics`                     |
| `SheetSectionFactory`                          | `SheetSection`                       |
| `SystemHealthFactory`                          | `SystemHealth`                       |
| `TraitCategoryFactory`                         | `TraitCategory`                      |
| `TraitFactory`                                 | `Trait`                              |
| `UserFactory`                                  | `User`                               |
| `VampireClanFactory`                           | `VampireClan`                        |
| `WerewolfAuspiceFactory`                       | `WerewolfAuspice`                    |
| `WerewolfGiftFactory`                          | `WerewolfGift`                       |
| `WerewolfRiteFactory`                          | `WerewolfRite`                       |
| `WerewolfTribeFactory`                         | `WerewolfTribe`                      |

## How It Works

`FakeVClient` subclasses `VClient` and overrides the internal HTTP client with an `httpx.MockTransport`. All the real service classes run unmodified — they make HTTP calls, but those calls are intercepted by an in-memory router that returns auto-generated responses.

Response data is generated by [polyfactory](https://polyfactory.litestar.dev/), which introspects the Pydantic model definitions to produce valid instances. When vclient updates a model (adds a field, changes a type, narrows a `Literal`), polyfactory generates data matching the new shape. Tests using the old shape will fail, surfacing the breaking change.

The `SyncFakeVClient` variant is auto-generated from the async source using the same codegen pipeline as `SyncVClient`.

### Default Client Registration Order

`FakeVClient` passes `set_as_default=True` by default, which registers it as the global default client for factory functions like `campaigns_service()`. If your application also creates a real `VClient` with `set_as_default=True`, the **last one created wins**.

In pytest, this means your fake client fixture must be created _after_ any application fixture that instantiates a real `VClient`. The simplest way to guarantee this is to make the fake client fixture depend on the application fixture:

```python
import pytest
from vclient.testing import FakeVClient

@pytest.fixture
def app():
    # Your application creates a real VClient internally
    return create_app()

@pytest.fixture
async def fake_client(app):
    # FakeVClient is created after app, so it becomes the default
    async with FakeVClient() as client:
        yield client
```

If you don't need the global default behavior, pass `set_as_default=False` and use the client directly instead of relying on factory functions.
