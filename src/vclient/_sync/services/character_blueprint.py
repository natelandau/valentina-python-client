# AUTO-GENERATED — do not edit. Run 'uv run duty generate_sync' to regenerate.
"""Service for interacting with the Character Blueprint API."""

from collections.abc import Iterator
from typing import TYPE_CHECKING

from vclient._sync.services.base import SyncBaseService
from vclient.constants import DEFAULT_PAGE_LIMIT, BlueprintTraitOrderBy, CharacterClass, GameVersion
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

if TYPE_CHECKING:
    from vclient._sync.client import SyncVClient


class SyncCharacterBlueprintService(SyncBaseService):
    """Service for interacting with the Character Blueprint API."""

    def __init__(self, client: "SyncVClient", company_id: str) -> None:
        """Initialize the service.

        Args:
            client: The SyncVClient instance to use for requests.
            company_id: The ID of the company to operate within.

        """
        super().__init__(client)
        self._company_id = company_id

    def _format_endpoint(self, endpoint: str, **kwargs: str) -> str:
        """Format an endpoint with the scoped company_id, user_id, and campaign_id plus any extra params."""
        return endpoint.format(company_id=self._company_id, **kwargs)

    def get_sections_page(
        self,
        game_version: GameVersion,
        *,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
        character_class: CharacterClass | None = None,
    ) -> PaginatedResponse[SheetSection]:
        """Get a paginated page of character blueprint sections."""
        return self._get_paginated_as(
            self._format_endpoint(Endpoints.BLUEPRINT_SECTIONS, game_version=game_version),
            SheetSection,
            limit=limit,
            offset=offset,
            params=self._build_params(character_class=character_class),
        )

    def list_all_sections(
        self, *, game_version: GameVersion, character_class: CharacterClass | None = None
    ) -> list[SheetSection]:
        """List all character blueprint sections."""
        return [
            section
            for section in self.iter_all_sections(
                game_version=game_version, character_class=character_class
            )
        ]

    def iter_all_sections(
        self, *, game_version: GameVersion, character_class: CharacterClass | None = None
    ) -> Iterator[SheetSection]:
        """Iterate through all character blueprint sections."""
        for section in self._iter_all_pages(
            self._format_endpoint(Endpoints.BLUEPRINT_SECTIONS, game_version=game_version),
            params=self._build_params(character_class=character_class),
        ):
            yield SheetSection.model_validate(section)

    def get_section(self, *, game_version: GameVersion, section_id: str) -> SheetSection:
        """Get a character blueprint section by ID."""
        response = self._get(
            self._format_endpoint(
                Endpoints.BLUEPRINT_SECTION_DETAIL, game_version=game_version, section_id=section_id
            )
        )
        return SheetSection.model_validate(response.json())

    def get_categories_page(
        self,
        *,
        game_version: GameVersion,
        section_id: str,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
        character_class: CharacterClass | None = None,
    ) -> PaginatedResponse[TraitCategory]:
        """Get a paginated page of character blueprint categories."""
        return self._get_paginated_as(
            self._format_endpoint(
                Endpoints.BLUEPRINT_CATEGORIES, game_version=game_version, section_id=section_id
            ),
            TraitCategory,
            limit=limit,
            offset=offset,
            params=self._build_params(character_class=character_class),
        )

    def list_all_categories(
        self,
        *,
        game_version: GameVersion,
        section_id: str,
        character_class: CharacterClass | None = None,
    ) -> list[TraitCategory]:
        """List all character blueprint categories."""
        return [
            category
            for category in self.iter_all_categories(
                game_version=game_version, section_id=section_id, character_class=character_class
            )
        ]

    def iter_all_categories(
        self,
        *,
        game_version: GameVersion,
        section_id: str,
        character_class: CharacterClass | None = None,
    ) -> Iterator[TraitCategory]:
        """Iterate through all character blueprint categories."""
        for category in self._iter_all_pages(
            self._format_endpoint(
                Endpoints.BLUEPRINT_CATEGORIES, game_version=game_version, section_id=section_id
            ),
            params=self._build_params(character_class=character_class),
        ):
            yield TraitCategory.model_validate(category)

    def get_category(
        self, *, game_version: GameVersion, section_id: str, category_id: str
    ) -> TraitCategory:
        """Get a character blueprint category by ID."""
        response = self._get(
            self._format_endpoint(
                Endpoints.BLUEPRINT_CATEGORY_DETAIL,
                game_version=game_version,
                section_id=section_id,
                category_id=category_id,
            )
        )
        return TraitCategory.model_validate(response.json())

    def get_subcategories_page(
        self,
        *,
        game_version: GameVersion,
        section_id: str,
        category_id: str,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
        character_class: CharacterClass | None = None,
    ) -> PaginatedResponse[TraitSubcategory]:
        """Get a paginated page of character blueprint category subcategories."""
        return self._get_paginated_as(
            self._format_endpoint(Endpoints.BLUEPRINT_SUBCATEGORIES),
            TraitSubcategory,
            limit=limit,
            offset=offset,
            params=self._build_params(character_class=character_class),
        )

    def list_all_subcategories(
        self,
        *,
        game_version: GameVersion,
        section_id: str,
        category_id: str,
        character_class: CharacterClass | None = None,
    ) -> list[TraitSubcategory]:
        """List all character blueprint category subcategories."""
        return [
            subcategory
            for subcategory in self.iter_all_subcategories(
                game_version=game_version,
                section_id=section_id,
                category_id=category_id,
                character_class=character_class,
            )
        ]

    def iter_all_subcategories(
        self,
        *,
        game_version: GameVersion,
        section_id: str,
        category_id: str,
        character_class: CharacterClass | None = None,
    ) -> Iterator[TraitSubcategory]:
        """Iterate through all character blueprint category subcategories."""
        for subcategory in self._iter_all_pages(
            self._format_endpoint(Endpoints.BLUEPRINT_SUBCATEGORIES),
            params=self._build_params(character_class=character_class),
        ):
            yield TraitSubcategory.model_validate(subcategory)

    def get_subcategory(
        self, *, game_version: GameVersion, section_id: str, category_id: str, subcategory_id: str
    ) -> TraitSubcategory:
        """Get a character blueprint category subcategory by ID."""
        response = self._get(
            self._format_endpoint(
                Endpoints.BLUEPRINT_SUBCATEGORY_DETAIL, subcategory_id=subcategory_id
            )
        )
        return TraitSubcategory.model_validate(response.json())

    def get_subcategory_traits_page(
        self,
        *,
        game_version: GameVersion,
        section_id: str,
        category_id: str,
        subcategory_id: str,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
        character_class: CharacterClass | None = None,
        is_rollable: bool | None = None,
    ) -> PaginatedResponse[Trait]:
        """Get a paginated page of character blueprint subcategory traits."""
        return self._get_paginated_as(
            self._format_endpoint(Endpoints.BLUEPRINT_TRAITS),
            Trait,
            limit=limit,
            offset=offset,
            params=self._build_params(character_class=character_class, is_rollable=is_rollable),
        )

    def list_all_subcategory_traits(
        self,
        *,
        game_version: GameVersion,
        section_id: str,
        category_id: str,
        subcategory_id: str,
        character_class: CharacterClass | None = None,
        is_rollable: bool | None = None,
    ) -> list[Trait]:
        """List all character blueprint subcategory traits."""
        return [
            trait
            for trait in self.iter_all_subcategory_traits(
                game_version=game_version,
                section_id=section_id,
                category_id=category_id,
                subcategory_id=subcategory_id,
                character_class=character_class,
                is_rollable=is_rollable,
            )
        ]

    def iter_all_subcategory_traits(
        self,
        *,
        game_version: GameVersion,
        section_id: str,
        category_id: str,
        subcategory_id: str,
        character_class: CharacterClass | None = None,
        is_rollable: bool | None = None,
    ) -> Iterator[Trait]:
        """Iterate through all character blueprint subcategory traits."""
        for trait in self._iter_all_pages(
            self._format_endpoint(Endpoints.BLUEPRINT_TRAITS),
            params=self._build_params(character_class=character_class, is_rollable=is_rollable),
        ):
            yield Trait.model_validate(trait)

    def get_category_traits_page(
        self,
        *,
        game_version: GameVersion,
        section_id: str,
        category_id: str,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
        character_class: CharacterClass | None = None,
        is_rollable: bool | None = None,
        character_id: str | None = None,
        exclude_subcategory_traits: bool = False,
    ) -> PaginatedResponse[Trait]:
        """Get a paginated page of character blueprint category traits."""
        return self._get_paginated_as(
            self._format_endpoint(Endpoints.BLUEPRINT_TRAITS),
            Trait,
            limit=limit,
            offset=offset,
            params=self._build_params(
                is_rollable=is_rollable,
                character_class=character_class,
                character_id=character_id,
                exclude_subcategory_traits=exclude_subcategory_traits or None,
            ),
        )

    def list_all_category_traits(
        self,
        *,
        game_version: GameVersion,
        section_id: str,
        category_id: str,
        character_class: CharacterClass | None = None,
        is_rollable: bool | None = None,
        character_id: str | None = None,
        exclude_subcategory_traits: bool = False,
    ) -> list[Trait]:
        """List all character blueprint category traits."""
        return [
            trait
            for trait in self.iter_all_category_traits(
                game_version=game_version,
                section_id=section_id,
                category_id=category_id,
                character_class=character_class,
                is_rollable=is_rollable,
                character_id=character_id,
                exclude_subcategory_traits=exclude_subcategory_traits,
            )
        ]

    def iter_all_category_traits(
        self,
        *,
        game_version: GameVersion,
        section_id: str,
        category_id: str,
        character_class: CharacterClass | None = None,
        is_rollable: bool | None = None,
        character_id: str | None = None,
        exclude_subcategory_traits: bool = False,
    ) -> Iterator[Trait]:
        """Iterate through all character blueprint category traits."""
        for trait in self._iter_all_pages(
            self._format_endpoint(Endpoints.BLUEPRINT_TRAITS),
            params=self._build_params(
                character_class=character_class,
                is_rollable=is_rollable,
                character_id=character_id,
                exclude_subcategory_traits=exclude_subcategory_traits or None,
            ),
        ):
            yield Trait.model_validate(trait)

    def get_traits_page(
        self,
        *,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
        game_version: GameVersion | None = None,
        character_class: CharacterClass | None = None,
        parent_category_id: str | None = None,
        is_rollable: bool | None = None,
        order_by: BlueprintTraitOrderBy | None = None,
    ) -> PaginatedResponse[Trait]:
        """Get a paginated page of all character blueprint traits."""
        return self._get_paginated_as(
            self._format_endpoint(Endpoints.BLUEPRINT_TRAITS),
            Trait,
            limit=limit,
            offset=offset,
            params=self._build_params(
                character_class=character_class,
                parent_category_id=parent_category_id,
                is_rollable=is_rollable,
                order_by=order_by,
                game_version=game_version,
            ),
        )

    def list_all_traits(
        self,
        *,
        game_version: GameVersion | None = None,
        character_class: CharacterClass | None = None,
        parent_category_id: str | None = None,
        is_rollable: bool | None = None,
        order_by: BlueprintTraitOrderBy | None = None,
    ) -> list[Trait]:
        """List all character blueprint traits."""
        return [
            trait
            for trait in self.iter_all_traits(
                game_version=game_version,
                character_class=character_class,
                parent_category_id=parent_category_id,
                is_rollable=is_rollable,
                order_by=order_by,
            )
        ]

    def iter_all_traits(
        self,
        *,
        game_version: GameVersion | None = None,
        character_class: CharacterClass | None = None,
        parent_category_id: str | None = None,
        is_rollable: bool | None = None,
        order_by: BlueprintTraitOrderBy | None = None,
    ) -> Iterator[Trait]:
        """Iterate through all character blueprint traits."""
        for trait in self._iter_all_pages(
            self._format_endpoint(Endpoints.BLUEPRINT_TRAITS),
            params=self._build_params(
                character_class=character_class,
                parent_category_id=parent_category_id,
                is_rollable=is_rollable,
                order_by=order_by,
                game_version=game_version,
            ),
        ):
            yield Trait.model_validate(trait)

    def get_trait(self, *, trait_id: str) -> Trait:
        """Get a character blueprint trait by ID."""
        response = self._get(
            self._format_endpoint(Endpoints.BLUEPRINT_TRAIT_DETAIL, trait_id=trait_id)
        )
        return Trait.model_validate(response.json())

    def get_concepts_page(
        self, *, limit: int = DEFAULT_PAGE_LIMIT, offset: int = 0
    ) -> PaginatedResponse[CharacterConcept]:
        """Get a paginated page of character concepts."""
        return self._get_paginated_as(
            self._format_endpoint(Endpoints.CONCEPTS), CharacterConcept, limit=limit, offset=offset
        )

    def list_all_concepts(self) -> list[CharacterConcept]:
        """List all character concepts."""
        return [concept for concept in self.iter_all_concepts()]

    def iter_all_concepts(self) -> Iterator[CharacterConcept]:
        """Iterate through all character concepts."""
        for concept in self._iter_all_pages(self._format_endpoint(Endpoints.CONCEPTS)):
            yield CharacterConcept.model_validate(concept)

    def get_concept(self, *, concept_id: str) -> CharacterConcept:
        """Get a character concept by ID."""
        response = self._get(self._format_endpoint(Endpoints.CONCEPT_DETAIL, concept_id=concept_id))
        return CharacterConcept.model_validate(response.json())

    def get_vampire_clans_page(
        self,
        *,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
        game_version: GameVersion | None = None,
    ) -> PaginatedResponse[VampireClan]:
        """Get a paginated page of vampire clans."""
        return self._get_paginated_as(
            self._format_endpoint(Endpoints.VAMPIRE_CLANS),
            VampireClan,
            limit=limit,
            offset=offset,
            params=self._build_params(game_version=game_version),
        )

    def list_all_vampire_clans(
        self, *, game_version: GameVersion | None = None
    ) -> list[VampireClan]:
        """List all vampire clans."""
        return [clan for clan in self.iter_all_vampire_clans(game_version=game_version)]

    def iter_all_vampire_clans(
        self, *, game_version: GameVersion | None = None
    ) -> Iterator[VampireClan]:
        """Iterate through all vampire clans."""
        for clan in self._iter_all_pages(
            self._format_endpoint(Endpoints.VAMPIRE_CLANS),
            params=self._build_params(game_version=game_version),
        ):
            yield VampireClan.model_validate(clan)

    def get_vampire_clan(self, *, vampire_clan_id: str) -> VampireClan:
        """Get a vampire clan by ID."""
        response = self._get(
            self._format_endpoint(Endpoints.VAMPIRE_CLAN_DETAIL, vampire_clan_id=vampire_clan_id)
        )
        return VampireClan.model_validate(response.json())

    def get_werewolf_auspices_page(
        self,
        *,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
        game_version: GameVersion | None = None,
    ) -> PaginatedResponse[WerewolfAuspice]:
        """Get a paginated page of werewolf auspices."""
        return self._get_paginated_as(
            self._format_endpoint(Endpoints.WEREWOLF_AUSPICES),
            WerewolfAuspice,
            limit=limit,
            offset=offset,
            params=self._build_params(game_version=game_version),
        )

    def list_all_werewolf_auspices(
        self, *, game_version: GameVersion | None = None
    ) -> list[WerewolfAuspice]:
        """List all werewolf auspices."""
        return [auspice for auspice in self.iter_all_werewolf_auspices(game_version=game_version)]

    def iter_all_werewolf_auspices(
        self, *, game_version: GameVersion | None = None
    ) -> Iterator[WerewolfAuspice]:
        """Iterate through all werewolf auspices."""
        for auspice in self._iter_all_pages(
            self._format_endpoint(Endpoints.WEREWOLF_AUSPICES),
            params=self._build_params(game_version=game_version),
        ):
            yield WerewolfAuspice.model_validate(auspice)

    def get_werewolf_auspice(self, *, werewolf_auspice_id: str) -> WerewolfAuspice:
        """Get a werewolf auspice by ID."""
        response = self._get(
            self._format_endpoint(
                Endpoints.WEREWOLF_AUSPICE_DETAIL, werewolf_auspice_id=werewolf_auspice_id
            )
        )
        return WerewolfAuspice.model_validate(response.json())

    def get_werewolf_tribes_page(
        self,
        *,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
        game_version: GameVersion | None = None,
    ) -> PaginatedResponse[WerewolfTribe]:
        """Get a paginated page of werewolf tribes."""
        return self._get_paginated_as(
            self._format_endpoint(Endpoints.WEREWOLF_TRIBES),
            WerewolfTribe,
            limit=limit,
            offset=offset,
            params=self._build_params(game_version=game_version),
        )

    def list_all_werewolf_tribes(
        self, *, game_version: GameVersion | None = None
    ) -> list[WerewolfTribe]:
        """List all werewolf tribes."""
        return [tribe for tribe in self.iter_all_werewolf_tribes(game_version=game_version)]

    def iter_all_werewolf_tribes(
        self, *, game_version: GameVersion | None = None
    ) -> Iterator[WerewolfTribe]:
        """Iterate through all werewolf tribes."""
        for tribe in self._iter_all_pages(
            self._format_endpoint(Endpoints.WEREWOLF_TRIBES),
            params=self._build_params(game_version=game_version),
        ):
            yield WerewolfTribe.model_validate(tribe)

    def get_werewolf_tribe(self, *, werewolf_tribe_id: str) -> WerewolfTribe:
        """Get a werewolf tribe by ID."""
        response = self._get(
            self._format_endpoint(
                Endpoints.WEREWOLF_TRIBE_DETAIL, werewolf_tribe_id=werewolf_tribe_id
            )
        )
        return WerewolfTribe.model_validate(response.json())
