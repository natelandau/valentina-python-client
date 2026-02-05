"""Service for interacting with the Dice Rolls API."""

from collections.abc import AsyncIterator
from typing import TYPE_CHECKING

from vclient.constants import DEFAULT_PAGE_LIMIT
from vclient.endpoints import Endpoints
from vclient.models import (
    Diceroll,
    DicerollCreate,
    PaginatedResponse,
    _DicerollQuickrollCreate,
)
from vclient.services.base import BaseService

if TYPE_CHECKING:
    from vclient.client import VClient


class DicerollService(BaseService):
    """Service for interacting with the Dice Rolls API."""

    def __init__(self, client: "VClient", company_id: str, user_id: str) -> None:
        """Initialize the service.

        Args:
            client: The VClient instance to use for requests.
            company_id: The ID of the company to operate within.
            user_id: The ID of the user to operate as.
        """
        super().__init__(client)
        self._company_id = company_id
        self._user_id = user_id

    def _format_endpoint(self, endpoint: str, **kwargs: str) -> str:
        """Format an endpoint with the scoped company_id and user_id plus any extra params."""
        return endpoint.format(company_id=self._company_id, user_id=self._user_id, **kwargs)

    # -------------------------------------------------------------------------
    # Diceroll CRUD Methods
    # -------------------------------------------------------------------------

    async def get_page(
        self,
        *,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
        userid: str | None = None,
        characterid: str | None = None,
        campaignid: str | None = None,
    ) -> PaginatedResponse[Diceroll]:
        """Retrieve a paginated page of dice rolls."""
        params = {}
        if userid is not None:
            params["userid"] = userid
        if characterid is not None:
            params["characterid"] = characterid
        if campaignid is not None:
            params["campaignid"] = campaignid

        return await self._get_paginated_as(
            self._format_endpoint(Endpoints.DICEROLLS),
            Diceroll,
            limit=limit,
            offset=offset,
            params=params or None,
        )

    async def list_all(
        self,
        *,
        userid: str | None = None,
        characterid: str | None = None,
        campaignid: str | None = None,
    ) -> list[Diceroll]:
        """Retrieve all dice rolls."""
        return [
            diceroll
            async for diceroll in self.iter_all(
                userid=userid, characterid=characterid, campaignid=campaignid
            )
        ]

    async def iter_all(
        self,
        *,
        userid: str | None = None,
        characterid: str | None = None,
        campaignid: str | None = None,
        limit: int = 100,
    ) -> AsyncIterator[Diceroll]:
        """Iterate through all dice rolls."""
        params = {}
        if userid is not None:
            params["userid"] = userid
        if characterid is not None:
            params["characterid"] = characterid
        if campaignid is not None:
            params["campaignid"] = campaignid
        async for item in self._iter_all_pages(
            self._format_endpoint(Endpoints.DICEROLLS),
            limit=limit,
            params=params or None,
        ):
            yield Diceroll.model_validate(item)

    async def get(self, diceroll_id: str) -> Diceroll:
        """Retrieve a specific dice roll."""
        response = await self._get(
            self._format_endpoint(Endpoints.DICEROLL, diceroll_id=diceroll_id)
        )
        return Diceroll.model_validate(response.json())

    async def create(
        self,
        request: DicerollCreate | None = None,
        /,
        **kwargs,
    ) -> Diceroll:
        """Create a new dice roll.

        Args:
            request: A DicerollCreate model, OR pass fields as keyword arguments.
            **kwargs: Fields for DicerollCreate if request is not provided.
                Accepts: dice_size (DiceSize, required), num_dice (int, required),
                difficulty (int | None), num_desperation_dice (int, default 0),
                comment (str | None), trait_ids (list[str]),
                character_id (str | None), campaign_id (str | None).
        """
        body = request if request is not None else DicerollCreate(**kwargs)
        response = await self._post(
            self._format_endpoint(Endpoints.DICEROLLS),
            json=body.model_dump(exclude_none=True, exclude_unset=True, mode="json"),
        )
        return Diceroll.model_validate(response.json())

    async def create_quickroll(
        self,
        *,
        quickroll_id: str,
        character_id: str,
        comment: str | None = None,
        difficulty: int = 6,
        num_desperation_dice: int = 0,
    ) -> Diceroll:
        """Create a new dice roll using a quickroll template."""
        response = await self._post(
            self._format_endpoint(Endpoints.DICEROLL_QUICKROLL),
            json=_DicerollQuickrollCreate(
                quickroll_id=quickroll_id,
                character_id=character_id,
                comment=comment,
                difficulty=difficulty,
                num_desperation_dice=num_desperation_dice,
            ).model_dump(exclude_none=True, exclude_unset=True, mode="json"),
        )
        return Diceroll.model_validate(response.json())
