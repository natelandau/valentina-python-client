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

Use `add_route()` to override what a specific endpoint returns. Pass an endpoint pattern from `vclient.endpoints.Endpoints` along with the JSON body you want:

```python
from vclient import users_service
from vclient.endpoints import Endpoints
from vclient.testing import FakeVClient

async with FakeVClient() as client:
    client.add_route(
        "GET",
        Endpoints.USERS,
        json={
            "items": [
                {
                    "id": "user-1",
                    "date_created": "2024-01-01T00:00:00Z",
                    "date_modified": "2024-01-01T00:00:00Z",
                    "name_first": "Ada",
                    "name_last": "Lovelace",
                    "username": "ada",
                    "email": "ada@example.com",
                    "role": "PLAYER",
                    "company_id": "fake-company",
                    "discord_profile": None,
                    "campaign_experience": [],
                    "asset_ids": [],
                }
            ],
            "total": 1,
            "limit": 10,
            "offset": 0,
        },
    )

    result = await users_service().list_all()
    assert result[0].name_first == "Ada"
```

You can also return error responses by setting `status_code`:

```python
client.add_route(
    "GET",
    Endpoints.CAMPAIGN,
    json={"detail": "Not found"},
    status_code=404,
)
```

### Building Override Data with Factories

Instead of writing JSON by hand, use the included model factories to generate valid data and customize only the fields you care about:

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
