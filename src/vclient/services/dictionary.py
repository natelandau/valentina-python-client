"""Service for interacting with the Dictionary API."""

from collections.abc import AsyncIterator
from typing import TYPE_CHECKING

from vclient.constants import DEFAULT_PAGE_LIMIT
from vclient.endpoints import Endpoints
from vclient.models import (
    DictionaryTerm,
    DictionaryTermCreate,
    DictionaryTermUpdate,
    PaginatedResponse,
)
from vclient.services.base import BaseService

if TYPE_CHECKING:
    from vclient.client import VClient


class DictionaryService(BaseService):
    """Service for interacting with the Dictionary API."""

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
        return endpoint.format(company_id=self._company_id, **kwargs)

    # -------------------------------------------------------------------------
    # Dictionary Term CRUD Methods
    # -------------------------------------------------------------------------

    async def get_page(
        self,
        *,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
        term: str | None = None,
    ) -> PaginatedResponse[DictionaryTerm]:
        """Retrieve a paginated page of dictionary terms."""
        params = {}
        if term is not None:
            params["term"] = term

        return await self._get_paginated_as(
            self._format_endpoint(Endpoints.DICTIONARY_TERMS),
            DictionaryTerm,
            limit=limit,
            offset=offset,
            params=params if params else None,
        )

    async def list_all(self, *, term: str | None = None) -> list[DictionaryTerm]:
        """Retrieve all dictionary terms."""
        return [term async for term in self.iter_all(term=term)]

    async def iter_all(
        self, *, term: str | None = None, limit: int = 100
    ) -> AsyncIterator[DictionaryTerm]:
        """Iterate through all dictionary terms."""
        params = {}
        if term is not None:
            params["term"] = term
        async for item in self._iter_all_pages(
            self._format_endpoint(Endpoints.DICTIONARY_TERMS),
            limit=limit,
            params=params if params else None,
        ):
            yield DictionaryTerm.model_validate(item)

    async def get(self, term_id: str) -> DictionaryTerm:
        """Retrieve a specific dictionary term."""
        response = await self._get(
            self._format_endpoint(Endpoints.DICTIONARY_TERM, term_id=term_id)
        )
        return DictionaryTerm.model_validate(response.json())

    async def create(
        self,
        request: DictionaryTermCreate | None = None,
        /,
        **kwargs,
    ) -> DictionaryTerm:
        """Create a new dictionary term.

        Args:
            request: A DictionaryTermCreate model, OR pass fields as keyword arguments.
            **kwargs: Fields for DictionaryTermCreate if request is not provided.
                Accepts: term (str, required), definition (str | None),
                link (str | None), synonyms (list[str]).
        """
        body = request if request is not None else DictionaryTermCreate(**kwargs)
        response = await self._post(
            self._format_endpoint(Endpoints.DICTIONARY_TERMS),
            json=body.model_dump(exclude_none=True, exclude_unset=True, mode="json"),
        )
        return DictionaryTerm.model_validate(response.json())

    async def update(
        self,
        term_id: str,
        request: DictionaryTermUpdate | None = None,
        /,
        **kwargs,
    ) -> DictionaryTerm:
        """Update a specific dictionary term.

        Args:
            term_id: The ID of the term to update.
            request: A DictionaryTermUpdate model, OR pass fields as keyword arguments.
            **kwargs: Fields for DictionaryTermUpdate if request is not provided.
                Accepts: term (str | None), definition (str | None),
                link (str | None), synonyms (list[str] | None).
        """
        body = request if request is not None else DictionaryTermUpdate(**kwargs)
        response = await self._put(
            self._format_endpoint(Endpoints.DICTIONARY_TERM, term_id=term_id),
            json=body.model_dump(exclude_none=True, exclude_unset=True, mode="json"),
        )
        return DictionaryTerm.model_validate(response.json())

    async def delete(self, term_id: str) -> None:
        """Delete a specific dictionary term."""
        await self._delete(self._format_endpoint(Endpoints.DICTIONARY_TERM, term_id=term_id))
