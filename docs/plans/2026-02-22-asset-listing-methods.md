# Asset Listing Methods Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add `get_assets_page()`, `list_all_assets()`, and `iter_all_assets()` to all 5 asset-bearing services, replacing the current `list_assets()` method to follow established conventions.

**Architecture:** Each service gets the same three-method pattern already used by notes, inventory, gifts, rites, and edges. `get_assets_page()` replaces the existing `list_assets()`. `list_all_assets()` delegates to `iter_all_assets()`. `iter_all_assets()` uses `_iter_all_pages()` from BaseService.

**Tech Stack:** Python 3.13+, Pydantic v2, httpx (async), respx (test mocking)

---

## Working Directory

All commands must be run from the worktree: `/Users/natelandau/repos/valentina-python-client/.worktrees/feat-asset-listing`

## Reference Pattern

The notes methods in `CharactersService` (`src/vclient/services/characters.py:450-525`) are the canonical pattern. Each service's asset section will mirror this structure exactly, substituting `Asset` for `Note` and the appropriate parent ID parameter.

---

### Task 1: CampaignsService — Rename and Add Methods

**Files:**
- Modify: `src/vclient/services/campaigns.py:252-278` (rename `list_assets` → `get_assets_page`, add two methods)

**Step 1: Rename `list_assets` to `get_assets_page` and add `list_all_assets` and `iter_all_assets`**

In `src/vclient/services/campaigns.py`, replace the `list_assets` method (lines 252-278) with:

```python
    async def get_assets_page(
        self,
        campaign_id: str,
        *,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
    ) -> PaginatedResponse[Asset]:
        """Retrieve a paginated page of assets for a campaign.

        Args:
            campaign_id: The ID of the campaign whose assets to list.
            limit: Maximum number of items to return (0-100, default 10).
            offset: Number of items to skip from the beginning (default 0).

        Returns:
            A PaginatedResponse containing Asset objects and pagination metadata.

        Raises:
            NotFoundError: If the campaign does not exist.
            AuthorizationError: If you don't have access.
        """
        return await self._get_paginated_as(
            self._format_endpoint(Endpoints.CAMPAIGN_ASSETS, campaign_id=campaign_id),
            Asset,
            limit=limit,
            offset=offset,
        )

    async def list_all_assets(
        self,
        campaign_id: str,
    ) -> list[Asset]:
        """Retrieve all assets for a campaign.

        Automatically paginates through all results. Use `get_assets_page()` for paginated
        access or `iter_all_assets()` for memory-efficient streaming of large datasets.

        Args:
            campaign_id: The ID of the campaign whose assets to list.

        Returns:
            A list of all Asset objects.

        Raises:
            NotFoundError: If the campaign does not exist.
            AuthorizationError: If you don't have access.
        """
        return [asset async for asset in self.iter_all_assets(campaign_id)]

    async def iter_all_assets(
        self,
        campaign_id: str,
        *,
        limit: int = 100,
    ) -> AsyncIterator[Asset]:
        """Iterate through all assets for a campaign.

        Yields individual assets, automatically fetching subsequent pages until
        all items have been retrieved.

        Args:
            campaign_id: The ID of the campaign whose assets to iterate.
            limit: Items per page (default 100 for efficiency).

        Yields:
            Individual Asset objects.

        Example:
            >>> async for asset in campaigns.iter_all_assets("campaign_id"):
            ...     print(asset.original_filename)
        """
        async for item in self._iter_all_pages(
            self._format_endpoint(Endpoints.CAMPAIGN_ASSETS, campaign_id=campaign_id),
            limit=limit,
        ):
            yield Asset.model_validate(item)
```

**Step 2: Update test — rename `test_list_assets` to `test_get_assets_page` and add `test_list_all_assets`**

In `tests/integration/services/test_campaigns.py`, rename the existing test and add a new one. The existing `test_list_assets` (line 442) becomes `test_get_assets_page`, and `list_assets(campaign_id)` on line 462 becomes `get_assets_page(campaign_id)`.

Add a new test `test_list_all_assets` in the same class, following the pattern from `test_list_all_notes` in `tests/integration/services/test_campaign_books.py:490-518`:

```python
    @respx.mock
    async def test_list_all_assets(self, vclient, base_url, asset_response_data):
        """Verify list_all_assets returns all assets."""
        # Given: A mocked assets endpoint
        company_id = "company123"
        user_id = "user123"
        campaign_id = "campaign123"
        respx.get(
            f"{base_url}{Endpoints.CAMPAIGN_ASSETS.format(company_id=company_id, user_id=user_id, campaign_id=campaign_id)}",
            params={"limit": "100", "offset": "0"},
        ).respond(
            200,
            json={
                "items": [asset_response_data],
                "limit": 100,
                "offset": 0,
                "total": 1,
            },
        )

        # When: Calling list_all_assets
        result = await vclient.campaigns(user_id, company_id).list_all_assets(campaign_id)

        # Then: Returns list of Asset objects
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], Asset)
```

**Step 3: Run tests to verify**

Run: `cd /Users/natelandau/repos/valentina-python-client/.worktrees/feat-asset-listing && uv run pytest tests/integration/services/test_campaigns.py -x --tb=short -q`

Expected: All tests pass.

**Step 4: Lint and commit**

```bash
cd /Users/natelandau/repos/valentina-python-client/.worktrees/feat-asset-listing
uv run ruff check src/vclient/services/campaigns.py tests/integration/services/test_campaigns.py --fix
uv run ruff format src/vclient/services/campaigns.py tests/integration/services/test_campaigns.py
git add src/vclient/services/campaigns.py tests/integration/services/test_campaigns.py
git commit -m "feat(campaigns): add get_assets_page, list_all_assets, iter_all_assets

Rename list_assets to get_assets_page and add list_all_assets and
iter_all_assets methods following the convention used by notes and
other sub-resources."
```

---

### Task 2: CharactersService — Rename and Add Methods

**Files:**
- Modify: `src/vclient/services/characters.py:336-362` (rename `list_assets` → `get_assets_page`, add two methods)

**Step 1: Rename `list_assets` to `get_assets_page` and add `list_all_assets` and `iter_all_assets`**

Same pattern as Task 1 but with `character_id` parameter and `CHARACTER_ASSETS` endpoint. Replace lines 336-362 with the three methods. The entity description in docstrings should say "character" instead of "campaign".

**Step 2: Update test — rename and add in `tests/integration/services/test_characters.py`**

Rename `test_list_assets` (line 947) to `test_get_assets_page`, update the `.list_assets(` call on line 967 to `.get_assets_page(`. Add `test_list_all_assets` following the same pattern as Task 1, using `CHARACTER_ASSETS` endpoint format with `company_id`, `user_id`, `campaign_id`, `character_id`.

**Step 3: Run tests**

Run: `cd /Users/natelandau/repos/valentina-python-client/.worktrees/feat-asset-listing && uv run pytest tests/integration/services/test_characters.py -x --tb=short -q`

**Step 4: Lint and commit**

```bash
cd /Users/natelandau/repos/valentina-python-client/.worktrees/feat-asset-listing
uv run ruff check src/vclient/services/characters.py tests/integration/services/test_characters.py --fix
uv run ruff format src/vclient/services/characters.py tests/integration/services/test_characters.py
git add src/vclient/services/characters.py tests/integration/services/test_characters.py
git commit -m "feat(characters): add get_assets_page, list_all_assets, iter_all_assets

Rename list_assets to get_assets_page and add list_all_assets and
iter_all_assets methods following the convention used by notes and
other sub-resources."
```

---

### Task 3: UsersService — Rename and Add Methods

**Files:**
- Modify: `src/vclient/services/users.py:278-304` (rename `list_assets` → `get_assets_page`, add two methods)

**Step 1: Rename and add methods**

Same pattern with `user_id` parameter and `USER_ASSETS` endpoint. Entity description: "user".

**Step 2: Update test in `tests/integration/services/test_users.py`**

Rename `test_list_assets` (line 485) to `test_get_assets_page`, update `.list_assets(` on line 504 to `.get_assets_page(`. Add `test_list_all_assets` using `USER_ASSETS` endpoint format with `company_id`, `user_id`.

**Step 3: Run tests**

Run: `cd /Users/natelandau/repos/valentina-python-client/.worktrees/feat-asset-listing && uv run pytest tests/integration/services/test_users.py -x --tb=short -q`

**Step 4: Lint and commit**

```bash
cd /Users/natelandau/repos/valentina-python-client/.worktrees/feat-asset-listing
uv run ruff check src/vclient/services/users.py tests/integration/services/test_users.py --fix
uv run ruff format src/vclient/services/users.py tests/integration/services/test_users.py
git add src/vclient/services/users.py tests/integration/services/test_users.py
git commit -m "feat(users): add get_assets_page, list_all_assets, iter_all_assets

Rename list_assets to get_assets_page and add list_all_assets and
iter_all_assets methods following the convention used by notes and
other sub-resources."
```

---

### Task 4: BooksService — Rename and Add Methods

**Files:**
- Modify: `src/vclient/services/campaign_books.py:441-467` (rename `list_assets` → `get_assets_page`, add two methods)

**Step 1: Rename and add methods**

Same pattern with `book_id` parameter and `BOOK_ASSETS` endpoint. Entity description: "book".

**Step 2: Update test in `tests/integration/services/test_campaign_books.py`**

Rename `test_list_assets` (line 616) to `test_get_assets_page`, update `.list_assets(` on line 637 to `.get_assets_page(`. Add `test_list_all_assets` using `BOOK_ASSETS` endpoint format with `company_id`, `user_id`, `campaign_id`, `book_id`.

**Step 3: Run tests**

Run: `cd /Users/natelandau/repos/valentina-python-client/.worktrees/feat-asset-listing && uv run pytest tests/integration/services/test_campaign_books.py -x --tb=short -q`

**Step 4: Lint and commit**

```bash
cd /Users/natelandau/repos/valentina-python-client/.worktrees/feat-asset-listing
uv run ruff check src/vclient/services/campaign_books.py tests/integration/services/test_campaign_books.py --fix
uv run ruff format src/vclient/services/campaign_books.py tests/integration/services/test_campaign_books.py
git add src/vclient/services/campaign_books.py tests/integration/services/test_campaign_books.py
git commit -m "feat(books): add get_assets_page, list_all_assets, iter_all_assets

Rename list_assets to get_assets_page and add list_all_assets and
iter_all_assets methods following the convention used by notes and
other sub-resources."
```

---

### Task 5: ChaptersService — Rename and Add Methods

**Files:**
- Modify: `src/vclient/services/campaign_book_chapters.py:345-371` (rename `list_assets` → `get_assets_page`, add two methods)

**Step 1: Rename and add methods**

Same pattern with `chapter_id` parameter and `BOOK_CHAPTER_ASSETS` endpoint. Entity description: "chapter".

**Step 2: Update test in `tests/integration/services/test_campaign_book_chapters.py`**

Rename `test_list_assets` (line 635) to `test_get_assets_page`, update `.list_assets(` on line 659 to `.get_assets_page(`. Add `test_list_all_assets` using `BOOK_CHAPTER_ASSETS` endpoint format with `company_id`, `user_id`, `campaign_id`, `book_id`, `chapter_id`.

**Step 3: Run tests**

Run: `cd /Users/natelandau/repos/valentina-python-client/.worktrees/feat-asset-listing && uv run pytest tests/integration/services/test_campaign_book_chapters.py -x --tb=short -q`

**Step 4: Lint and commit**

```bash
cd /Users/natelandau/repos/valentina-python-client/.worktrees/feat-asset-listing
uv run ruff check src/vclient/services/campaign_book_chapters.py tests/integration/services/test_campaign_book_chapters.py --fix
uv run ruff format src/vclient/services/campaign_book_chapters.py tests/integration/services/test_campaign_book_chapters.py
git add src/vclient/services/campaign_book_chapters.py tests/integration/services/test_campaign_book_chapters.py
git commit -m "feat(chapters): add get_assets_page, list_all_assets, iter_all_assets

Rename list_assets to get_assets_page and add list_all_assets and
iter_all_assets methods following the convention used by notes and
other sub-resources."
```

---

### Task 6: Full Test Suite Verification

**Step 1: Run the full test suite**

Run: `cd /Users/natelandau/repos/valentina-python-client/.worktrees/feat-asset-listing && uv run pytest tests/ -x --tb=short -q`

Expected: All 783+ tests pass (existing 783 + 5 new `test_list_all_assets` tests).

**Step 2: Run full lint**

Run: `cd /Users/natelandau/repos/valentina-python-client/.worktrees/feat-asset-listing && uv run duty lint`

Expected: No errors.

---

### Task 7: Update Documentation

**Files (in separate repo):**
- Modify: `../valentina-noir/docs/python-api-client/campaigns.md`
- Modify: `../valentina-noir/docs/python-api-client/characters.md`
- Modify: `../valentina-noir/docs/python-api-client/users.md`
- Modify: `../valentina-noir/docs/python-api-client/campaign_books.md`
- Modify: `../valentina-noir/docs/python-api-client/campaign_chapters.md`

For each doc file, update the Assets method table to match the Notes pattern. Replace:

```markdown
| `list_assets(entity_id, limit?, offset?)`    | `PaginatedResponse[Asset]` | List assets |
```

With:

```markdown
| `get_assets_page(entity_id, limit?, offset?)`    | `PaginatedResponse[Asset]` | Get a page of assets     |
| `list_all_assets(entity_id)`                      | `list[Asset]`              | Get all assets           |
| `iter_all_assets(entity_id, limit?)`              | `AsyncIterator[Asset]`     | Iterate through assets   |
```

Also update the code examples in each doc file. For example, in `campaigns.md:137`, replace:
```python
assets = await campaigns.list_assets(campaign.id)
```
With:
```python
# List all assets
all_assets = await campaigns.list_all_assets(campaign.id)

# Or iterate for memory efficiency
async for asset in campaigns.iter_all_assets(campaign.id):
    print(asset.original_filename)
```

Use the appropriate entity_id parameter name for each service file (campaign_id, character_id, user_id, book_id, chapter_id).

**Note:** These docs are in a separate repo (`../valentina-noir/`). Commit there separately if the user wants.
