# Dice Rolls Service

Create and retrieve dice rolls for characters within a company.

## Usage

```python
from vclient import dicerolls_service

dicerolls = dicerolls_service(user_id="USER_ID", company_id="COMPANY_ID")
```

## Methods

### CRUD Operations

| Method                                              | Returns    | Description                    |
| --------------------------------------------------- | ---------- | ------------------------------ |
| `get(diceroll_id)`                                  | `Diceroll` | Get a dice roll by ID          |
| `create(DicerollCreate, **kwargs)`                  | `Diceroll` | Create a new dice roll         |
| `create_quickroll(quickroll_id, character_id, ...)` | `Diceroll` | Create a roll from a quickroll |

### Pagination

| Method | Returns | Description |
| --- | --- | --- |
| `get_page(limit?, offset?, userid?, characterid?, campaignid?)` | `PaginatedResponse[Diceroll]` | Get a page of rolls |
| `list_all(userid?, characterid?, campaignid?)` | `list[Diceroll]` | Get all rolls |
| `iter_all(userid?, characterid?, campaignid?, limit?)` | `AsyncIterator[Diceroll]` | Iterate through rolls |

## Example

```python
from vclient.models import DicerollCreate

# Create a dice roll (preferred: use model object)
request = DicerollCreate(
    dice_size=10,
    num_dice=5,
    difficulty=6,
    num_desperation_dice=0,
    comment="Strength + Brawl",
    trait_ids=["strength_id", "brawl_id"],
    character_id="character_id",
    campaign_id="campaign_id"
)
roll = await dicerolls.create(request)

# Alternative: pass fields as kwargs
roll = await dicerolls.create(
    dice_size=10,
    num_dice=5,
    difficulty=6,
    comment="Strength + Brawl",
    character_id="character_id",
    campaign_id="campaign_id"
)

# Use a quickroll
roll = await dicerolls.create_quickroll(
    quickroll_id="quickroll_id",
    character_id="character_id",
    comment="Combat roll",
    difficulty=6
)
```

See [Response Models](models.md) for `Diceroll`.
