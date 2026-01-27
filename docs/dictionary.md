# Dictionary Service

The Dictionary Service provides methods to create, retrieve, update, and delete dictionary terms within a company.

## Usage

```python
from vclient import dictionary_service

dictionary = dictionary_service("company123")

# Create a new dictionary term
term = await dictionary.create(term="Test Term", definition="A test definition", link="https://example.com", is_global=False, synonyms=["Test Synonym", "Test Synonym 2"])

# Get a dictionary term
term = await dictionary.get("term123")

# Update a dictionary term
await dictionary.update(term_id="term123", term="Updated Term", definition="An updated definition", link="https://example.com", is_global=True, synonyms=["Updated Synonym", "Updated Synonym 2"])

# Delete a dictionary term
await dictionary.delete("term123")
```

## Available Methods

This service supports all common CRUD and pagination methods:

- `get(term_id)` - Retrieve a dictionary term by ID
- `create(term, definition?, link?, is_global?, company_id?, synonyms?)` - Create a new dictionary term
- `update(term_id, term?, definition?, link?, is_global?, company_id?, synonyms?)` - Update a dictionary term
- `delete(term_id)` - Delete a dictionary term
- `get_page(limit?, offset?, term?)` - Get a paginated page of dictionary terms
- `list_all(term?)` - Get all dictionary terms
- `iter_all(limit?, term?)` - Iterate through all dictionary terms

## Response Models

### `DictionaryTerm`

Represents a dictionary term returned from the API.

| Field           | Type          | Description                                     |
| --------------- | ------------- | ----------------------------------------------- |
| `id`            | `str`         | MongoDB document ObjectID                       |
| `date_created`  | `datetime`    | Timestamp when the dictionary term was created  |
| `date_modified` | `datetime`    | Timestamp when the dictionary term was modified |
| `term`          | `str`         | Dictionary term name (3-50 characters)          |
| `definition`    | `str \| None` | Dictionary term definition                      |
| `link`          | `str \| None` | Dictionary term link                            |
| `synonyms`      | `list[str]`   | List of synonyms for the dictionary term        |
