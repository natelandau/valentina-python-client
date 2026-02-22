# Design: Asset Listing Methods for All Services

## Problem

The 5 services with asset endpoints (Users, Campaigns, Characters, Books, Chapters) only expose `list_assets()` which returns a single paginated page. All other sub-resources (notes, inventory, gifts, rites, edges) follow a three-method convention: `get_X_page()`, `list_all_X()`, `iter_all_X()`. Assets should follow the same pattern.

## Scope

### Services affected

- `UsersService` (users.py)
- `CampaignsService` (campaigns.py)
- `CharactersService` (characters.py)
- `BooksService` (campaign_books.py)
- `ChaptersService` (campaign_book_chapters.py)

### Changes per service

1. **Rename** `list_assets()` to `get_assets_page()` (breaking change, direct rename)
2. **Add** `list_all_assets()` — returns `list[Asset]`, delegates to `iter_all_assets()`
3. **Add** `iter_all_assets()` — returns `AsyncIterator[Asset]`, delegates to `_iter_all_pages()`

### Method signatures

Each service's parent entity ID parameter varies:

| Service   | Parent param   | Endpoint constant      |
| --------- | -------------- | ---------------------- |
| Users     | `user_id`      | `USER_ASSETS`          |
| Campaigns | `campaign_id`  | `CAMPAIGN_ASSETS`      |
| Characters| `character_id` | `CHARACTER_ASSETS`     |
| Books     | `book_id`      | `BOOK_ASSETS`          |
| Chapters  | `chapter_id`   | `BOOK_CHAPTER_ASSETS`  |

### Tests

- Update existing integration tests referencing `list_assets` to `get_assets_page`
- Add integration tests for `list_all_assets` and `iter_all_assets` per service

### Documentation

- Update service docs in `../valentina-noir/docs/python-api-client/` for each affected service

## Pattern reference

From `CharactersService.get_notes_page` / `list_all_notes` / `iter_all_notes` — the exact pattern to replicate.
