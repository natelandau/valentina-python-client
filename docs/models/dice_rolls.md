---
icon: lucide/dices
---

# Dice Roll Models

## DiceRoll

| Field                  | Type             | Description        |
| ---------------------- | ---------------- | ------------------ |
| `id`                   | `str`            | Unique identifier  |
| `date_created`         | `datetime`       | Creation timestamp |
| `dice_size`            | `DiceSize`       | Dice size          |
| `difficulty`           | `int \| None`    | Target difficulty  |
| `num_dice`             | `int`            | Number of dice     |
| `num_desperation_dice` | `int`            | Desperation dice   |
| `comment`              | `str \| None`    | Roll comment       |
| `trait_ids`            | `list[str]`      | Traits used        |
| `user_id`              | `str \| None`    | User ID            |
| `character_id`         | `str \| None`    | Character ID       |
| `campaign_id`          | `str \| None`    | Campaign ID        |
| `result`               | `DiceRollResult` | Roll result        |

## DiceRollResult

| Field                    | Type             | Description             |
| ------------------------ | ---------------- | ----------------------- |
| `total_result`           | `int \| None`    | Total successes         |
| `total_result_type`      | `RollResultType` | Result type             |
| `total_result_humanized` | `str \| None`    | Human-readable result   |
| `total_dice_roll`        | `list[int]`      | All dice values         |
| `player_roll`            | `list[int]`      | Player dice values      |
| `desperation_roll`       | `list[int]`      | Desperation dice values |
