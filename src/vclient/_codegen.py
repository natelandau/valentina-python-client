"""AST-based code generator that transforms async source files into synchronous equivalents.

Reads the async vclient source as the single source of truth and mechanically
produces a ``vclient._sync`` package with all async constructs removed.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

HEADER_COMMENT = "# AUTO-GENERATED — do not edit. Run 'uv run duty generate_sync' to regenerate.\n"

RENAME_CLASSES: dict[str, str] = {
    "BaseService": "SyncBaseService",
    "BooksService": "SyncBooksService",
    "CampaignsService": "SyncCampaignsService",
    "ChaptersService": "SyncChaptersService",
    "CharacterAutogenService": "SyncCharacterAutogenService",
    "CharacterBlueprintService": "SyncCharacterBlueprintService",
    "CharacterTraitsService": "SyncCharacterTraitsService",
    "CharactersService": "SyncCharactersService",
    "CompaniesService": "SyncCompaniesService",
    "DeveloperService": "SyncDeveloperService",
    "DicerollService": "SyncDicerollService",
    "DictionaryService": "SyncDictionaryService",
    "GlobalAdminService": "SyncGlobalAdminService",
    "OptionsService": "SyncOptionsService",
    "SystemService": "SyncSystemService",
    "UsersService": "SyncUsersService",
    "VClient": "SyncVClient",
}

FACTORY_RENAMES: dict[str, str] = {
    "companies_service": "sync_companies_service",
    "developer_service": "sync_developer_service",
    "global_admin_service": "sync_global_admin_service",
    "system_service": "sync_system_service",
    "users_service": "sync_users_service",
    "campaigns_service": "sync_campaigns_service",
    "books_service": "sync_books_service",
    "chapters_service": "sync_chapters_service",
    "characters_service": "sync_characters_service",
    "character_traits_service": "sync_character_traits_service",
    "character_blueprint_service": "sync_character_blueprint_service",
    "dictionary_service": "sync_dictionary_service",
    "dicerolls_service": "sync_dicerolls_service",
    "options_service": "sync_options_service",
    "character_autogen_service": "sync_character_autogen_service",
    "configure_default_client": "sync_configure_default_client",
    "clear_default_client": "sync_clear_default_client",
    "default_client": "sync_default_client",
}

IMPORT_REWRITES: dict[str, str] = {
    "vclient.client": "vclient._sync.client",
    "vclient.services": "vclient._sync.services",
    "vclient.services.base": "vclient._sync.services.base",
    "vclient.services.companies": "vclient._sync.services.companies",
    "vclient.services.developers": "vclient._sync.services.developers",
    "vclient.services.global_admin": "vclient._sync.services.global_admin",
    "vclient.services.system": "vclient._sync.services.system",
    "vclient.services.users": "vclient._sync.services.users",
    "vclient.services.campaigns": "vclient._sync.services.campaigns",
    "vclient.services.campaign_books": "vclient._sync.services.campaign_books",
    "vclient.services.campaign_book_chapters": "vclient._sync.services.campaign_book_chapters",
    "vclient.services.characters": "vclient._sync.services.characters",
    "vclient.services.character_traits": "vclient._sync.services.character_traits",
    "vclient.services.character_blueprint": "vclient._sync.services.character_blueprint",
    "vclient.services.dictionary": "vclient._sync.services.dictionary",
    "vclient.services.dicerolls": "vclient._sync.services.dicerolls",
    "vclient.services.options": "vclient._sync.services.options",
    "vclient.services.character_autogen": "vclient._sync.services.character_autogen",
    "vclient.registry": "vclient._sync.registry",
}

# Combined lookup for renaming any identifier (class or factory function)
_ALL_RENAMES: dict[str, str] = {**RENAME_CLASSES, **FACTORY_RENAMES}


class AsyncToSyncTransformer(ast.NodeTransformer):
    """Transform async Python source into synchronous equivalents.

    Visit each relevant AST node and mechanically strip or rename async
    constructs so the resulting tree is fully synchronous.
    """

    # ------------------------------------------------------------------
    # Async construct removal
    # ------------------------------------------------------------------

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.FunctionDef:
        """Convert ``async def`` to ``def``, renaming dunder methods."""
        self.generic_visit(node)

        name = node.name
        if name == "__aenter__":
            name = "__enter__"
        elif name == "__aexit__":
            name = "__exit__"
        else:
            name = FACTORY_RENAMES.get(name, name)

        return ast.FunctionDef(
            name=name,
            args=node.args,
            body=node.body,
            decorator_list=node.decorator_list,
            returns=node.returns,
            type_comment=node.type_comment,
        )

    def visit_Await(self, node: ast.Await) -> ast.expr:
        """Unwrap ``await expr`` to just ``expr``."""
        self.generic_visit(node)
        return node.value

    def visit_AsyncWith(self, node: ast.AsyncWith) -> ast.With:
        """Convert ``async with`` to ``with``."""
        self.generic_visit(node)
        return ast.With(items=node.items, body=node.body)

    def visit_AsyncFor(self, node: ast.AsyncFor) -> ast.For:
        """Convert ``async for`` to ``for``."""
        self.generic_visit(node)
        return ast.For(
            target=node.target,
            iter=node.iter,
            body=node.body,
            orelse=node.orelse,
        )

    # ------------------------------------------------------------------
    # Async comprehensions
    # ------------------------------------------------------------------

    def _sync_generators(self, generators: list[ast.comprehension]) -> None:
        """Set ``is_async = 0`` on all generators in-place."""
        for gen in generators:
            gen.is_async = 0

    def visit_ListComp(self, node: ast.ListComp) -> ast.ListComp:
        """Remove async from list comprehension generators."""
        self.generic_visit(node)
        self._sync_generators(node.generators)
        return node

    def visit_SetComp(self, node: ast.SetComp) -> ast.SetComp:
        """Remove async from set comprehension generators."""
        self.generic_visit(node)
        self._sync_generators(node.generators)
        return node

    def visit_GeneratorExp(self, node: ast.GeneratorExp) -> ast.GeneratorExp:
        """Remove async from generator expression generators."""
        self.generic_visit(node)
        self._sync_generators(node.generators)
        return node

    # ------------------------------------------------------------------
    # Name / Attribute renaming
    # ------------------------------------------------------------------

    def visit_Name(self, node: ast.Name) -> ast.Name:
        """Rename ``AsyncIterator`` to ``Iterator`` and service class names."""
        self.generic_visit(node)
        if node.id == "AsyncIterator":
            node.id = "Iterator"
        elif node.id in _ALL_RENAMES:
            node.id = _ALL_RENAMES[node.id]
        return node

    def visit_Attribute(self, node: ast.Attribute) -> ast.Attribute:
        """Rename ``AsyncClient`` to ``Client`` and ``aclose`` to ``close``."""
        self.generic_visit(node)
        if node.attr == "AsyncClient":
            node.attr = "Client"
        elif node.attr == "aclose":
            node.attr = "close"
        elif node.attr in _ALL_RENAMES:
            node.attr = _ALL_RENAMES[node.attr]
        return node

    # ------------------------------------------------------------------
    # Class / function definition renaming
    # ------------------------------------------------------------------

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        """Rename class definitions found in RENAME_CLASSES."""
        self.generic_visit(node)
        if node.name in RENAME_CLASSES:
            node.name = RENAME_CLASSES[node.name]
        return node

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        """Rename factory function definitions found in FACTORY_RENAMES."""
        self.generic_visit(node)
        if node.name in FACTORY_RENAMES:
            node.name = FACTORY_RENAMES[node.name]
        return node

    # ------------------------------------------------------------------
    # String annotations (TYPE_CHECKING)
    # ------------------------------------------------------------------

    def visit_Constant(self, node: ast.Constant) -> ast.Constant:
        """Rename class names inside string annotations."""
        if isinstance(node.value, str):
            value = node.value
            for old, new in _ALL_RENAMES.items():
                value = value.replace(old, new)
            node.value = value
        return node

    # ------------------------------------------------------------------
    # Import rewriting
    # ------------------------------------------------------------------

    def visit_ImportFrom(self, node: ast.ImportFrom) -> ast.ImportFrom:
        """Rewrite ``from vclient.x import Y`` paths and rename imported names."""
        if node.module and node.module in IMPORT_REWRITES:
            node.module = IMPORT_REWRITES[node.module]

        if node.names:
            for alias in node.names:
                if alias.name in _ALL_RENAMES:
                    alias.name = _ALL_RENAMES[alias.name]

        self.generic_visit(node)
        return node

    def visit_Import(self, node: ast.Import) -> ast.Import:
        """Replace ``import asyncio`` with ``import time``."""
        for alias in node.names:
            if alias.name == "asyncio":
                alias.name = "time"
        return node

    # ------------------------------------------------------------------
    # Call rewriting
    # ------------------------------------------------------------------

    def visit_Call(self, node: ast.Call) -> ast.Call:
        """Replace ``asyncio.sleep()`` with ``time.sleep()``."""
        self.generic_visit(node)
        if (
            isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "asyncio"
            and node.func.attr == "sleep"
        ):
            node.func.value.id = "time"
        return node


# ---------------------------------------------------------------------------
# File-level helpers
# ---------------------------------------------------------------------------


def transform_file(source_path: Path) -> str:
    """Read an async source file, transform it, and return the sync version.

    Args:
        source_path: Path to the async Python source file.

    Returns:
        The transformed synchronous source code with a generated header.
    """
    source = source_path.read_text()
    tree = ast.parse(source)
    transformer = AsyncToSyncTransformer()
    new_tree = transformer.visit(tree)
    ast.fix_missing_locations(new_tree)
    return HEADER_COMMENT + ast.unparse(new_tree) + "\n"


def _write_sync_init(path: Path) -> None:
    """Write the ``_sync/__init__.py`` that re-exports public names.

    Args:
        path: Path to the ``_sync/__init__.py`` file to write.
    """
    lines = [
        HEADER_COMMENT,
        "from vclient._sync.client import SyncVClient",
        "from vclient._sync.registry import (",
        "    sync_books_service,",
        "    sync_campaigns_service,",
        "    sync_chapters_service,",
        "    sync_characters_service,",
        "    sync_character_autogen_service,",
        "    sync_character_blueprint_service,",
        "    sync_character_traits_service,",
        "    sync_clear_default_client,",
        "    sync_companies_service,",
        "    sync_configure_default_client,",
        "    sync_default_client,",
        "    sync_developer_service,",
        "    sync_dicerolls_service,",
        "    sync_dictionary_service,",
        "    sync_global_admin_service,",
        "    sync_options_service,",
        "    sync_system_service,",
        "    sync_users_service,",
        ")",
        "",
        "__all__ = [",
        '    "SyncVClient",',
        '    "sync_books_service",',
        '    "sync_campaigns_service",',
        '    "sync_chapters_service",',
        '    "sync_characters_service",',
        '    "sync_character_autogen_service",',
        '    "sync_character_blueprint_service",',
        '    "sync_character_traits_service",',
        '    "sync_clear_default_client",',
        '    "sync_companies_service",',
        '    "sync_configure_default_client",',
        '    "sync_default_client",',
        '    "sync_developer_service",',
        '    "sync_dicerolls_service",',
        '    "sync_dictionary_service",',
        '    "sync_global_admin_service",',
        '    "sync_options_service",',
        '    "sync_system_service",',
        '    "sync_users_service",',
        "]",
        "",
    ]
    path.write_text("\n".join(lines))


def generate_sync(src_dir: Path) -> None:
    """Transform all async source files and write them into the ``_sync/`` package.

    Args:
        src_dir: Path to the ``src/vclient`` directory.
    """
    sync_dir = src_dir / "_sync"
    sync_dir.mkdir(exist_ok=True)

    # Transform top-level modules
    for source_file in ["client.py", "registry.py"]:
        source_path = src_dir / source_file
        if source_path.exists():
            output_path = sync_dir / source_file
            output_path.write_text(transform_file(source_path))

    # Transform services
    services_src = src_dir / "services"
    services_dst = sync_dir / "services"
    services_dst.mkdir(exist_ok=True)

    for source_path in sorted(services_src.glob("*.py")):
        output_path = services_dst / source_path.name
        output_path.write_text(transform_file(source_path))

    # Write the _sync/__init__.py
    _write_sync_init(sync_dir / "__init__.py")


if __name__ == "__main__":
    project_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("src/vclient")
    generate_sync(project_root)
