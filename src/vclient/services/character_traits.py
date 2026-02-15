"""Service for interacting with the Character Traits API."""

from collections.abc import AsyncIterator
from typing import TYPE_CHECKING

from vclient.constants import DEFAULT_PAGE_LIMIT, TraitModifyCurrency
from vclient.endpoints import Endpoints
from vclient.models import (
    CharacterCreateTraitAssign,
    CharacterTrait,
    CharacterTraitValueOptionsResponse,
    PaginatedResponse,
    TraitCreate,
    _TraitModify,
)
from vclient.services.base import BaseService

if TYPE_CHECKING:
    from vclient.client import VClient


class CharacterTraitsService(BaseService):
    """Service for interacting with the Character Traits API."""

    def __init__(
        self, client: "VClient", company_id: str, user_id: str, campaign_id: str, character_id: str
    ) -> None:
        """Initialize the service.

        Args:
            client: The VClient instance to use for requests.
            company_id: The ID of the company to operate within.
            user_id: The ID of the user to operate as.
            campaign_id: The ID of the campaign to operate within.
            character_id: The ID of the character to operate within.
        """
        super().__init__(client)
        self._company_id = company_id
        self._user_id = user_id
        self._campaign_id = campaign_id
        self._character_id = character_id

    def _format_endpoint(self, endpoint: str, **kwargs: str) -> str:
        """Format an endpoint with the scoped company_id, user_id, campaign_id, and character_id plus any extra params."""
        return endpoint.format(
            company_id=self._company_id,
            user_id=self._user_id,
            campaign_id=self._campaign_id,
            character_id=self._character_id,
            **kwargs,
        )

    # -------------------------------------------------------------------------
    # Character Trait CRUD Methods
    # -------------------------------------------------------------------------

    async def get_page(
        self,
        *,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
        parent_category_id: str | None = None,
    ) -> PaginatedResponse[CharacterTrait]:
        """Retrieve a paginated page of character traits.

        Args:
            limit: Maximum number of items to return (0-100, default 10).
            offset: Number of items to skip from the beginning (default 0).
            parent_category_id: Filter by parent category ID.

        Returns:
            A PaginatedResponse containing CharacterTrait objects and pagination metadata.
        """
        params: dict[str, str | int] = {}
        if parent_category_id is not None:
            params["parent_category_id"] = parent_category_id

        return await self._get_paginated_as(
            self._format_endpoint(Endpoints.CHARACTER_TRAITS),
            CharacterTrait,
            limit=limit,
            offset=offset,
            params=params or None,
        )

    async def list_all(
        self,
        *,
        parent_category_id: str | None = None,
    ) -> list[CharacterTrait]:
        """Retrieve all character traits.

        Args:
            parent_category_id: Filter by parent category ID.

        Returns:
            A list of all CharacterTrait objects.
        """
        return [trait async for trait in self.iter_all(parent_category_id=parent_category_id)]

    async def iter_all(
        self,
        *,
        limit: int = 100,
        parent_category_id: str | None = None,
    ) -> AsyncIterator[CharacterTrait]:
        """Iterate through all character traits.

        Args:
            limit: Maximum number of items to return (0-100, default 10).
            parent_category_id: Filter by parent category ID.

        Yields:
            Individual CharacterTrait objects.

        Example:
            >>> async for trait in character_traits.iter_all():
            ...     print(trait.name)
        """
        params: dict[str, str | int] = {}
        if parent_category_id is not None:
            params["parent_category_id"] = parent_category_id

        async for item in self._iter_all_pages(
            self._format_endpoint(Endpoints.CHARACTER_TRAITS),
            limit=limit,
            params=params or None,
        ):
            yield CharacterTrait.model_validate(item)

    async def get(self, character_trait_id: str) -> CharacterTrait:
        """Retrieve a specific character trait.

        Args:
            character_trait_id: The ID of the trait to retrieve.

        Returns:
            The CharacterTrait object.

        Raises:
            NotFoundError: If the character trait does not exist.
            AuthorizationError: If you don't have access to the character.
        """
        response = await self._get(
            self._format_endpoint(Endpoints.CHARACTER_TRAIT, character_trait_id=character_trait_id)
        )
        return CharacterTrait.model_validate(response.json())

    async def delete(self, character_trait_id: str) -> None:
        """Delete a character trait.

        Args:
            character_trait_id: The ID of the trait to delete.
        """
        await self._delete(
            self._format_endpoint(Endpoints.CHARACTER_TRAIT, character_trait_id=character_trait_id)
        )

    async def assign(self, trait_id: str, value: int) -> CharacterTrait:
        """Assign a trait to a character.

        Args:
            trait_id: The ID of the trait to assign.
            value: The value of the trait to assign.

        Returns:
            The newly assigned CharacterTrait object.

        Raises:
            NotFoundError: If the trait does not exist.
            AuthorizationError: If you don't have access to the character.
            RequestValidationError: If the input parameters fail client-side validation.
            ValidationError: If the request data is invalid.
        """
        body = self._validate_request(
            CharacterCreateTraitAssign,
            trait_id=trait_id,
            value=value,
        )
        response = await self._post(
            self._format_endpoint(Endpoints.CHARACTER_TRAIT_CREATE),
            json=body.model_dump(exclude_none=True, exclude_unset=True, mode="json"),
        )
        return CharacterTrait.model_validate(response.json())

    async def create(
        self,
        request: TraitCreate | None = None,
        **kwargs,
    ) -> CharacterTrait:
        """Create a new character trait.

        Args:
            request: A TraitCreate model, OR pass fields as keyword arguments.
            **kwargs: Fields for TraitCreate if request is not provided.
                Required: name (str), parent_category_id (str).
                Optional: description (str | None), max_value (int), min_value (int),
                show_when_zero (bool), initial_cost (int | None),
                upgrade_cost (int | None), value (int | None).
        """
        body = request if request is not None else self._validate_request(TraitCreate, **kwargs)
        response = await self._post(
            self._format_endpoint(Endpoints.CHARACTER_TRAIT_CREATE),
            json=body.model_dump(exclude_none=True, exclude_unset=True, mode="json"),
        )
        return CharacterTrait.model_validate(response.json())

    # -------------------------------------------------------------------------
    # Trait Value Modification Methods
    # -------------------------------------------------------------------------

    async def get_value_options(
        self, character_trait_id: str
    ) -> CharacterTraitValueOptionsResponse:
        """Get the value options for a character trait.

        Args:
            character_trait_id: The ID of the trait to get the value options for.

        Returns:
            The CharacterTraitValueOptionsResponse object.

        Raises:
            NotFoundError: If the trait does not exist.
            AuthorizationError: If you don't have access to the character.
            RequestValidationError: If the input parameters fail client-side validation.
            ValidationError: If the request data is invalid.
        """
        response = await self._get(
            self._format_endpoint(
                Endpoints.CHARACTER_TRAIT_VALUE_OPTIONS, character_trait_id=character_trait_id
            ),
        )
        return CharacterTraitValueOptionsResponse.model_validate(response.json())

    async def change_value(
        self,
        character_trait_id: str,
        new_value: int,
        currency: TraitModifyCurrency,
    ) -> CharacterTrait:
        """Change the value of a character trait.

        Args:
            character_trait_id: The ID of the trait to change the value of.
            new_value: The new value of the trait.
            currency: The currency to use for the modification.
        """
        body = self._validate_request(
            _TraitModify,
            target_value=new_value,
            currency=currency,
        )
        response = await self._put(
            self._format_endpoint(
                Endpoints.CHARACTER_TRAIT_VALUE, character_trait_id=character_trait_id
            ),
            json=body.model_dump(exclude_none=True, exclude_unset=True, mode="json"),
        )
        return CharacterTrait.model_validate(response.json())
