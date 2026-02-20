# Codebase Concerns

**Analysis Date:** 2026-02-20

## Tech Debt

### Constants Formatting Issue
- Issue: `constants.py` lines 52, 56, and 62 have leading space indentation (likely from copy-paste)
- Files: `src/vclient/constants.py` (lines 52, 56, 62)
- Impact: Code style inconsistency; lines with `GrantXPPermission`, `PermissionLevel`, and `SpecialtyType` have incorrect indentation while still syntactically valid Python
- Fix approach: Remove leading space from lines 52, 56, and 62 to match surrounding constant definitions

### Global State in Registry Without Thread Safety
- Issue: `_default_client` module-level variable with no locking mechanism
- Files: `src/vclient/registry.py` (line 43, 63-64, 77-79)
- Impact: In multi-threaded environments or concurrent async contexts, race conditions could occur when multiple threads/tasks configure/clear the default client simultaneously
- Fix approach: Consider using `threading.Lock` or async-safe mechanisms if thread-safe behavior is needed, or add documentation clarifying this is for single-threaded/single-async-loop use

### Large Service Classes
- Issue: Service classes exceed 1000+ lines with many methods
- Files: `src/vclient/services/characters.py` (1380 lines), `src/vclient/services/users.py` (917 lines)
- Impact: High cognitive complexity; difficult to navigate; easier to introduce bugs in methods; harder to test isolated functionality
- Fix approach: Consider breaking large services into focused sub-services (e.g., `CharacterAssetsService`, `CharacterNotesService`) or using composition patterns

## Known Issues

### No Validation That Client Is Open Before Requests
- Issue: No checks prevent using a closed VClient for requests
- Files: `src/vclient/client.py` (209-211), all service classes calling `_http`
- Trigger: Call any service method after `await client.close()`; will silently fail or raise cryptic httpx errors
- Workaround: Manually check `client.is_closed` before using, though this is not enforced by the API
- Impact: Error messages from httpx are less helpful than a clear "client is closed" error

### Pagination Edge Case: Division by Zero in total_pages
- Issue: `PaginatedResponse.total_pages` returns 0 when `limit == 0`
- Files: `src/vclient/models/pagination.py` (lines 52-55)
- Trigger: If API returns a page with `limit: 0`, calculation becomes `(total + 0 - 1) // 0`
- Impact: Will raise `ZeroDivisionError` if accessed; though limit should never be 0 in practice
- Fix approach: Add guard or handle edge case explicitly

### Missing Validation of File Sizes During Upload
- Issue: File upload methods accept `bytes` with no size limit checking
- Files: `src/vclient/services/characters.py` (lines 411-440), and similar in other services (campaigns, chapters, users)
- Trigger: Upload large file (>API limit, typically 10MB+) without client-side validation
- Impact: Entire large file is buffered in memory and sent, only to fail server-side; poor user experience and wasted bandwidth
- Fix approach: Add optional `max_size_bytes` parameter to upload methods; validate and raise `ValidationError` before sending if exceeded

## Security Considerations

### API Key Visible in User-Agent and Logging
- Risk: If httpx logs full request headers or if user misconfigures logging
- Files: `src/vclient/client.py` (lines 165-179), `src/vclient/services/base.py` (lines 174, 284)
- Current mitigation: API key is only added to headers, not to user-agent; request logger only binds method/url, not headers
- Recommendations: Document that users should not enable httpx debug logging; consider masking headers in error messages; add note to CLAUDE.md about logging best practices

### Environment Variable Secret Access
- Risk: `.env.secret` file could be exposed if not properly gitignored
- Files: `scripts/validate_constants.py` (reads `.env.secret`)
- Current mitigation: `.env.secret` is in `.gitignore`; note in README advises this
- Recommendations: Verify `.env.secret` is never accidentally committed; consider using `python-dotenv` or asking for explicit env var instead of reading file

## Performance Bottlenecks

### Memory Usage During list_all() on Large Datasets
- Problem: `list_all()` collects all items into a list in memory before returning
- Files: `src/vclient/services/base.py` (lines 689-710)
- Cause: Convenience method materializes entire result set; for millions of items, this is a memory leak
- Improvement path: Encourage users to use `iter_all()` instead; consider adding docstring warning or renaming to emphasize materialization

### Retry Logic Blocks on Backoff Delays
- Problem: `await asyncio.sleep(delay)` in retry loop blocks the event loop
- Files: `src/vclient/services/base.py` (lines 196, 203, 221, 227, 239, 246)
- Cause: While `asyncio.sleep()` is correct async, the exponential backoff can reach 8+ seconds for high attempt counts (8+ seconds on attempt 3 with base 1s delay)
- Improvement path: Document maximum retry wait times in docstrings; consider adding `max_backoff_delay` config parameter to cap wait time

### N+1 Pagination Pattern in _iter_all_pages
- Problem: Each page requires a separate HTTP request; no prefetching or batching
- Files: `src/vclient/services/base.py` (lines 645-687)
- Cause: By design—sequential pagination is correct, but slower for users who want all data
- Improvement path: This is acceptable; document that users should tune `limit` parameter (use MAX_PAGE_LIMIT for faster fetching)

## Fragile Areas

### CharacterCreate Model Validation
- Files: `src/vclient/models/characters.py` (model definition), `src/vclient/services/characters.py` (create/update methods)
- Why fragile: Complex nested models with many optional fields; Pydantic validation errors can be verbose and hard to parse; no client-side field documentation
- Safe modification: Always run `uv run pytest tests/unit/models/test_characters.py -x` after changing any CharacterCreate or related model; add new test case for each new optional field
- Test coverage: Integration tests exist in `tests/integration/services/test_characters.py`; mock all responses

### Exception Handling in _raise_for_status
- Files: `src/vclient/services/base.py` (lines 277-282)
- Why fragile: Bare `except (ValueError, KeyError, TypeError)` could mask legitimate errors; if response structure changes, silent failures occur
- Safe modification: Only catch specific JSON parsing errors; log the raw response text when parsing fails
- Test coverage: Integration tests mock responses; add test case for malformed JSON response from API

### Pagination Continuation Assumption
- Files: `src/vclient/services/base.py` (lines 671-687)
- Why fragile: `_iter_all_pages` relies on `page.has_more` and `page.next_offset` being correct; if API pagination is buggy, infinite loops or data skips could occur
- Safe modification: Add timeout/max_pages guard to prevent infinite loops; test with intentionally malformed pagination responses
- Test coverage: Unit tests don't mock pagination edge cases (offset > total, limit mismatch); add integration tests for these scenarios

## Scaling Limits

### Default Client Registry As Single Global
- Current capacity: One active default client per Python process
- Limit: Cannot use multiple simultaneous clients with factory functions (e.g., `companies_service()` always uses same client)
- Scaling path: Users must either (1) not use factory functions and pass client explicitly, or (2) reassign default client repeatedly—both are awkward

### HTTP Connection Pool Not Configurable
- Current capacity: httpx.AsyncClient default pool limits (100 connections per host)
- Limit: If processing >100 concurrent requests, connection pooling becomes a bottleneck
- Scaling path: Expose `httpx.AsyncClient` pool configuration in VClient constructor (pool_limits, pool_timeout, etc.)

## Dependencies at Risk

### Pydantic v2 Type Validation Strictness
- Risk: Pydantic v2 is stricter than v1; may reject valid data if API schema drifts
- Impact: If API adds unexpected fields or changes types, validation will fail
- Migration plan: Already using Pydantic v2 (field mode='json'); consider using `ConfigDict(extra='allow')` for future-proofing if API evolution is expected

### httpx Dependency on Python 3.13+
- Risk: Python 3.13 reaches end-of-life in 2026; httpx may drop support
- Impact: Users stuck on older Python versions; potential security gaps
- Migration plan: Monitor httpx releases; be prepared to update min Python version or switch to alternative HTTP library

## Missing Critical Features

### No Request/Response Logging Middleware
- Problem: Users cannot easily see full request/response bodies for debugging; only structured fields logged
- Blocks: Debugging integration issues; understanding API behavior
- Recommendation: Add optional `verbose` mode or middleware hook for full request/response logging (with API key redaction)

### No Built-in Retry Jitter Configuration
- Problem: All clients retry with same jitter (0-25%); thundering herd risk if many clients retry simultaneously
- Blocks: Advanced retry strategies for high-concurrency scenarios
- Recommendation: Expose `jitter_factor` or `jitter_seed` in VClient constructor

### No Request Timeout Per Method
- Problem: Global timeout applies to all requests; cannot override for slow endpoints
- Blocks: Calling slow API endpoints without timeout; calling fast endpoints with conservative global timeout
- Recommendation: Allow per-method `timeout` override in service method signatures

## Test Coverage Gaps

### Integration Tests Don't Cover Error Scenarios
- What's not tested: Server errors (5xx), malformed JSON responses, rate limit edge cases
- Files: `tests/integration/services/` (17 service test files), all using respx mocking
- Risk: Real error handling code paths never exercised; bugs in `_raise_for_status` won't be caught
- Priority: Medium—add error response fixtures and test each exception type

### Model Validation Tests Missing Edge Cases
- What's not tested: Empty nested lists, None values in required fields, Unicode in string fields
- Files: `tests/unit/models/` (model test files)
- Risk: Invalid models could be created; validation bypassed if user manually constructs models
- Priority: Medium—add parametrized tests for boundary values

### Factory Function Tests Missing Multiple Clients
- What's not tested: Calling factory function after client closed, switching between multiple clients
- Files: `tests/unit/test_registry.py`, `tests/integration/test_client.py`
- Risk: Registry state issues not detected; race conditions in multi-client scenarios
- Priority: Low—rarely occurs in production, but important for advanced users

### Pagination Tests Don't Cover Offset Arithmetic
- What's not tested: Offset > total, offset + limit > total, limit = 0, total = 0
- Files: `tests/unit/models/test_pagination.py`
- Risk: Edge cases in `has_more`, `next_offset`, `total_pages`, `current_page` calculations
- Priority: Low—low likelihood but high impact if occurs

### Service Scoping Not Validated
- What's not tested: Mismatched scoping IDs (company_id, user_id, campaign_id) in nested services
- Files: Service tests assume correct scoping
- Risk: Silent failures if user passes wrong IDs to nested services
- Priority: Low—user responsibility to pass correct IDs, but integration tests should verify endpoint format

---

*Concerns audit: 2026-02-20*
