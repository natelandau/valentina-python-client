---
icon: lucide/book-a
---

# Dictionary Models

Models for in-game terminology, definitions, and synonyms specific to your campaigns.

## DictionaryTerm

| Field           | Type          | Description             |
| --------------- | ------------- | ----------------------- |
| `id`            | `str`         | Unique identifier       |
| `date_created`  | `datetime`    | Creation timestamp      |
| `date_modified` | `datetime`    | Last modified timestamp |
| `term`          | `str`         | Term name               |
| `definition`    | `str \| None` | Definition              |
| `link`          | `str \| None` | Reference link          |
| `synonyms`      | `list[str]`   | Synonyms                |
| `company_id`    | `str \| None` | Company ID              |
| `source_type`   | `str \| None` | Source type             |
| `source_id`     | `str \| None` | Source ID               |
