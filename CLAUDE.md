# Project Instructions

This document contains coding standards and guidelines for the valentina-api-client project.

## Tooling

### Python Package Management

Use `uv` exclusively for Python package management. Never use pip, pip-tools, poetry, or conda directly.

- Install dependencies: `uv add <package>`
- Remove dependencies: `uv remove <package>`
- Sync dependencies: `uv sync`
- Run Python scripts: `uv run <script-name>.py`
- Run Python tools: `uv run pytest` or `uv run ruff`
- Launch Python REPL: `uv run python`

### Preferred Tools

- pytest for testing
- pytest-mock for mocking
- loguru for logging
- rich for pretty printing
- Pathlib for file system operations (not os.path or os)
- When reporting errors to the console, use `logger.error` instead of print

### Linting

After making changes to Python files, run the lint command to verify changes pass all checks:

```bash
uv run duty lint
```

## Global Coding Standards

### Core Principles

- Only modify code directly relevant to the specific request
- Break problems into smaller steps and think through each step before implementing
- Provide a clear plan with reasoning before making changes
- Write comments only in English
- Make minimal changes - modify only what's necessary to complete the task

### Software Development Principles

- **DRY** (Don't Repeat Yourself): Avoid code duplication, extract reusable components
- **KISS** (Keep It Simple, Stupid): Choose simple solutions over complex ones
- **SRP** (Single Responsibility Principle): Functions and classes should have one purpose
- **YAGNI** (You Aren't Gonna Need It): Don't implement functionality until it's necessary

### Clean Code Guidelines

- Choose names for variables, functions, and classes that reflect their purpose and behavior
- Include auxiliary verbs in variable names when appropriate (e.g., `is_active`, `has_permission`)
- Use named constants instead of hard-coded values with meaningful names
- Encapsulate nested conditionals into well-named functions
- Handle errors and edge cases at the beginning of functions
- Use early returns for error conditions to avoid deeply nested if statements
- Use guard clauses to handle preconditions and invalid states early

## Python Standards

### Naming Conventions

- Python files: `snake_case.py` (e.g., `user_handlers.py`, `database_utils.py`)
- Class names: `CamelCase` (e.g., `UserHandler`, `DatabaseConnection`)
- Function names: `snake_case` (e.g., `get_user`, `create_product`)
- Variables: `snake_case` (e.g., `user_id`, `product_name`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_PORT`, `MAX_CONNECTIONS`)

### Type Hints

- Use type hints for all function signatures (parameters and return values)
- Never use `Any` type unless absolutely necessary; use unions or TypeVars instead
- Use `T | None` for nullable types (not `Optional[T]`)
- Use lowercase for type names (e.g., `list[str]` not `List[str]`)
- Use `|` for union types (e.g., `str | None` not `Union[str, None]`)
- Annotate variable types when first mentioned (e.g., `scopes: list[str] = [...]`)

### Best Practices

- Never use mutable default arguments
- Use context managers (`with` statement) for file/resource management
- Use `is` for comparing with `None`, `True`, `False`
- Use f-strings for string formatting
- Use list comprehensions and generator expressions
- Use `enumerate()` instead of manual counter variables

### Class Style

- Keep classes focused on a single responsibility
- Keep `__init__` simple; avoid complex logic
- Use dataclasses for simple data containers
- Prefer composition over inheritance
- Avoid creating additional class functions if not necessary
- Use `@property` for computed attributes

### Exception Handling

- Never silently swallow exceptions without logging
- Never use bare `except:` clauses
- Catch specific exceptions rather than broad exception types
- Use context managers for resource cleanup
- Provide meaningful error messages
- Add messages to a variable before adding it to the exception

### Docstrings

Use Google format docstrings for all public functions, classes, and methods:

- Document function parameters, return values, and exceptions raised
- Write in imperative voice only (never "This function...")
- Be descriptive and explain why a developer would use the function
- Do not use line wraps within paragraphs
- Do not document return when nothing is returned
- Only include raised exceptions if explicitly raised in the code

Example:
```python
def read_config(path: Path = "config.toml", globs: list[str] | None = None) -> list[Path]:
    """Read and validate the TOML configuration file that maps repository names to paths.

    Search the given `path` for files matching any of the glob patterns provided in `globs`. If no globs are provided, returns all files in the directory.

    Args:
        path (Path): The root directory where the search will be conducted.
        globs (list[str] | None, optional): A list of glob patterns to match files. Defaults to None.

    Returns:
        list[Path]: A list of Path objects representing the files that match the glob patterns.

    Raises:
        cappa.Exit: If the config file doesn't exist, contains invalid TOML, or has invalid repository paths
    """
```

### Inline Comments

- Use comments sparingly and make them meaningful
- Don't comment on obvious things
- Only use comments to convey the "why" behind specific actions or explain unusual behavior
- Never change or remove `noqa` or `type: ignore` comments
- Never describe the code; explain the reasoning

## Testing Standards (pytest)

- Review existing fixtures and reuse them if possible
- Write single sentence docstrings in imperative voice starting with "Verify"
- Structure test body with given/when/then comments
- Use pytest-mock plugin (not unittest)
- Include unit and integration tests
- Use fixture factories to create reusable test data
- Use `@pytest.mark.parametrize` for multiple inputs/outputs
- Ensure tests are stateless and independent
- Use `autospec=True` when mocking
- Mock external dependencies to isolate tests

Example:
```python
@pytest.fixture
def user_factory():
    def create_user(username, email):
        return {"username": username, "email": email}
    return create_user

def test_backup_file_creates_backup(tmp_path, mocker, user_factory) -> None:
    """Verify creating backups file with .bak extension."""
    # Given a constant return from module.function
    mock_function = mocker.patch('module.function', autospec=True)
    mock_function.return_value = 'mocked'

    # Given a user
    user = user_factory("testuser", "test@example.com")

    # Given: A test file exists
    file = tmp_path / "test.txt"
    file.write_text("test")

    # When: Creating a backup
    backup_file(file)

    # Then: Backup file exists and original is moved
    expected_backup = file.parent / (file.name + ".bak")
    assert expected_backup.exists()
    assert not file.exists()
```

## API Pydantic Models

Follow these patterns when creating Pydantic models for API services in `src/vclient/api/`.

### Response Models

- Use Pydantic `BaseModel` for all API response DTOs
- Use `model_validate()` to parse API responses into typed objects
- Include all fields from the API response with appropriate types

```python
class Company(BaseModel):
    """Response model for a company."""
    id: str | None = Field(default=None, description="MongoDB document ObjectID.")
    name: str = Field(..., min_length=3, max_length=50)
    email: str = Field(...)
    settings: CompanySettings | None = Field(default=None)
```

### Request Models

- Create separate request models for create/update operations
- Request models should NOT include server-generated fields (id, date_created, etc.)
- Use `exclude_none=True, exclude_unset=True` when serializing

```python
class CreateCompanyRequest(BaseModel):
    """Request body for creating a new company."""
    name: str = Field(..., min_length=3, max_length=50)
    email: str = Field(...)
    description: str | None = Field(default=None)

class UpdateCompanyRequest(BaseModel):
    """Request body for updating a company. All fields optional for partial updates."""
    name: str | None = Field(default=None, min_length=3, max_length=50)
    email: str | None = Field(default=None)
```

### Service Method Pattern

```python
async def create(
    self,
    name: str,
    email: str,
    *,
    description: str | None = None,
) -> Company:
    body = CreateCompanyRequest(name=name, email=email, description=description)
    response = await self._post(
        Endpoints.COMPANIES,
        json=body.model_dump(exclude_none=True, exclude_unset=True, mode="json"),
    )
    return Company.model_validate(response.json())
```

### Literal Type Aliases (Preferred over Enums)

Use `Literal` type aliases instead of `StrEnum` for constrained string fields:

```python
from typing import Literal

PermissionLevel = Literal["USER", "ADMIN", "OWNER", "REVOKE"]

class CompanyPermissions(BaseModel):
    company_id: str = Field(...)
    permission: PermissionLevel = Field(...)
```

### Naming Conventions

- Response models: Entity name (e.g., `Company`, `Developer`)
- Create request: `Create{Entity}Request`
- Update request: `Update{Entity}Request`
- Settings/nested: `{Entity}Settings`

## Git Commit Messages

Use Angular-style conventional commits. The first line should never exceed 50 characters.

Format: `<type>(<scope>): <subject>`

### Types

- `build`: Changes to build system or external dependencies
- `ci`: Changes to CI configuration files and scripts
- `docs`: Documentation only changes
- `feat`: A new feature
- `fix`: A bug fix
- `perf`: A code change that improves performance
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `style`: Changes that do not affect the meaning of the code
- `test`: Adding missing tests or correcting existing tests

### Rules

- Use imperative, present tense: "change" not "changed" nor "changes"
- Don't capitalize the first letter of the subject
- No dot (.) at the end of the subject
- The body should explain WHY you are making the change

### Examples

- `feat: add email notifications on new direct messages`
- `feat(shopping cart): add the amazing button`
- `fix(api): fix wrong calculation of request body checksum`
- `docs(readme): update installation instructions`

## Bash Scripting Standards

When writing bash scripts:

- Use Bash's built-in string manipulation features instead of external commands when possible
- Use `[[ ]]` over `[ ]` for string comparisons
- Always quote variables to prevent word splitting and globbing issues
- Avoid using `eval`
- Use `$(command)` instead of backticks for command substitution
- Use `local` within functions to minimize global variables
- Use `set -e` to exit on errors automatically
- Use `printf` for formatted output instead of `echo`
- Use `mktemp` for temporary files and clean them up when finished

## Documentation Style

When writing documentation for README.md and docs/*.md:

- Write for end users, not developers of this package
- Simple over complex: Use everyday words
- Active over passive: "Generate reports" not "Reports are generated"
- Imperative voice: "Create a report" not "Creates a report"
- Be specific, avoid vague words like "streamline," "optimize," "innovative"
- All code examples should be runnable and verified
