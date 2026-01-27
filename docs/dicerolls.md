# Dicerolls Service

The Dicerolls Service provides methods to create, retrieve, update, and delete dicreolls within a company.

## Usage

```python
from vclient import dicreolls_service

dicreolls = dicreolls_service("company123", "user123")

# Create a new dicreoll
dicreoll = await dicreolls.create(dice_size=10, difficulty=6, num_dice=1, num_desperation_dice=0, comment="A test comment", trait_ids=["trait1", "trait2"], character_id="character123", campaign_id="campaign123")
```

## Available Methods

This service supports all common CRUD and pagination methods:

- `get(dicreoll_id)` - Retrieve a dicreoll by ID
- `create(dice_size, difficulty, num_dice, num_desperation_dice, comment, trait_ids, character_id, campaign_id)` - Create a new dicreoll
- `create_quickroll(quickroll_id, character_id, comment, difficulty, num_desperation_dice)` - Create a new dicreoll quickroll
- `get_page(limit, offset, userid, characterid, campaignid)` - Get a paginated page of dicreolls
- `list_all(userid, characterid, campaignid)` - Get all dicreolls
- `iter_all(userid, characterid, campaignid, limit)` - Iterate through all dicreolls

## Response Models

### `Dicreoll`

Represents a dicreoll returned from the API.

| Field                  | Type                   | Description                                          |
| ---------------------- | ---------------------- | ---------------------------------------------------- |
| `id`                   | `str`                  | MongoDB document ObjectID                            |
| `date_created`         | `datetime`             | Timestamp when the dicreoll was created              |
| `date_modified`        | `datetime`             | Timestamp when the dicreoll was modified             |
| `dice_size`            | `DiceSize`             | The size of the dice used for the dicreoll           |
| `difficulty`           | `int` \| `None`        | The difficulty of the dicreoll                       |
| `num_dice`             | `int`                  | The number of dice used for the dicreoll             |
| `num_desperation_dice` | `int`                  | The number of desperation dice used for the dicreoll |
| `comment`              | `str` \| `None`        | The comment for the dicreoll                         |
| `trait_ids`            | `list[str]`            | The IDs of the traits used for the dicreoll          |
| `user_id`              | `str` \| `None`        | The ID of the user who created the dicreoll          |
| `character_id`         | `str` \| `None`        | The ID of the character who created the dicreoll     |
| `campaign_id`          | `str` \| `None`        | The ID of the campaign who created the dicreoll      |
| `company_id`           | `str`                  | The ID of the company who created the dicreoll       |
| `result`               | `DiceRollResultSchema` | The result of the dicreoll                           |

### `DiceRollResultSchema`

Represents the result of a dice roll.

| Field                        | Type             | Description                                          |
| ---------------------------- | ---------------- | ---------------------------------------------------- |
| `total_result`               | `int` \| `None`  | The total result of the dice roll                    |
| `total_result_type`          | `RollResultType` | The type of the total result                         |
| `total_result_humanized`     | `str` \| `None`  | The humanized total result                           |
| `total_dice_roll`            | `list[int]`      | The list of dice rolls used for the total result     |
| `player_roll`                | `list[int]`      | The list of dice rolls used for the player roll      |
| `desperation_roll`           | `list[int]`      | The list of dice rolls used for the desperation roll |
| `total_dice_roll_emoji`      | `str` \| `None`  | The emoji for the total dice roll                    |
| `total_dice_roll_shortcode`  | `str` \| `None`  | The shortcode for the total dice roll                |
| `player_roll_emoji`          | `str` \| `None`  | The emoji for the player roll                        |
| `player_roll_shortcode`      | `str` \| `None`  | The shortcode for the player roll                    |
| `desperation_roll_emoji`     | `str` \| `None`  | The emoji for the desperation roll                   |
| `desperation_roll_shortcode` | `str` \| `None`  | The shortcode for the desperation roll               |
