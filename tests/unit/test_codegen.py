"""Tests for vclient._codegen AST transformer."""

import ast
import textwrap

from vclient._codegen import AsyncToSyncTransformer


class TestAsyncToSyncTransformer:
    """Tests for the AsyncToSyncTransformer AST node transformer."""

    def _transform(self, source: str) -> str:
        """Parse source, apply the transformer, and return unparsed code.

        Args:
            source: Python source code string to transform.

        Returns:
            The transformed source code as a string.
        """
        tree = ast.parse(textwrap.dedent(source))
        transformer = AsyncToSyncTransformer()
        new_tree = transformer.visit(tree)
        ast.fix_missing_locations(new_tree)
        return ast.unparse(new_tree)

    def test_async_def_becomes_def(self) -> None:
        """Verify async function definitions are converted to synchronous definitions."""
        # Given: An async function definition
        source = """
        async def fetch_data():
            return 42
        """

        # When: The transformer processes the source
        result = self._transform(source)

        # Then: The function is no longer async
        assert "async def" not in result
        assert "def fetch_data():" in result

    def test_await_is_unwrapped(self) -> None:
        """Verify await expressions are unwrapped to plain expressions."""
        # Given: A function containing an await expression
        source = """
        async def fetch_data():
            result = await get_result()
            return result
        """

        # When: The transformer processes the source
        result = self._transform(source)

        # Then: The await keyword is removed, leaving the plain call
        assert "await" not in result
        assert "result = get_result()" in result

    def test_async_with_becomes_with(self) -> None:
        """Verify async with statements are converted to plain with statements."""
        # Given: A function containing an async with statement
        source = """
        async def connect():
            async with open_connection() as conn:
                pass
        """

        # When: The transformer processes the source
        result = self._transform(source)

        # Then: async with becomes plain with
        assert "async with" not in result
        assert "with open_connection() as conn:" in result

    def test_async_for_becomes_for(self) -> None:
        """Verify async for loops are converted to plain for loops."""
        # Given: A function containing an async for loop
        source = """
        async def iterate():
            async for item in get_items():
                process(item)
        """

        # When: The transformer processes the source
        result = self._transform(source)

        # Then: async for becomes plain for
        assert "async for" not in result
        assert "for item in get_items():" in result

    def test_async_iterator_becomes_iterator(self) -> None:
        """Verify AsyncIterator type annotations are replaced with Iterator."""
        # Given: A function returning AsyncIterator
        source = """
        async def iter_items() -> AsyncIterator[str]:
            yield "item"
        """

        # When: The transformer processes the source
        result = self._transform(source)

        # Then: AsyncIterator is replaced with Iterator
        assert "AsyncIterator" not in result
        assert "Iterator" in result

    def test_asyncio_sleep_becomes_time_sleep(self) -> None:
        """Verify asyncio.sleep() calls are replaced with time.sleep()."""
        # Given: A function calling asyncio.sleep
        source = """
        async def wait():
            await asyncio.sleep(1)
        """

        # When: The transformer processes the source
        result = self._transform(source)

        # Then: asyncio.sleep is replaced with time.sleep
        assert "asyncio.sleep" not in result
        assert "time.sleep(1)" in result

    def test_aclose_becomes_close(self) -> None:
        """Verify .aclose() method calls are replaced with .close()."""
        # Given: A function calling aclose
        source = """
        async def cleanup():
            await client.aclose()
        """

        # When: The transformer processes the source
        result = self._transform(source)

        # Then: aclose is replaced with close
        assert "aclose" not in result
        assert "client.close()" in result

    def test_aenter_becomes_enter(self) -> None:
        """Verify __aenter__ method names are replaced with __enter__."""
        # Given: A class with __aenter__ method
        source = """
        class MyClient:
            async def __aenter__(self):
                return self
        """

        # When: The transformer processes the source
        result = self._transform(source)

        # Then: __aenter__ is replaced with __enter__
        assert "__aenter__" not in result
        assert "__enter__" in result

    def test_aexit_becomes_exit(self) -> None:
        """Verify __aexit__ method names are replaced with __exit__."""
        # Given: A class with __aexit__ method
        source = """
        class MyClient:
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                await self.close()
        """

        # When: The transformer processes the source
        result = self._transform(source)

        # Then: __aexit__ is replaced with __exit__
        assert "__aexit__" not in result
        assert "__exit__" in result

    def test_httpx_async_client_becomes_client(self) -> None:
        """Verify httpx.AsyncClient references are replaced with httpx.Client."""
        # Given: Code referencing httpx.AsyncClient
        source = """
        def create_client():
            return httpx.AsyncClient()
        """

        # When: The transformer processes the source
        result = self._transform(source)

        # Then: AsyncClient is replaced with Client
        assert "AsyncClient" not in result
        assert "httpx.Client()" in result

    def test_async_list_comprehension(self) -> None:
        """Verify async list comprehensions are converted to sync."""
        # Given: A function with an async list comprehension
        source = """
        async def collect():
            return [item async for item in aiterable]
        """

        # When: The transformer processes the source
        result = self._transform(source)

        # Then: The async keyword is removed from the comprehension
        assert "async for" not in result
        assert "[item for item in aiterable]" in result

    def test_import_asyncio_becomes_import_time(self) -> None:
        """Verify 'import asyncio' is replaced with 'import time'."""
        # Given: An asyncio import
        source = """
        import asyncio
        """

        # When: The transformer processes the source
        result = self._transform(source)

        # Then: asyncio import is replaced with time import
        assert "import asyncio" not in result
        assert "import time" in result

    def test_import_from_rewrite(self) -> None:
        """Verify vclient import paths are rewritten to vclient._sync paths."""
        # Given: An import from vclient.services.base
        source = """
        from vclient.services.base import BaseService
        """

        # When: The transformer processes the source
        result = self._transform(source)

        # Then: The import path is rewritten and class name is renamed
        assert "vclient._sync.services.base" in result
        assert "SyncBaseService" in result

    def test_class_def_rename(self) -> None:
        """Verify service class definitions are renamed to Sync* versions."""
        # Given: A class definition for a service
        source = """
        class BaseService:
            pass
        """

        # When: The transformer processes the source
        result = self._transform(source)

        # Then: The class is renamed
        assert "class SyncBaseService:" in result

    def test_factory_function_rename(self) -> None:
        """Verify factory function definitions are renamed to sync_* versions."""
        # Given: A factory function definition
        source = """
        def companies_service():
            pass
        """

        # When: The transformer processes the source
        result = self._transform(source)

        # Then: The function is renamed
        assert "def sync_companies_service():" in result

    def test_constant_string_annotation_rename(self) -> None:
        """Verify string annotations containing class names are renamed."""
        # Given: A function with a string type annotation
        source = """
        def get_client() -> "VClient":
            pass
        """

        # When: The transformer processes the source
        result = self._transform(source)

        # Then: The string annotation is renamed
        assert "SyncVClient" in result

    def test_name_reference_rename(self) -> None:
        """Verify class name references in code are renamed."""
        # Given: Code referencing a service class by name
        source = """
        def create():
            return CompaniesService(client)
        """

        # When: The transformer processes the source
        result = self._transform(source)

        # Then: The class name reference is renamed
        assert "SyncCompaniesService" in result

    def test_vclient_class_rename(self) -> None:
        """Verify VClient class definition is renamed to SyncVClient."""
        # Given: A VClient class definition
        source = """
        class VClient:
            pass
        """

        # When: The transformer processes the source
        result = self._transform(source)

        # Then: VClient is renamed to SyncVClient
        assert "class SyncVClient:" in result

    def test_import_from_vclient_client_rewrite(self) -> None:
        """Verify imports from vclient.client are rewritten correctly."""
        # Given: An import from vclient.client
        source = """
        from vclient.client import VClient
        """

        # When: The transformer processes the source
        result = self._transform(source)

        # Then: Both path and name are rewritten
        assert "vclient._sync.client" in result
        assert "SyncVClient" in result

    def test_import_from_vclient_registry_rewrite(self) -> None:
        """Verify imports from vclient.registry are rewritten correctly."""
        # Given: An import from vclient.registry
        source = """
        from vclient.registry import configure_default_client
        """

        # When: The transformer processes the source
        result = self._transform(source)

        # Then: Path is rewritten and function name is renamed
        assert "vclient._sync.registry" in result
        assert "sync_configure_default_client" in result

    def test_multiple_transforms_combined(self) -> None:
        """Verify multiple transformations work together on realistic code."""
        # Given: A realistic async service method
        source = """
        async def fetch_all():
            async with httpx.AsyncClient() as client:
                result = await client.get("/data")
                return result
        """

        # When: The transformer processes the source
        result = self._transform(source)

        # Then: All async constructs are removed
        assert "async" not in result
        assert "await" not in result
        assert "AsyncClient" not in result
        assert "def fetch_all():" in result
        assert "with httpx.Client() as client:" in result
        assert "result = client.get('/data')" in result

    def test_async_set_comprehension(self) -> None:
        """Verify async set comprehensions are converted to sync."""
        # Given: A function with an async set comprehension
        source = """
        async def collect():
            return {item async for item in aiterable}
        """

        # When: The transformer processes the source
        result = self._transform(source)

        # Then: The async keyword is removed from the comprehension
        assert "async for" not in result
        assert "{item for item in aiterable}" in result

    def test_async_generator_expression(self) -> None:
        """Verify async generator expressions are converted to sync."""
        # Given: A function with an async generator expression
        source = """
        async def collect():
            return list(item async for item in aiterable)
        """

        # When: The transformer processes the source
        result = self._transform(source)

        # Then: The async keyword is removed from the generator
        assert "async for" not in result
        assert "item for item in aiterable" in result
