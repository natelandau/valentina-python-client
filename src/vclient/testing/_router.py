"""Fake HTTP router that maps endpoint patterns to factory-generated responses."""

from __future__ import annotations

import datetime
import re
from typing import Any

import httpx

from vclient.endpoints import Endpoints
from vclient.models import (
    Asset,
    Campaign,
    CampaignBook,
    CampaignChapter,
    Character,
    CharacterConcept,
    CharacterTrait,
    CharacterTraitValueOptionsResponse,
    Company,
    CompanyPermissions,
    Developer,
    DeveloperWithApiKey,
    Diceroll,
    DictionaryTerm,
    EdgeAndPerks,
    HunterEdge,
    HunterEdgePerk,
    InventoryItem,
    MeDeveloper,
    MeDeveloperWithApiKey,
    NewCompanyResponse,
    Note,
    Perk,
    Quickroll,
    RollStatistics,
    SheetSection,
    SystemHealth,
    Trait,
    TraitCategory,
    User,
    VampireClan,
    WerewolfAuspice,
    WerewolfGift,
    WerewolfRite,
    WerewolfTribe,
)
from vclient.models.character_autogen import ChargenSessionResponse
from vclient.models.users import CampaignExperience
from vclient.testing._factories import (
    AssetFactory,
    CampaignBookFactory,
    CampaignChapterFactory,
    CampaignExperienceFactory,
    CampaignFactory,
    CharacterConceptFactory,
    CharacterFactory,
    CharacterTraitFactory,
    CharacterTraitValueOptionsResponseFactory,
    ChargenSessionResponseFactory,
    CompanyFactory,
    CompanyPermissionsFactory,
    DeveloperFactory,
    DeveloperWithApiKeyFactory,
    DicerollFactory,
    DictionaryTermFactory,
    EdgeAndPerksFactory,
    HunterEdgeFactory,
    HunterEdgePerkFactory,
    InventoryItemFactory,
    MeDeveloperFactory,
    MeDeveloperWithApiKeyFactory,
    NewCompanyResponseFactory,
    NoteFactory,
    PerkFactory,
    QuickrollFactory,
    RollStatisticsFactory,
    SheetSectionFactory,
    SystemHealthFactory,
    TraitCategoryFactory,
    TraitFactory,
    UserFactory,
    VampireClanFactory,
    WerewolfAuspiceFactory,
    WerewolfGiftFactory,
    WerewolfRiteFactory,
    WerewolfTribeFactory,
)

# Response style constants
PAGINATED = "paginated"
SINGLE = "single"
NO_CONTENT = "no_content"
RAW_JSON = "raw_json"

_FACTORY_MAP: dict[type, type] = {
    Asset: AssetFactory,
    Campaign: CampaignFactory,
    CampaignBook: CampaignBookFactory,
    CampaignChapter: CampaignChapterFactory,
    CampaignExperience: CampaignExperienceFactory,
    Character: CharacterFactory,
    CharacterConcept: CharacterConceptFactory,
    CharacterTrait: CharacterTraitFactory,
    CharacterTraitValueOptionsResponse: CharacterTraitValueOptionsResponseFactory,
    ChargenSessionResponse: ChargenSessionResponseFactory,
    Company: CompanyFactory,
    CompanyPermissions: CompanyPermissionsFactory,
    Developer: DeveloperFactory,
    DeveloperWithApiKey: DeveloperWithApiKeyFactory,
    Diceroll: DicerollFactory,
    DictionaryTerm: DictionaryTermFactory,
    EdgeAndPerks: EdgeAndPerksFactory,
    HunterEdge: HunterEdgeFactory,
    HunterEdgePerk: HunterEdgePerkFactory,
    InventoryItem: InventoryItemFactory,
    MeDeveloper: MeDeveloperFactory,
    MeDeveloperWithApiKey: MeDeveloperWithApiKeyFactory,
    NewCompanyResponse: NewCompanyResponseFactory,
    Note: NoteFactory,
    Perk: PerkFactory,
    Quickroll: QuickrollFactory,
    RollStatistics: RollStatisticsFactory,
    SheetSection: SheetSectionFactory,
    SystemHealth: SystemHealthFactory,
    Trait: TraitFactory,
    TraitCategory: TraitCategoryFactory,
    User: UserFactory,
    VampireClan: VampireClanFactory,
    WerewolfAuspice: WerewolfAuspiceFactory,
    WerewolfGift: WerewolfGiftFactory,
    WerewolfRite: WerewolfRiteFactory,
    WerewolfTribe: WerewolfTribeFactory,
}

_ROUTE_DEFAULTS: list[tuple[str, str, type | None, str]] = [
    ("GET", Endpoints.HEALTH, SystemHealth, SINGLE),
    ("GET", Endpoints.ADMIN_DEVELOPERS, Developer, PAGINATED),
    ("GET", Endpoints.ADMIN_DEVELOPER, Developer, SINGLE),
    ("POST", Endpoints.ADMIN_DEVELOPERS, Developer, SINGLE),
    ("PATCH", Endpoints.ADMIN_DEVELOPER, Developer, SINGLE),
    ("DELETE", Endpoints.ADMIN_DEVELOPER, None, NO_CONTENT),
    ("POST", Endpoints.ADMIN_DEVELOPER_NEW_KEY, DeveloperWithApiKey, SINGLE),
    ("GET", Endpoints.DEVELOPER_ME, MeDeveloper, SINGLE),
    ("PATCH", Endpoints.DEVELOPER_ME, MeDeveloper, SINGLE),
    ("POST", Endpoints.DEVELOPER_ME_NEW_KEY, MeDeveloperWithApiKey, SINGLE),
    ("GET", Endpoints.COMPANIES, Company, PAGINATED),
    ("GET", Endpoints.COMPANY, Company, SINGLE),
    ("POST", Endpoints.COMPANIES, NewCompanyResponse, SINGLE),
    ("PATCH", Endpoints.COMPANY, Company, SINGLE),
    ("DELETE", Endpoints.COMPANY, None, NO_CONTENT),
    ("POST", Endpoints.COMPANY_ACCESS, CompanyPermissions, SINGLE),
    ("GET", Endpoints.COMPANY_STATISTICS, RollStatistics, SINGLE),
    ("GET", Endpoints.USERS, User, PAGINATED),
    ("GET", Endpoints.USER, User, SINGLE),
    ("POST", Endpoints.USERS, User, SINGLE),
    ("PATCH", Endpoints.USER, User, SINGLE),
    ("DELETE", Endpoints.USER, None, NO_CONTENT),
    ("GET", Endpoints.USER_STATISTICS, RollStatistics, SINGLE),
    ("GET", Endpoints.USER_ASSETS, Asset, PAGINATED),
    ("GET", Endpoints.USER_ASSET, Asset, SINGLE),
    ("DELETE", Endpoints.USER_ASSET, None, NO_CONTENT),
    ("POST", Endpoints.USER_ASSET_UPLOAD, Asset, SINGLE),
    ("GET", Endpoints.USER_EXPERIENCE_CAMPAIGN, CampaignExperience, SINGLE),
    ("POST", Endpoints.USER_EXPERIENCE_XP_ADD, CampaignExperience, SINGLE),
    ("POST", Endpoints.USER_EXPERIENCE_XP_REMOVE, CampaignExperience, SINGLE),
    ("POST", Endpoints.USER_EXPERIENCE_CP_ADD, CampaignExperience, SINGLE),
    ("GET", Endpoints.USER_NOTES, Note, PAGINATED),
    ("GET", Endpoints.USER_NOTE, Note, SINGLE),
    ("POST", Endpoints.USER_NOTES, Note, SINGLE),
    ("PATCH", Endpoints.USER_NOTE, Note, SINGLE),
    ("DELETE", Endpoints.USER_NOTE, None, NO_CONTENT),
    ("GET", Endpoints.USER_QUICKROLLS, Quickroll, PAGINATED),
    ("GET", Endpoints.USER_QUICKROLL, Quickroll, SINGLE),
    ("POST", Endpoints.USER_QUICKROLLS, Quickroll, SINGLE),
    ("PATCH", Endpoints.USER_QUICKROLL, Quickroll, SINGLE),
    ("DELETE", Endpoints.USER_QUICKROLL, None, NO_CONTENT),
    ("GET", Endpoints.CAMPAIGNS, Campaign, PAGINATED),
    ("GET", Endpoints.CAMPAIGN, Campaign, SINGLE),
    ("POST", Endpoints.CAMPAIGNS, Campaign, SINGLE),
    ("PATCH", Endpoints.CAMPAIGN, Campaign, SINGLE),
    ("DELETE", Endpoints.CAMPAIGN, None, NO_CONTENT),
    ("GET", Endpoints.CAMPAIGN_STATISTICS, RollStatistics, SINGLE),
    ("GET", Endpoints.CAMPAIGN_ASSETS, Asset, PAGINATED),
    ("GET", Endpoints.CAMPAIGN_ASSET, Asset, SINGLE),
    ("DELETE", Endpoints.CAMPAIGN_ASSET, None, NO_CONTENT),
    ("POST", Endpoints.CAMPAIGN_ASSET_UPLOAD, Asset, SINGLE),
    ("GET", Endpoints.CAMPAIGN_NOTES, Note, PAGINATED),
    ("GET", Endpoints.CAMPAIGN_NOTE, Note, SINGLE),
    ("POST", Endpoints.CAMPAIGN_NOTES, Note, SINGLE),
    ("PATCH", Endpoints.CAMPAIGN_NOTE, Note, SINGLE),
    ("DELETE", Endpoints.CAMPAIGN_NOTE, None, NO_CONTENT),
    ("GET", Endpoints.CAMPAIGN_BOOKS, CampaignBook, PAGINATED),
    ("GET", Endpoints.CAMPAIGN_BOOK, CampaignBook, SINGLE),
    ("POST", Endpoints.CAMPAIGN_BOOKS, CampaignBook, SINGLE),
    ("PATCH", Endpoints.CAMPAIGN_BOOK, CampaignBook, SINGLE),
    ("DELETE", Endpoints.CAMPAIGN_BOOK, None, NO_CONTENT),
    ("PUT", Endpoints.CAMPAIGN_BOOK_NUMBER, CampaignBook, SINGLE),
    ("GET", Endpoints.BOOK_NOTES, Note, PAGINATED),
    ("GET", Endpoints.BOOK_NOTE, Note, SINGLE),
    ("POST", Endpoints.BOOK_NOTES, Note, SINGLE),
    ("PATCH", Endpoints.BOOK_NOTE, Note, SINGLE),
    ("DELETE", Endpoints.BOOK_NOTE, None, NO_CONTENT),
    ("GET", Endpoints.BOOK_ASSETS, Asset, PAGINATED),
    ("GET", Endpoints.BOOK_ASSET, Asset, SINGLE),
    ("DELETE", Endpoints.BOOK_ASSET, None, NO_CONTENT),
    ("POST", Endpoints.BOOK_ASSET_UPLOAD, Asset, SINGLE),
    ("GET", Endpoints.BOOK_CHAPTERS, CampaignChapter, PAGINATED),
    ("GET", Endpoints.BOOK_CHAPTER, CampaignChapter, SINGLE),
    ("POST", Endpoints.BOOK_CHAPTERS, CampaignChapter, SINGLE),
    ("PATCH", Endpoints.BOOK_CHAPTER, CampaignChapter, SINGLE),
    ("DELETE", Endpoints.BOOK_CHAPTER, None, NO_CONTENT),
    ("PUT", Endpoints.BOOK_CHAPTER_NUMBER, CampaignChapter, SINGLE),
    ("GET", Endpoints.BOOK_CHAPTER_NOTES, Note, PAGINATED),
    ("GET", Endpoints.BOOK_CHAPTER_NOTE, Note, SINGLE),
    ("POST", Endpoints.BOOK_CHAPTER_NOTES, Note, SINGLE),
    ("PATCH", Endpoints.BOOK_CHAPTER_NOTE, Note, SINGLE),
    ("DELETE", Endpoints.BOOK_CHAPTER_NOTE, None, NO_CONTENT),
    ("GET", Endpoints.BOOK_CHAPTER_ASSETS, Asset, PAGINATED),
    ("GET", Endpoints.BOOK_CHAPTER_ASSET, Asset, SINGLE),
    ("DELETE", Endpoints.BOOK_CHAPTER_ASSET, None, NO_CONTENT),
    ("POST", Endpoints.BOOK_CHAPTER_ASSET_UPLOAD, Asset, SINGLE),
    ("GET", Endpoints.CHARACTERS, Character, PAGINATED),
    ("GET", Endpoints.CHARACTER, Character, SINGLE),
    ("POST", Endpoints.CHARACTERS, Character, SINGLE),
    ("PATCH", Endpoints.CHARACTER, Character, SINGLE),
    ("DELETE", Endpoints.CHARACTER, None, NO_CONTENT),
    ("GET", Endpoints.CHARACTER_STATISTICS, RollStatistics, SINGLE),
    ("GET", Endpoints.CHARACTER_ASSETS, Asset, PAGINATED),
    ("GET", Endpoints.CHARACTER_ASSET, Asset, SINGLE),
    ("DELETE", Endpoints.CHARACTER_ASSET, None, NO_CONTENT),
    ("POST", Endpoints.CHARACTER_ASSET_UPLOAD, Asset, SINGLE),
    ("GET", Endpoints.CHARACTER_NOTES, Note, PAGINATED),
    ("GET", Endpoints.CHARACTER_NOTE, Note, SINGLE),
    ("POST", Endpoints.CHARACTER_NOTES, Note, SINGLE),
    ("PATCH", Endpoints.CHARACTER_NOTE, Note, SINGLE),
    ("DELETE", Endpoints.CHARACTER_NOTE, None, NO_CONTENT),
    ("GET", Endpoints.CHARACTER_INVENTORY, InventoryItem, PAGINATED),
    ("GET", Endpoints.CHARACTER_INVENTORY_ITEM, InventoryItem, SINGLE),
    ("POST", Endpoints.CHARACTER_INVENTORY, InventoryItem, SINGLE),
    ("PATCH", Endpoints.CHARACTER_INVENTORY_ITEM, InventoryItem, SINGLE),
    ("DELETE", Endpoints.CHARACTER_INVENTORY_ITEM, None, NO_CONTENT),
    ("GET", Endpoints.CHARACTER_WEREWOLF_GIFTS, WerewolfGift, PAGINATED),
    ("GET", Endpoints.CHARACTER_WEREWOLF_GIFT_DETAIL, WerewolfGift, SINGLE),
    ("POST", Endpoints.CHARACTER_WEREWOLF_GIFTS, WerewolfGift, SINGLE),
    ("DELETE", Endpoints.CHARACTER_WEREWOLF_GIFT_DETAIL, None, NO_CONTENT),
    ("GET", Endpoints.CHARACTER_WEREWOLF_RITES, WerewolfRite, PAGINATED),
    ("GET", Endpoints.CHARACTER_WEREWOLF_RITE_DETAIL, WerewolfRite, SINGLE),
    ("POST", Endpoints.CHARACTER_WEREWOLF_RITES, WerewolfRite, SINGLE),
    ("DELETE", Endpoints.CHARACTER_WEREWOLF_RITE_DETAIL, None, NO_CONTENT),
    ("GET", Endpoints.CHARACTER_HUNTER_EDGES, EdgeAndPerks, PAGINATED),
    ("GET", Endpoints.CHARACTER_HUNTER_EDGE_DETAIL, EdgeAndPerks, SINGLE),
    ("POST", Endpoints.CHARACTER_HUNTER_EDGES, EdgeAndPerks, SINGLE),
    ("DELETE", Endpoints.CHARACTER_HUNTER_EDGE_DETAIL, None, NO_CONTENT),
    ("GET", Endpoints.CHARACTER_HUNTER_EDGE_PERKS, Perk, PAGINATED),
    ("GET", Endpoints.CHARACTER_HUNTER_EDGE_PERK_DETAIL, Perk, SINGLE),
    ("POST", Endpoints.CHARACTER_HUNTER_EDGE_PERKS, Perk, SINGLE),
    ("DELETE", Endpoints.CHARACTER_HUNTER_EDGE_PERK_DETAIL, None, NO_CONTENT),
    ("POST", Endpoints.AUTOGENERATE, Character, SINGLE),
    ("POST", Endpoints.CHARGEN_START, ChargenSessionResponse, SINGLE),
    ("POST", Endpoints.CHARGEN_FINALIZE, Character, SINGLE),
    ("GET", Endpoints.CHARACTER_TRAITS, CharacterTrait, PAGINATED),
    ("GET", Endpoints.CHARACTER_TRAIT, CharacterTrait, SINGLE),
    ("DELETE", Endpoints.CHARACTER_TRAIT, None, NO_CONTENT),
    ("POST", Endpoints.CHARACTER_TRAIT_ASSIGN, CharacterTrait, SINGLE),
    ("POST", Endpoints.CHARACTER_TRAIT_CREATE, CharacterTrait, SINGLE),
    ("GET", Endpoints.CHARACTER_TRAIT_VALUE_OPTIONS, CharacterTraitValueOptionsResponse, SINGLE),
    ("PUT", Endpoints.CHARACTER_TRAIT_VALUE, CharacterTrait, SINGLE),
    ("GET", Endpoints.BLUEPRINT_SECTIONS, SheetSection, PAGINATED),
    ("GET", Endpoints.BLUEPRINT_SECTION_DETAIL, SheetSection, SINGLE),
    ("GET", Endpoints.BLUEPRINT_CATEGORIES, TraitCategory, PAGINATED),
    ("GET", Endpoints.BLUEPRINT_CATEGORY_DETAIL, TraitCategory, SINGLE),
    ("GET", Endpoints.BLUEPRINT_CATEGORY_TRAITS, Trait, PAGINATED),
    ("GET", Endpoints.BLUEPRINT_TRAITS, Trait, PAGINATED),
    ("GET", Endpoints.BLUEPRINT_TRAIT_DETAIL, Trait, SINGLE),
    ("GET", Endpoints.CONCEPTS, CharacterConcept, PAGINATED),
    ("GET", Endpoints.CONCEPT_DETAIL, CharacterConcept, SINGLE),
    ("GET", Endpoints.VAMPIRE_CLANS, VampireClan, PAGINATED),
    ("GET", Endpoints.VAMPIRE_CLAN_DETAIL, VampireClan, SINGLE),
    ("GET", Endpoints.WEREWOLF_TRIBES, WerewolfTribe, PAGINATED),
    ("GET", Endpoints.WEREWOLF_TRIBE_DETAIL, WerewolfTribe, SINGLE),
    ("GET", Endpoints.WEREWOLF_AUSPICES, WerewolfAuspice, PAGINATED),
    ("GET", Endpoints.WEREWOLF_AUSPICE_DETAIL, WerewolfAuspice, SINGLE),
    ("GET", Endpoints.WEREWOLF_GIFTS, WerewolfGift, PAGINATED),
    ("GET", Endpoints.WEREWOLF_GIFT_DETAIL, WerewolfGift, SINGLE),
    ("GET", Endpoints.WEREWOLF_RITES, WerewolfRite, PAGINATED),
    ("GET", Endpoints.WEREWOLF_RITE_DETAIL, WerewolfRite, SINGLE),
    ("GET", Endpoints.HUNTER_EDGES, HunterEdge, PAGINATED),
    ("GET", Endpoints.HUNTER_EDGE_DETAIL, HunterEdge, SINGLE),
    ("GET", Endpoints.HUNTER_EDGE_PERKS, HunterEdgePerk, PAGINATED),
    ("GET", Endpoints.HUNTER_EDGE_PERK_DETAIL, HunterEdgePerk, SINGLE),
    ("GET", Endpoints.DICTIONARY_TERMS, DictionaryTerm, PAGINATED),
    ("GET", Endpoints.DICTIONARY_TERM, DictionaryTerm, SINGLE),
    ("POST", Endpoints.DICTIONARY_TERMS, DictionaryTerm, SINGLE),
    ("PUT", Endpoints.DICTIONARY_TERM, DictionaryTerm, SINGLE),
    ("DELETE", Endpoints.DICTIONARY_TERM, None, NO_CONTENT),
    ("GET", Endpoints.DICEROLLS, Diceroll, PAGINATED),
    ("GET", Endpoints.DICEROLL, Diceroll, SINGLE),
    ("POST", Endpoints.DICEROLLS, Diceroll, SINGLE),
    ("POST", Endpoints.DICEROLL_QUICKROLL, Diceroll, SINGLE),
    ("GET", Endpoints.OPTIONS, None, RAW_JSON),
]


def _endpoint_to_regex(pattern: str) -> re.Pattern[str]:
    """Convert an Endpoints pattern like '/api/v1/companies/{company_id}' to a regex."""
    regex = re.sub(r"\{[^}]+\}", r"[^/]+", pattern)
    return re.compile(f"^{regex}$")


class _Route:
    """A single route entry with pattern matching and response generation."""

    def __init__(
        self,
        method: str,
        pattern: str,
        model_class: type | None,
        style: str,
        *,
        override_json: dict[str, Any] | None = None,
        override_status: int | None = None,
    ) -> None:
        self.method = method.upper()
        self.pattern = pattern
        self.regex = _endpoint_to_regex(pattern)
        self.model_class = model_class
        self.style = style
        self.override_json = override_json
        self.override_status = override_status

    def matches(self, method: str, path: str) -> bool:
        """Check if the given HTTP method and URL path match this route."""
        return self.method == method.upper() and self.regex.match(path) is not None

    def respond(self) -> httpx.Response:
        """Generate an httpx.Response for this route."""
        if self.override_json is not None:
            return httpx.Response(
                status_code=self.override_status or 200,
                json=self.override_json,
            )

        if self.style == NO_CONTENT:
            return httpx.Response(status_code=204)

        if self.style == RAW_JSON:
            return httpx.Response(status_code=200, json={})

        factory = _FACTORY_MAP[self.model_class]  # type: ignore[index]
        instance = factory.build()  # type: ignore[unresolved-attribute]
        instance_data = instance.model_dump(mode="json")

        if self.style == PAGINATED:
            body = {
                "items": [instance_data],
                "total": 1,
                "limit": 10,
                "offset": 0,
            }
            return httpx.Response(status_code=200, json=body)

        return httpx.Response(status_code=200, json=instance_data)


class _FakeRouter:
    """Route HTTP requests to factory-generated responses.

    Provide default responses for all Valentina API endpoints using model factories,
    while allowing user overrides for specific routes.
    """

    def __init__(self) -> None:
        self._overrides: list[_Route] = []
        self._defaults: list[_Route] = []
        self._register_defaults()

    def _register_defaults(self) -> None:
        """Populate default routes from _ROUTE_DEFAULTS, sorted longest-pattern-first."""
        sorted_defaults = sorted(_ROUTE_DEFAULTS, key=lambda t: len(t[1]), reverse=True)
        for method, pattern, model_class, style in sorted_defaults:
            self._defaults.append(_Route(method, pattern, model_class, style))

    def add_route(
        self,
        method: str,
        pattern: str,
        *,
        json: dict[str, Any],
        status_code: int = 200,
    ) -> None:
        """Register a user-defined override that takes precedence over defaults.

        Args:
            method: HTTP method (GET, POST, etc.).
            pattern: Endpoint pattern string from Endpoints class.
            json: Response body to return.
            status_code: HTTP status code to return.
        """
        self._overrides.append(
            _Route(
                method,
                pattern,
                model_class=None,
                style=SINGLE,
                override_json=json,
                override_status=status_code,
            )
        )

    def handle(self, request: httpx.Request) -> httpx.Response:
        """Match a request against registered routes and return a response.

        Overrides are checked first, then defaults. Returns a 404 response if no
        route matches.

        Args:
            request: The incoming httpx.Request to match.

        Returns:
            An httpx.Response from the matched route, or a 404 if unmatched.
        """
        method = request.method
        path = request.url.raw_path.decode("ascii").split("?")[0]

        for route in self._overrides:
            if route.matches(method, path):
                return self._with_elapsed(route.respond())

        for route in self._defaults:
            if route.matches(method, path):
                return self._with_elapsed(route.respond())

        return self._with_elapsed(
            httpx.Response(
                status_code=404,
                json={"detail": f"No route matched: {method} {path}"},
            )
        )

    @staticmethod
    def _with_elapsed(response: httpx.Response) -> httpx.Response:
        """Set the elapsed time on a response so BaseService._request can log it."""
        response.elapsed = datetime.timedelta(milliseconds=1)
        return response
