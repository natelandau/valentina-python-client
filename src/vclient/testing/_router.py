"""Fake HTTP router that maps endpoint patterns to factory-generated responses."""

from __future__ import annotations

import datetime
import re
from typing import Any

import httpx

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
from vclient.testing._routes import NO_CONTENT, PAGINATED, RAW_JSON, Routes, RouteSpec

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


def _endpoint_to_regex(pattern: str) -> re.Pattern[str]:
    """Convert an Endpoints pattern like '/api/v1/companies/{company_id}' to a regex.

    Path parameters become named capture groups so their values can be extracted
    for per-parameter response matching.
    """
    regex = re.sub(r"\{([^}]+)\}", r"(?P<\1>[^/]+)", pattern)
    return re.compile(f"^{regex}$")


def _collect_route_specs() -> list[RouteSpec]:
    """Collect all RouteSpec values from the Routes class."""
    return [
        getattr(Routes, name)
        for name in dir(Routes)
        if isinstance(getattr(Routes, name), RouteSpec)
    ]


class _Route:
    """A single route entry with pattern matching and response generation."""

    def __init__(  # noqa: PLR0913
        self,
        method: str,
        pattern: str,
        model_class: type | None,
        style: str,
        *,
        override_json: dict[str, Any] | None = None,
        override_status: int | None = None,
        match_params: dict[str, str] | None = None,
    ) -> None:
        self.method = method.upper()
        self.pattern = pattern
        self.regex = _endpoint_to_regex(pattern)
        self.model_class = model_class
        self.style = style
        self.override_json = override_json
        self.override_status = override_status
        self.match_params = match_params

    def matches(self, method: str, path: str) -> bool:
        """Check if the given HTTP method and URL path match this route."""
        if self.method != method.upper():
            return False

        m = self.regex.match(path)
        if m is None:
            return False

        if self.match_params is not None:
            captured = m.groupdict()
            for key, value in self.match_params.items():
                if captured.get(key) != value:
                    return False

        return True

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
        """Populate default routes from Routes class, sorted longest-pattern-first."""
        specs = _collect_route_specs()
        specs.sort(key=lambda s: len(s.pattern), reverse=True)
        for spec in specs:
            self._defaults.append(_Route(spec.method, spec.pattern, spec.model_class, spec.style))

    def add_route(
        self,
        method: str,
        pattern: str,
        *,
        json: dict[str, Any],
        status_code: int = 200,
        params: dict[str, str] | None = None,
    ) -> None:
        """Register a user-defined override that takes precedence over defaults.

        Args:
            method: HTTP method (GET, POST, etc.).
            pattern: Endpoint pattern string from Endpoints class.
            json: Response body to return.
            status_code: HTTP status code to return.
            params: Optional path parameter values to match against. When set,
                this override only matches requests whose path segments match
                all specified parameter values.
        """
        self._overrides.append(
            _Route(
                method,
                pattern,
                model_class=None,
                style="single",
                override_json=json,
                override_status=status_code,
                match_params=params,
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

        # Parameterized overrides first so specific matches beat generic ones
        for route in self._overrides:
            if route.match_params and route.matches(method, path):
                return self._with_elapsed(route.respond())

        for route in self._overrides:
            if not route.match_params and route.matches(method, path):
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
