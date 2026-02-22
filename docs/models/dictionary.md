---
icon: lucide/book-a
---

# Dictionary Models

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
