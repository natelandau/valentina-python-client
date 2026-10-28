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

    `assign()` also raises `ConflictError` when the character already has the trait. This check runs before the value range check, so a duplicate with an out-of-range value also returns 409. Do not retry it. Use the value methods on the existing trait instead.

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

### V5 Willpower

On V5 characters, Willpower always equals Composure + Resolve. The server keeps it in sync, so you cannot change it directly:

- `change_value()` and `delete()` raise `ValidationError` (400).
- `get_value_options()` returns an empty `options` dictionary.
- `assign()` raises `ConflictError` (409), and `bulk_assign()` puts the item in `failed`, because every V5 character already has Willpower.

To change V5 Willpower, change Composure or Resolve. Then fetch the Willpower trait again, because `change_value()` returns only the trait that you changed. For the same reason, fetch health again with `characters.get_health()` after you change V5 Stamina, because Stamina sets the size of the health track. V4 Willpower has none of these limits.

### Trackers

| Method                                                                       | Returns   | Description                          |
| ---------------------------------------------------------------------------- | --------- | ------------------------------------ |
| `get_tracker(character_trait_id)`                                            | `Tracker` | Get the in-play state of a trait     |
| `set_tracker(character_trait_id, TrackerStateSet, **kwargs)`                 | `Tracker` | Replace the full tracker state       |
| `apply_tracker_action(character_trait_id, action, amount?)`                  | `Tracker` | Apply one in-play action             |

A tracker holds the in-play state of a trait that is spent or stained during a session. `Tracker` is one of two models. Read its `type` field to know which one you have:

| `type`    | Model            | Used for                                                                                 | Field for `set_tracker()` | Actions                              |
| --------- | ---------------- | ---------------------------------------------------------------------------------------- | ------------------------- | ------------------------------------ |
| `COUNTER` | `CounterTracker` | Willpower in V4 and V5, Blood Pool, Rage, Gnosis, Conviction, and Humanity for every character except a V5 vampire | `current` (required) | `spend`, `gain`, `reset`             |
| `STAINS`  | `StainsTracker`  | Humanity on a V5 vampire                                                                  | `stains`                  | `add_stain`, `remove_stain`, `reset` |

The same tracker object is on `CharacterTrait.tracker`. It is `None` when the trait has no tracker for the character's game version. Custom traits never have a tracker. `Trait.tracker_type_v4` and `Trait.tracker_type_v5` tell you which traits have a tracker before you assign them.

!!! warning "Humanity"

    Choose the Humanity control from `CharacterTrait.tracker.type`, not from the blueprint. `Trait.tracker_type_v5` for Humanity is `STAINS`, but only a V5 vampire gets a `STAINS` tracker. Every other character gets a `COUNTER`.

Use `apply_tracker_action()` for changes during play, and `set_tracker()` to correct the full state. An empty `set_tracker()` request clears a stains tracker. Each method returns the updated tracker, so you do not need to fetch it again. The actions for each tracker type and game version are in `characters.TrackerRules` from the [Options Service](options.md). Stains past `stain_capacity` stay on the tracker and have no other effect.

The methods raise these errors:

- `NotFoundError` (404): the trait has no tracker for the character's game version.
- `ValidationError` (400): the field or action does not fit the tracker type, a spend is more than `current`, or a value is more than the tracker size.
- `AuthorizationError` (403): you are not the character's player or a storyteller.
- `RequestValidationError`: a value is negative, `amount` is less than 1, or `set_tracker()` receives a field other than `current` and `stains`. The client raises this error before it sends the request.

!!! note "API version"

    The tracker endpoints need a Valentina API release later than `v0.28.0`. An older API returns 404, and `CharacterTrait.tracker` is always `None`. API `v0.29.0` sends V5 Willpower as a `DAMAGE` tracker, which this client rejects, so parsing any V5 character's traits from that release raises a `pydantic.ValidationError`. Use an API release later than `v0.29.0`.

```python
from vclient.models import CounterTracker, StainsTracker

tracker = await traits.get_tracker(willpower.id)

match tracker:
    case CounterTracker():
        print(f"{tracker.current}/{tracker.size} Willpower")
    case StainsTracker():
        print(f"{tracker.stains} stains, {tracker.stain_capacity} free boxes")

# Spend two points of Willpower
tracker = await traits.apply_tracker_action(willpower.id, "spend", amount=2)

# Correct the full state
tracker = await traits.set_tracker(willpower.id, current=3)
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
