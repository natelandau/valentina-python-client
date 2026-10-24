---
icon: lucide/sliders-horizontal
---

# Character Traits Service

Manage character traits including retrieval, assignment, and value modification.

## Usage

```python
from vclient import character_traits_service

traits = character_traits_service(
    character_id="CHARACTER_ID", on_behalf_of="USER_ID", company_id="COMPANY_ID"
)
```

## Methods

### CRUD Operations

| Method                                  | Returns          | Description                                                                 |
| --------------------------------------- | ---------------- | --------------------------------------------------------------------------- |
| `get(character_trait_id)`               | `CharacterTrait` | Get a character trait by ID                                                 |
| `assign(trait_id, value, currency)`     | `CharacterTrait` | Assign an existing trait to the character with `TraitModifyCurrency`        |
| `bulk_assign(list[CharacterTraitAdd])` | `BulkAssignTraitResponse` | Assign multiple traits at once with best-effort semantics |
| `create(TraitCreate, **kwargs)`         | `CharacterTrait` | Create a custom trait                                                       |
| `delete(character_trait_id, currency?)` | `None`           | Delete a character trait. Optional `TraitModifyCurrency` to recoup the cost |

!!! warning "NPC and Storyteller characters require `NO_COST`"

    On `NPC` and `STORYTELLER` characters, every trait operation that takes a `currency` (`assign`, `bulk_assign`, `create`, `change_value`, `delete`, and `add_specialty`) accepts only `currency="NO_COST"`. Passing `"XP"` or `"STARTING_POINTS"` raises `ValidationError` (400). `PLAYER` characters accept all three currencies.

### Pagination

| Method                                           | Returns                             | Description              |
| ------------------------------------------------ | ----------------------------------- | ------------------------ |
| `get_page(limit?, offset?, category_id?)`        | `PaginatedResponse[CharacterTrait]` | Get a page of traits     |
| `list_all(category_id?)`                         | `list[CharacterTrait]`              | Get all character traits |
| `iter_all(limit?, category_id?)`                 | `AsyncIterator[CharacterTrait]`     | Iterate through traits   |

### Value Modification

| Method                                                  | Returns                              | Description                 |
| ------------------------------------------------------- | ------------------------------------ | --------------------------- |
| `get_value_options(character_trait_id)`                 | `CharacterTraitValueOptionsResponse` | Get available value options |
| `change_value(character_trait_id, new_value, currency)` | `CharacterTrait`                     | Change trait value          |

!!! warning "Check Options First"

    Always call `get_value_options()` before changing a trait value to ensure the change is valid and to understand the cost implications.

Lowering an ability to `0` with `change_value()`, or deleting the trait with `delete()`, also removes its specialties and refunds what each cost. For the `"0"` and `"DELETE"` options, `xp_after` and `starting_points_after` include those refunds. `point_change` counts dots only.

!!! note "Concurrent changes raise `ConflictError`"

    `change_value()` with any currency, and `delete()`, `assign()`, and `create()` with `"XP"` or `"STARTING_POINTS"`, raise `ConflictError` (409) when another request changed the trait's value first. Nothing is spent or refunded. Fetch the trait again and retry.

    ```python
    from vclient.exceptions import ConflictError

    try:
        await traits.change_value(trait.id, new_value=4, currency="XP")
    except ConflictError:
        trait = await traits.get(trait.id)
        # Decide again with the current value, then retry
    ```

### Specialties

| Method                                                   | Returns          | Description                             |
| -------------------------------------------------------- | ---------------- | --------------------------------------- |
| `add_specialty(character_trait_id, name, currency?)`     | `CharacterTrait` | Add a specialty to an ability           |
| `update_specialty(character_trait_id, specialty_id, name)` | `CharacterTrait` | Rename a specialty                    |
| `delete_specialty(character_trait_id, specialty_id)`     | `None`           | Remove a specialty and refund its cost  |

Specialties are free-text focuses on ability traits, such as "Knives" on Melee. Only abilities with a value of 1 or higher accept them. The name must be 3 to 50 characters and unique on the trait, ignoring case.

The cost depends on the company's `specialty_xp_cost_enabled` setting:

- **Off** (default): specialties are free, whatever the `currency`.
- **On**: a specialty paid with `"XP"` or `"STARTING_POINTS"` costs 3 points. `"NO_COST"` follows the company's free trait changes setting.

`delete_specialty()` refunds the cost in the currency used to buy it. An `XP` refund follows the company's `permission_recoup_xp` setting. Starting points are always refunded.

`add_specialty()` raises `ValidationError` when the trait is not an ability, has a value of 0, already has a specialty with that name, or the character cannot afford the cost. `update_specialty()` and `delete_specialty()` raise `NotFoundError` for an unknown specialty or one that belongs to a different trait.

```python
melee = await traits.add_specialty(trait.id, name="Knives", currency="XP")
knives = melee.specialties[0]

melee = await traits.update_specialty(trait.id, knives.id, name="Throwing Knives")
await traits.delete_specialty(trait.id, knives.id)
```

## Example

```python
from vclient.models import TraitCreate

# Assign an existing trait from the blueprint
trait = await traits.assign(trait_id="strength_trait_id", value=3, currency="XP")

# Create a custom trait (preferred method: use model object).
# The trait is always created at a value of 1; the currency pays for that first dot.
# Custom traits are rollable by default; pass is_rollable=False for a non-rollable trait.
request = TraitCreate(
    name="Street Smarts",
    category_id="skills_category_id",
    currency="XP",
    max_value=5,
)
custom = await traits.create(request)

# Alternative: pass fields as keyword arguments
custom = await traits.create(
    name="Street Smarts",
    category_id="skills_category_id",
    currency="XP",
    max_value=5,
)

# Check available value change options
options = await traits.get_value_options(trait.id)
print(f"Available values: {options.available_values}")
print(f"Current value: {options.current_value}")

# Change the trait value
updated = await traits.change_value(trait.id, new_value=4, currency="XP")
```

## Bulk Assignment

Assign multiple traits in a single request. Each item is processed independently — successful assignments are saved and failed ones are reported with error details.

```python
from vclient.models import CharacterTraitAdd

items = [
    CharacterTraitAdd(trait_id="strength_id", value=3, currency="XP"),
    CharacterTraitAdd(trait_id="dexterity_id", value=2, currency="NO_COST"),
    CharacterTraitAdd(trait_id="stamina_id", value=1, currency="STARTING_POINTS"),
]
result = await traits.bulk_assign(items)

for success in result.succeeded:
    print(f"Assigned: {success.character_trait.trait.name}")

for failure in result.failed:
    print(f"Failed {failure.trait_id}: {failure.error}")
```

!!! warning "Running Currency Balance"

    Currency balances are tracked across the batch. If early traits spend XP or starting points, later traits in the same request see the reduced balance. Order items strategically — place flaw traits (which grant currency) before traits that spend it.

Maximum batch size is 200 items. Exceeding this raises `ValidationError`.

See [Response Models](../models/character_traits.md) for `CharacterTrait`, `Trait`, and related types.
