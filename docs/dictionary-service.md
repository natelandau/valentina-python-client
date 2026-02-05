# Dictionary Service

Manage dictionary terms within a company for in-game terminology and definitions.

## Usage

```python
from vclient import dictionary_service

dictionary = dictionary_service(company_id="COMPANY_ID")
```

## Methods

### CRUD Operations

| Method                                            | Returns          | Description       |
| ------------------------------------------------- | ---------------- | ----------------- |
| `get(term_id)`                                    | `DictionaryTerm` | Get a term by ID  |
| `create(DictionaryTermCreate, **kwargs)`          | `DictionaryTerm` | Create a new term |
| `update(term_id, DictionaryTermUpdate, **kwargs)` | `DictionaryTerm` | Update a term     |
| `delete(term_id)`                                 | `None`           | Delete a term     |

### Pagination

| Method                             | Returns                             | Description           |
| ---------------------------------- | ----------------------------------- | --------------------- |
| `get_page(limit?, offset?, term?)` | `PaginatedResponse[DictionaryTerm]` | Get a page of terms   |
| `list_all(term?)`                  | `list[DictionaryTerm]`              | Get all terms         |
| `iter_all(limit?, term?)`          | `AsyncIterator[DictionaryTerm]`     | Iterate through terms |

## Example

```python
from vclient.models import DictionaryTermCreate, DictionaryTermUpdate

# Create a term (preferred: use model object)
request = DictionaryTermCreate(
    term="Embrace",
    definition="The act of turning a mortal into a vampire",
    synonyms=["Turn", "Siring"]
)
term = await dictionary.create(request)

# Alternative: pass fields as kwargs
term = await dictionary.create(
    term="Embrace",
    definition="The act of turning a mortal into a vampire",
    synonyms=["Turn", "Siring"]
)

# Update a term
update = DictionaryTermUpdate(definition="Updated definition")
updated = await dictionary.update(term.id, update)

# Search for a term
terms = await dictionary.list_all(term="Embrace")
```

See [Response Models](models.md) for `DictionaryTerm`.
