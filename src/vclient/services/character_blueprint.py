"""Service for interacting with the Character Blueprint API."""

from collections.abc import AsyncIterator
from typing import TYPE_CHECKING

from vclient.constants import (
    DEFAULT_PAGE_LIMIT,
    BlueprintTraitOrderBy,
    CharacterClass,
    GameVersion,
)
from vclient.endpoints import Endpoints
from vclient.models import (
    CharacterConcept,
    PaginatedResponse,
    SheetSection,
    Trait,
    TraitCategory,
    TraitSubcategory,
    VampireClan,
    WerewolfAuspice,
    WerewolfTribe,
)
from vclient.services.base import BaseService

if TYPE_CHECKING:
    from vclient.client import VClient


class CharacterBlueprintService(BaseService):
    """Service for interacting with the Character Blueprint API."""

    def __init__(self, client: "VClient", company_id: str) -> None:
        """Initialize the service.

        Args:
            client: The VClient instance to use for requests.
            company_id: The ID of the company to operate within.

        """
        super().__init__(client)
        self._company_id = company_id

    def _format_endpoint(self, endpoint: str, **kwargs: str) -> str:
        """Format an endpoint with the scoped company_id plus any extra params."""
        return endpoint.format(
            company_id=self._company_id,
            **kwargs,
        )

    # Character Sheet Sections

    async def get_sections_page(
        self,
        *,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
        game_version: GameVersion | None = None,
        character_class: CharacterClass | None = None,
    ) -> PaginatedResponse[SheetSection]:
        """Get a paginated page of character blueprint sections."""
        return await self._get_paginated_as(
            self._format_endpoint(Endpoints.BLUEPRINT_SECTIONS),
            SheetSection,
            limit=limit,
            offset=offset,
            params=self._build_params(game_version=game_version, character_class=character_class),
        )

    async def list_all_sections(
        self,
        *,
        game_version: GameVersion | None = None,
        character_class: CharacterClass | None = None,
    ) -> list[SheetSection]:
        """List all character blueprint sections."""
        return [
            section
            async for section in self.iter_all_sections(
                game_version=game_version, character_class=character_class
            )
        ]

    async def iter_all_sections(
        self,
        *,
        game_version: GameVersion | None = None,
        character_class: CharacterClass | None = None,
    ) -> AsyncIterator[SheetSection]:
        """Iterate through all character blueprint sections."""
        async for section in self._iter_all_pages(
            self._format_endpoint(Endpoints.BLUEPRINT_SECTIONS),
            params=self._build_params(game_version=game_version, character_class=character_class),
        ):
            yield SheetSection.model_validate(section)

    async def get_section(self, *, section_id: str) -> SheetSection:
        """Get a character blueprint section by ID."""
        response = await self._get(
            self._format_endpoint(
                Endpoints.BLUEPRINT_SECTION_DETAIL,
                section_id=section_id,
            ),
        )
        return SheetSection.model_validate(response.json())

    # Character Sheet Categories

    async def get_categories_page(
        self,
        *,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
        game_version: GameVersion | None = None,
        section_id: str | None = None,
        character_class: CharacterClass | None = None,
    ) -> PaginatedResponse[TraitCategory]:
        """Get a paginated page of character blueprint categories."""
        return await self._get_paginated_as(
            self._format_endpoint(Endpoints.BLUEPRINT_CATEGORIES),
            TraitCategory,
            limit=limit,
            offset=offset,
            params=self._build_params(
                game_version=game_version,
                section_id=section_id,
                character_class=character_class,
            ),
        )

    async def list_all_categories(
        self,
        *,
        game_version: GameVersion | None = None,
        section_id: str | None = None,
        character_class: CharacterClass | None = None,
    ) -> list[TraitCategory]:
        """List all character blueprint categories."""
        return [
            category
            async for category in self.iter_all_categories(
                game_version=game_version,
                section_id=section_id,
                character_class=character_class,
            )
        ]

    async def iter_all_categories(
        self,
        *,
        game_version: GameVersion | None = None,
        section_id: str | None = None,
        character_class: CharacterClass | None = None,
    ) -> AsyncIterator[TraitCategory]:
        """Iterate through all character blueprint categories."""
        async for category in self._iter_all_pages(
            self._format_endpoint(Endpoints.BLUEPRINT_CATEGORIES),
            params=self._build_params(
                game_version=game_version,
                section_id=section_id,
                character_class=character_class,
            ),
        ):
            yield TraitCategory.model_validate(category)

    async def get_category(self, *, category_id: str) -> TraitCategory:
        """Get a character blueprint category by ID."""
        response = await self._get(
            self._format_endpoint(
                Endpoints.BLUEPRINT_CATEGORY_DETAIL,
                category_id=category_id,
            ),
        )
        return TraitCategory.model_validate(response.json())

    # Character Sheet Subcategories

    async def get_subcategories_page(
        self,
        *,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
        game_version: GameVersion | None = None,
        category_id: str | None = None,
        character_class: CharacterClass | None = None,
    ) -> PaginatedResponse[TraitSubcategory]:
        """Get a paginated page of character blueprint subcategories."""
        return await self._get_paginated_as(
            self._format_endpoint(Endpoints.BLUEPRINT_SUBCATEGORIES),
            TraitSubcategory,
            limit=limit,
            offset=offset,
            params=self._build_params(
                game_version=game_version,
                category_id=category_id,
                character_class=character_class,
            ),
        )

    async def list_all_subcategories(
        self,
        *,
        game_version: GameVersion | None = None,
        category_id: str | None = None,
        character_class: CharacterClass | None = None,
    ) -> list[TraitSubcategory]:
        """List all character blueprint subcategories."""
        return [
            subcategory
            async for subcategory in self.iter_all_subcategories(
                game_version=game_version,
                category_id=category_id,
                character_class=character_class,
            )
        ]

    async def iter_all_subcategories(
        self,
        *,
        game_version: GameVersion | None = None,
        category_id: str | None = None,
        character_class: CharacterClass | None = None,
    ) -> AsyncIterator[TraitSubcategory]:
        """Iterate through all character blueprint subcategories."""
        async for subcategory in self._iter_all_pages(
            self._format_endpoint(Endpoints.BLUEPRINT_SUBCATEGORIES),
            params=self._build_params(
                game_version=game_version,
                category_id=category_id,
                character_class=character_class,
            ),
        ):
            yield TraitSubcategory.model_validate(subcategory)

    async def get_subcategory(self, *, subcategory_id: str) -> TraitSubcategory:
        """Get a character blueprint subcategory by ID."""
        response = await self._get(
            self._format_endpoint(
                Endpoints.BLUEPRINT_SUBCATEGORY_DETAIL,
                subcategory_id=subcategory_id,
            ),
        )
        return TraitSubcategory.model_validate(response.json())

    # Character Traits

    async def get_traits_page(
        self,
        *,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
        game_version: GameVersion | None = None,
        character_class: CharacterClass | None = None,
        parent_category_id: str | None = None,
        subcategory_id: str | None = None,
        is_rollable: bool | None = None,
        order_by: BlueprintTraitOrderBy | None = None,
        exclude_subcategory_traits: bool = False,
    ) -> PaginatedResponse[Trait]:
        """Get a paginated page of character blueprint traits."""
        return await self._get_paginated_as(
            self._format_endpoint(Endpoints.BLUEPRINT_TRAITS),
            Trait,
            limit=limit,
            offset=offset,
            params=self._build_params(
                character_class=character_class,
                parent_category_id=parent_category_id,
                subcategory_id=subcategory_id,
                is_rollable=is_rollable,
                order_by=order_by,
                game_version=game_version,
                exclude_subcategory_traits=exclude_subcategory_traits or None,
            ),
        )

    async def list_all_traits(
        self,
        *,
        game_version: GameVersion | None = None,
        character_class: CharacterClass | None = None,
        parent_category_id: str | None = None,
        subcategory_id: str | None = None,
        is_rollable: bool | None = None,
        order_by: BlueprintTraitOrderBy | None = None,
        exclude_subcategory_traits: bool = False,
    ) -> list[Trait]:
        """List all character blueprint traits."""
        return [
            trait
            async for trait in self.iter_all_traits(
                game_version=game_version,
                character_class=character_class,
                parent_category_id=parent_category_id,
                subcategory_id=subcategory_id,
                is_rollable=is_rollable,
                order_by=order_by,
                exclude_subcategory_traits=exclude_subcategory_traits,
            )
        ]

    async def iter_all_traits(
        self,
        *,
        game_version: GameVersion | None = None,
        character_class: CharacterClass | None = None,
        parent_category_id: str | None = None,
        subcategory_id: str | None = None,
        is_rollable: bool | None = None,
        order_by: BlueprintTraitOrderBy | None = None,
        exclude_subcategory_traits: bool = False,
    ) -> AsyncIterator[Trait]:
        """Iterate through all character blueprint traits."""
        async for trait in self._iter_all_pages(
            self._format_endpoint(Endpoints.BLUEPRINT_TRAITS),
            params=self._build_params(
                character_class=character_class,
                parent_category_id=parent_category_id,
                subcategory_id=subcategory_id,
                is_rollable=is_rollable,
                order_by=order_by,
                game_version=game_version,
                exclude_subcategory_traits=exclude_subcategory_traits or None,
            ),
        ):
            yield Trait.model_validate(trait)

    async def get_trait(self, *, trait_id: str) -> Trait:
        """Get a character blueprint trait by ID."""
        response = await self._get(
            self._format_endpoint(Endpoints.BLUEPRINT_TRAIT_DETAIL, trait_id=trait_id),
        )
        return Trait.model_validate(response.json())

    # Character Concepts

    async def get_concepts_page(
        self,
        *,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
    ) -> PaginatedResponse[CharacterConcept]:
        """Get a paginated page of character concepts."""
        return await self._get_paginated_as(
            self._format_endpoint(Endpoints.CONCEPTS),
            CharacterConcept,
            limit=limit,
            offset=offset,
        )

    async def list_all_concepts(self) -> list[CharacterConcept]:
        """List all character concepts."""
        return [concept async for concept in self.iter_all_concepts()]

    async def iter_all_concepts(self) -> AsyncIterator[CharacterConcept]:
        """Iterate through all character concepts."""
        async for concept in self._iter_all_pages(
            self._format_endpoint(Endpoints.CONCEPTS),
        ):
            yield CharacterConcept.model_validate(concept)

    async def get_concept(self, *, concept_id: str) -> CharacterConcept:
        """Get a character concept by ID."""
        response = await self._get(
            self._format_endpoint(Endpoints.CONCEPT_DETAIL, concept_id=concept_id),
        )
        return CharacterConcept.model_validate(response.json())

    # -----------------------------------------------------------------------------
    # Vampire Clans
    # -----------------------------------------------------------------------------
    async def get_vampire_clans_page(
        self,
        *,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
        game_version: GameVersion | None = None,
    ) -> PaginatedResponse[VampireClan]:
        """Get a paginated page of vampire clans."""
        return await self._get_paginated_as(
            self._format_endpoint(Endpoints.VAMPIRE_CLANS),
            VampireClan,
            limit=limit,
            offset=offset,
            params=self._build_params(game_version=game_version),
        )

    async def list_all_vampire_clans(
        self, *, game_version: GameVersion | None = None
    ) -> list[VampireClan]:
        """List all vampire clans."""
        return [clan async for clan in self.iter_all_vampire_clans(game_version=game_version)]

    async def iter_all_vampire_clans(
        self, *, game_version: GameVersion | None = None
    ) -> AsyncIterator[VampireClan]:
        """Iterate through all vampire clans."""
        async for clan in self._iter_all_pages(
            self._format_endpoint(Endpoints.VAMPIRE_CLANS),
            params=self._build_params(game_version=game_version),
        ):
            yield VampireClan.model_validate(clan)

    async def get_vampire_clan(self, *, vampire_clan_id: str) -> VampireClan:
        """Get a vampire clan by ID."""
        response = await self._get(
            self._format_endpoint(Endpoints.VAMPIRE_CLAN_DETAIL, vampire_clan_id=vampire_clan_id),
        )
        return VampireClan.model_validate(response.json())

    # -----------------------------------------------------------------------------
    # Werewolf Auspices
    # -----------------------------------------------------------------------------
    async def get_werewolf_auspices_page(
        self,
        *,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
        game_version: GameVersion | None = None,
    ) -> PaginatedResponse[WerewolfAuspice]:
        """Get a paginated page of werewolf auspices."""
        return await self._get_paginated_as(
            self._format_endpoint(Endpoints.WEREWOLF_AUSPICES),
            WerewolfAuspice,
            limit=limit,
            offset=offset,
            params=self._build_params(game_version=game_version),
        )

    async def list_all_werewolf_auspices(
        self, *, game_version: GameVersion | None = None
    ) -> list[WerewolfAuspice]:
        """List all werewolf auspices."""
        return [
            auspice async for auspice in self.iter_all_werewolf_auspices(game_version=game_version)
        ]

    async def iter_all_werewolf_auspices(
        self, *, game_version: GameVersion | None = None
    ) -> AsyncIterator[WerewolfAuspice]:
        """Iterate through all werewolf auspices."""
        async for auspice in self._iter_all_pages(
            self._format_endpoint(Endpoints.WEREWOLF_AUSPICES),
            params=self._build_params(game_version=game_version),
        ):
            yield WerewolfAuspice.model_validate(auspice)

    async def get_werewolf_auspice(self, *, werewolf_auspice_id: str) -> WerewolfAuspice:
        """Get a werewolf auspice by ID."""
        response = await self._get(
            self._format_endpoint(
                Endpoints.WEREWOLF_AUSPICE_DETAIL, werewolf_auspice_id=werewolf_auspice_id
            ),
        )
        return WerewolfAuspice.model_validate(response.json())

    # -----------------------------------------------------------------------------
    # Werewolf Tribes
    # -----------------------------------------------------------------------------
    async def get_werewolf_tribes_page(
        self,
        *,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
        game_version: GameVersion | None = None,
    ) -> PaginatedResponse[WerewolfTribe]:
        """Get a paginated page of werewolf tribes."""
        return await self._get_paginated_as(
            self._format_endpoint(Endpoints.WEREWOLF_TRIBES),
            WerewolfTribe,
            limit=limit,
            offset=offset,
            params=self._build_params(game_version=game_version),
        )

    async def list_all_werewolf_tribes(
        self, *, game_version: GameVersion | None = None
    ) -> list[WerewolfTribe]:
        """List all werewolf tribes."""
        return [tribe async for tribe in self.iter_all_werewolf_tribes(game_version=game_version)]

    async def iter_all_werewolf_tribes(
        self, *, game_version: GameVersion | None = None
    ) -> AsyncIterator[WerewolfTribe]:
        """Iterate through all werewolf tribes."""
        async for tribe in self._iter_all_pages(
            self._format_endpoint(Endpoints.WEREWOLF_TRIBES),
            params=self._build_params(game_version=game_version),
        ):
            yield WerewolfTribe.model_validate(tribe)

    async def get_werewolf_tribe(self, *, werewolf_tribe_id: str) -> WerewolfTribe:
        """Get a werewolf tribe by ID."""
        response = await self._get(
            self._format_endpoint(
                Endpoints.WEREWOLF_TRIBE_DETAIL, werewolf_tribe_id=werewolf_tribe_id
            ),
        )
        return WerewolfTribe.model_validate(response.json())
