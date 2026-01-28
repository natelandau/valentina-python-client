"""Tests for the registry module."""

import pytest

from vclient import VClient
from vclient.registry import (
    books_service,
    campaigns_service,
    chapters_service,
    character_autogen_service,
    character_blueprint_service,
    character_traits_service,
    characters_service,
    companies_service,
    configure_default_client,
    default_client,
    developer_service,
    dicreolls_service,
    dictionary_service,
    global_admin_service,
    options_service,
    system_service,
    users_service,
)
from vclient.services import (
    BooksService,
    CampaignsService,
    ChaptersService,
    CharacterAutogenService,
    CharacterBlueprintService,
    CharactersService,
    CharacterTraitsService,
    CompaniesService,
    DeveloperService,
    DicreollService,
    DictionaryService,
    GlobalAdminService,
    OptionsService,
    SystemService,
    UsersService,
)


@pytest.fixture(autouse=True)
def reset_default_client():
    """Reset the default client before and after each test."""
    # Given: Clear any existing default client
    from vclient import registry

    registry._default_client = None
    yield
    # Then: Clean up after test
    registry._default_client = None


class TestConfigureDefaultClient:
    """Tests for configure_default_client function."""

    def test_configure_default_client_stores_client(self, api_config) -> None:
        """Verify configure_default_client stores the client in module state."""
        # Given: A VClient instance
        client = VClient(config=api_config)

        # When: Configuring the default client
        configure_default_client(client)

        # Then: The client is stored
        from vclient import registry

        assert registry._default_client is client

    def test_configure_default_client_overwrites_previous(self, api_config) -> None:
        """Verify configure_default_client overwrites a previously configured client."""
        # Given: Two VClient instances
        client1 = VClient(config=api_config)
        client2 = VClient(config=api_config)

        # When: Configuring the first, then the second
        configure_default_client(client1)
        configure_default_client(client2)

        # Then: The second client is stored
        from vclient import registry

        assert registry._default_client is client2


class TestDefaultClient:
    """Tests for default_client function."""

    def test_default_client_raises_when_not_configured(self) -> None:
        """Verify default_client raises RuntimeError when no client is configured."""
        # Given: No default client configured

        # When/Then: Calling default_client raises RuntimeError
        with pytest.raises(RuntimeError, match="No default client configured"):
            default_client()

    def test_default_client_returns_configured_client(self, api_config) -> None:
        """Verify default_client returns the configured client."""
        # Given: A configured default client
        client = VClient(config=api_config)
        configure_default_client(client)

        # When: Getting the default client
        result = default_client()

        # Then: The configured client is returned
        assert result is client


class TestCompaniesService:
    """Tests for companies_service factory function."""

    def test_companies_service_raises_when_not_configured(self) -> None:
        """Verify companies_service raises RuntimeError when no client is configured."""
        # Given: No default client configured

        # When/Then: Calling companies_service raises RuntimeError
        with pytest.raises(RuntimeError, match="No default client configured"):
            companies_service()

    def test_companies_service_returns_service_instance(self, api_config) -> None:
        """Verify companies_service returns a CompaniesService with the default client."""
        # Given: A configured default client
        client = VClient(config=api_config)
        configure_default_client(client)

        # When: Getting the companies service
        service = companies_service()

        # Then: A CompaniesService is returned with the correct client
        assert isinstance(service, CompaniesService)
        assert service._client is client


class TestGlobalAdminService:
    """Tests for global_admin_service factory function."""

    def test_global_admin_service_raises_when_not_configured(self) -> None:
        """Verify global_admin_service raises RuntimeError when no client is configured."""
        # Given: No default client configured

        # When/Then: Calling global_admin_service raises RuntimeError
        with pytest.raises(RuntimeError, match="No default client configured"):
            global_admin_service()

    def test_global_admin_service_returns_service_instance(self, api_config) -> None:
        """Verify global_admin_service returns a GlobalAdminService with the default client."""
        # Given: A configured default client
        client = VClient(config=api_config)
        configure_default_client(client)

        # When: Getting the global admin service
        service = global_admin_service()

        # Then: A GlobalAdminService is returned with the correct client
        assert isinstance(service, GlobalAdminService)
        assert service._client is client


class TestCharacterTraitsService:
    """Tests for character_traits_service factory function."""

    def test_character_traits_service_raises_when_not_configured(self) -> None:
        """Verify character_traits_service raises RuntimeError when no client is configured."""
        # Given: No default client configured

        # When/Then: Calling character_traits_service raises RuntimeError
        with pytest.raises(RuntimeError, match="No default client configured"):
            character_traits_service(
                user_id="user_id",
                campaign_id="campaign_id",
                character_id="character_id",
                company_id="company_id",
            )

    def test_character_traits_service_returns_service_instance(self, api_config) -> None:
        """Verify character_traits_service returns a CharacterTraitsService with the default client."""
        # Given: A configured default client
        client = VClient(config=api_config)
        configure_default_client(client)

        # When: Getting the character traits service
        service = character_traits_service(
            user_id="user_id",
            campaign_id="campaign_id",
            character_id="character_id",
            company_id="company_id",
        )

        # Then: A CharacterTraitsService is returned with the correct client
        assert isinstance(service, CharacterTraitsService)
        assert service._client is client


class TestCharactersService:
    """Tests for characters_service factory function."""

    def test_characters_service_raises_when_not_configured(self) -> None:
        """Verify characters_service raises RuntimeError when no client is configured."""
        # Given: No default client configured

        # When/Then: Calling characters_service raises RuntimeError
        with pytest.raises(RuntimeError, match="No default client configured"):
            characters_service(
                user_id="user_id", campaign_id="campaign_id", company_id="company_id"
            )

    def test_characters_service_returns_service_instance(self, api_config) -> None:
        """Verify characters_service returns a CharactersService with the default client."""
        # Given: A configured default client
        client = VClient(config=api_config)
        configure_default_client(client)

        # When: Getting the characters service
        service = characters_service(
            user_id="user_id", campaign_id="campaign_id", company_id="company_id"
        )

        # Then: A CharactersService is returned with the correct client
        assert isinstance(service, CharactersService)
        assert service._client is client


class TestChaptersService:
    """Tests for chapters_service factory function."""

    def test_chapters_service_raises_when_not_configured(self) -> None:
        """Verify chapters_service raises RuntimeError when no client is configured."""
        # Given: No default client configured

        # When/Then: Calling chapters_service raises RuntimeError
        with pytest.raises(RuntimeError, match="No default client configured"):
            chapters_service(
                user_id="user_id",
                campaign_id="campaign_id",
                book_id="book_id",
                company_id="company_id",
            )

    def test_chapters_service_returns_service_instance(self, api_config) -> None:
        """Verify chapters_service returns a ChaptersService with the default client."""
        # Given: A configured default client
        client = VClient(config=api_config)
        configure_default_client(client)

        # When: Getting the chapters service
        service = chapters_service(
            user_id="user_id", campaign_id="campaign_id", book_id="book_id", company_id="company_id"
        )

        # Then: A ChaptersService is returned with the correct client
        assert isinstance(service, ChaptersService)
        assert service._client is client


class TestBooksService:
    """Tests for books_service factory function."""

    def test_books_service_raises_when_not_configured(self) -> None:
        """Verify books_service raises RuntimeError when no client is configured."""
        # Given: No default client configured

        # When/Then: Calling books_service raises RuntimeError
        with pytest.raises(RuntimeError, match="No default client configured"):
            books_service(user_id="user_id", campaign_id="campaign_id", company_id="company_id")

    def test_books_service_returns_service_instance(self, api_config) -> None:
        """Verify books_service returns a BooksService with the default client."""
        # Given: A configured default client
        client = VClient(config=api_config)
        configure_default_client(client)

        # When: Getting the books service
        service = books_service(
            user_id="user_id", campaign_id="campaign_id", company_id="company_id"
        )

        # Then: A BooksService is returned with the correct client
        assert isinstance(service, BooksService)
        assert service._client is client


class TestCampaignsService:
    """Tests for campaigns_service factory function."""

    def test_campaigns_service_raises_when_not_configured(self) -> None:
        """Verify campaigns_service raises RuntimeError when no client is configured."""
        # Given: No default client configured

        # When/Then: Calling campaigns_service raises RuntimeError
        with pytest.raises(RuntimeError, match="No default client configured"):
            campaigns_service(user_id="user_id", company_id="company_id")

    def test_campaigns_service_returns_service_instance(self, api_config) -> None:
        """Verify campaigns_service returns a CampaignsService with the default client."""
        # Given: A configured default client
        client = VClient(config=api_config)
        configure_default_client(client)

        # When: Getting the campaigns service
        service = campaigns_service(user_id="user_id", company_id="company_id")

        # Then: A CampaignsService is returned with the correct client
        assert isinstance(service, CampaignsService)
        assert service._client is client


class TestUsersService:
    """Tests for users_service factory function."""

    def test_users_service_raises_when_not_configured(self) -> None:
        """Verify users_service raises RuntimeError when no client is configured."""
        # Given: No default client configured

        # When/Then: Calling users_service raises RuntimeError
        with pytest.raises(RuntimeError, match="No default client configured"):
            users_service(company_id="company_id")

    def test_users_service_returns_service_instance(self, api_config) -> None:
        """Verify users_service returns a UsersService with the default client."""
        # Given: A configured default client
        client = VClient(config=api_config)
        configure_default_client(client)

        # When: Getting the users service
        service = users_service(company_id="company_id")

        # Then: A UsersService is returned with the correct client
        assert isinstance(service, UsersService)
        assert service._client is client


class TestSystemService:
    """Tests for system_service factory function."""

    def test_system_service_raises_when_not_configured(self) -> None:
        """Verify system_service raises RuntimeError when no client is configured."""
        # Given: No default client configured

        # When/Then: Calling system_service raises RuntimeError
        with pytest.raises(RuntimeError, match="No default client configured"):
            system_service()

    def test_system_service_returns_service_instance(self, api_config) -> None:
        """Verify system_service returns a SystemService with the default client."""
        # Given: A configured default client
        client = VClient(config=api_config)
        configure_default_client(client)

        # When: Getting the system service
        service = system_service()

        # Then: A SystemService is returned with the correct client
        assert isinstance(service, SystemService)
        assert service._client is client


class TestTopLevelImports:
    """Tests for top-level package imports."""

    def test_imports_from_vclient(self) -> None:
        """Verify factory functions are importable from vclient package."""
        # When: Importing from vclient
        from vclient import (
            companies_service,
            configure_default_client,
            default_client,
            global_admin_service,
            system_service,
        )

        # Then: All functions are callable
        assert callable(configure_default_client)
        assert callable(default_client)
        assert callable(companies_service)
        assert callable(global_admin_service)
        assert callable(system_service)

    def test_imports_from_vclient_api(self) -> None:
        """Verify factory functions are importable from vclient package."""
        # When: Importing from vclient
        from vclient import (
            companies_service,
            configure_default_client,
            default_client,
            global_admin_service,
            system_service,
        )

        # Then: All functions are callable
        assert callable(configure_default_client)
        assert callable(default_client)
        assert callable(companies_service)
        assert callable(global_admin_service)
        assert callable(system_service)


class TestDeveloperService:
    """Tests for developer_service factory function."""

    def test_developer_service_raises_when_not_configured(self) -> None:
        """Verify developer_service raises RuntimeError when no client is configured."""
        # Given: No default client configured

        # When/Then: Calling developer_service raises RuntimeError
        with pytest.raises(RuntimeError, match="No default client configured"):
            developer_service()

    def test_developer_service_returns_service_instance(self, api_config) -> None:
        """Verify developer_service returns a DeveloperService with the default client."""
        # Given: A configured default client
        client = VClient(config=api_config)
        configure_default_client(client)

        # When: Getting the developer service
        service = developer_service()

        # Then: A DeveloperService is returned with the correct client
        assert isinstance(service, DeveloperService)
        assert service._client is client


class TestCharacterBlueprintService:
    """Tests for character_blueprint_service factory function."""

    def test_character_blueprint_service_raises_when_not_configured(self) -> None:
        """Verify character_blueprint_service raises RuntimeError when no client is configured."""
        # Given: No default client configured

        # When/Then: Calling character_blueprint_service raises RuntimeError
        with pytest.raises(RuntimeError, match="No default client configured"):
            character_blueprint_service(company_id="company_id")

    def test_character_blueprint_service_returns_service_instance(self, api_config) -> None:
        """Verify character_blueprint_service returns a CharacterBlueprintService with the default client."""
        # Given: A configured default client
        client = VClient(config=api_config)
        configure_default_client(client)

        # When: Getting the character blueprint service
        service = character_blueprint_service(company_id="company_id")

        # Then: A CharacterBlueprintService is returned with the correct client
        assert isinstance(service, CharacterBlueprintService)
        assert service._client is client


class TestDictionaryService:
    """Tests for dictionary_service factory function."""

    def test_dictionary_service_raises_when_not_configured(self) -> None:
        """Verify dictionary_service raises RuntimeError when no client is configured."""
        # Given: No default client configured

        # When/Then: Calling dictionary_service raises RuntimeError
        with pytest.raises(RuntimeError, match="No default client configured"):
            dictionary_service(company_id="company_id")

    def test_dictionary_service_returns_service_instance(self, api_config) -> None:
        """Verify dictionary_service returns a DictionaryService with the default client."""
        # Given: A configured default client
        client = VClient(config=api_config)
        configure_default_client(client)

        # When: Getting the dictionary service
        service = dictionary_service(company_id="company_id")

        # Then: A DictionaryService is returned with the correct client
        assert isinstance(service, DictionaryService)
        assert service._client is client


class TestDicreollService:
    """Tests for dicreolls_service factory function."""

    def test_dicreolls_service_raises_when_not_configured(self) -> None:
        """Verify dicreolls_service raises RuntimeError when no client is configured."""
        # Given: No default client configured

        # When/Then: Calling dicreolls_service raises RuntimeError
        with pytest.raises(RuntimeError, match="No default client configured"):
            dicreolls_service(user_id="user_id", company_id="company_id")

    def test_dicreolls_service_returns_service_instance(self, api_config) -> None:
        """Verify dicreolls_service returns a DicreollService with the default client."""
        # Given: A configured default client
        client = VClient(config=api_config)
        configure_default_client(client)

        # When: Getting the dicreolls service
        service = dicreolls_service(user_id="user_id", company_id="company_id")

        # Then: A DicreollService is returned with the correct client
        assert isinstance(service, DicreollService)
        assert service._client is client


class TestOptionsService:
    """Tests for options_service factory function."""

    def test_options_service_raises_when_not_configured(self) -> None:
        """Verify options_service raises RuntimeError when no client is configured."""
        # Given: No default client configured

        # When/Then: Calling options_service raises RuntimeError
        with pytest.raises(RuntimeError, match="No default client configured"):
            options_service(company_id="company_id")

    def test_options_service_returns_service_instance(self, api_config) -> None:
        """Verify options_service returns a OptionsService with the default client."""
        # Given: A configured default client
        client = VClient(config=api_config)
        configure_default_client(client)

        # When: Getting the options service
        service = options_service(company_id="company_id")

        # Then: A OptionsService is returned with the correct client
        assert isinstance(service, OptionsService)
        assert service._client is client


class TestCharacterAutogenService:
    """Tests for character_autogen_service factory function."""

    def test_character_autogen_service_raises_when_not_configured(self) -> None:
        """Verify character_autogen_service raises RuntimeError when no client is configured."""
        # Given: No default client configured

        # When/Then: Calling character_autogen_service raises RuntimeError
        with pytest.raises(RuntimeError, match="No default client configured"):
            character_autogen_service(
                user_id="user_id", campaign_id="campaign_id", company_id="company_id"
            )

    def test_character_autogen_service_returns_service_instance(self, api_config) -> None:
        """Verify character_autogen_service returns a CharacterAutogenService with the default client."""
        # Given: A configured default client
        client = VClient(config=api_config)
        configure_default_client(client)

        # When: Getting the character autogen service
        service = character_autogen_service(
            user_id="user_id", campaign_id="campaign_id", company_id="company_id"
        )

        # Then: A CharacterAutogenService is returned with the correct client
        assert isinstance(service, CharacterAutogenService)
        assert service._client is client


class TestDefaultCompanyId:
    """Tests for default_company_id behavior."""

    def test_uses_default_company_id_when_not_provided(self, api_config) -> None:
        """Verify service uses default_company_id when company_id not passed."""
        # Given: A client with default_company_id configured
        api_config.default_company_id = "default-company"
        client = VClient(config=api_config)
        configure_default_client(client)

        # When: Getting users service without company_id
        service = users_service()

        # Then: Service uses the default company_id
        assert service._company_id == "default-company"

    def test_explicit_company_id_overrides_default(self, api_config) -> None:
        """Verify explicit company_id overrides default_company_id."""
        # Given: A client with default_company_id configured
        api_config.default_company_id = "default-company"
        client = VClient(config=api_config)
        configure_default_client(client)

        # When: Getting users service with explicit company_id
        service = users_service("explicit-company")

        # Then: Service uses the explicit company_id
        assert service._company_id == "explicit-company"

    def test_raises_when_no_company_id_and_no_default(self, api_config) -> None:
        """Verify ValueError raised when no company_id and no default."""
        # Given: A client without default_company_id
        client = VClient(config=api_config)
        configure_default_client(client)

        # When/Then: Calling users_service without company_id raises ValueError
        with pytest.raises(ValueError, match="company_id is required"):
            users_service()


class TestVClientDefaultCompanyId:
    """Tests for VClient default_company_id behavior."""

    def test_default_company_id_property(self, api_config) -> None:
        """Verify default_company_id property returns configured value."""
        # Given: Config with default_company_id
        api_config.default_company_id = "my-company"

        # When: Creating client
        client = VClient(config=api_config, set_as_default=False)

        # Then: Property returns the value
        assert client.default_company_id == "my-company"

    def test_default_company_id_property_returns_none(self, api_config) -> None:
        """Verify default_company_id property returns None when not configured."""
        # Given: Config without default_company_id

        # When: Creating client
        client = VClient(config=api_config, set_as_default=False)

        # Then: Property returns None
        assert client.default_company_id is None

    def test_default_company_id_from_init_param(self, base_url, api_key) -> None:
        """Verify default_company_id can be set via init parameter."""
        # When: Creating client with default_company_id param
        client = VClient(
            base_url=base_url,
            api_key=api_key,
            default_company_id="param-company",
            set_as_default=False,
        )

        # Then: Property returns the value
        assert client.default_company_id == "param-company"

    def test_client_users_uses_default_company_id(self, api_config) -> None:
        """Verify client.users() uses default_company_id when not passed."""
        # Given: A client with default_company_id configured
        api_config.default_company_id = "default-company"
        client = VClient(config=api_config, set_as_default=False)

        # When: Getting users service without company_id
        service = client.users()

        # Then: Service uses the default company_id
        assert service._company_id == "default-company"

    def test_client_users_explicit_overrides_default(self, api_config) -> None:
        """Verify client.users() explicit company_id overrides default."""
        # Given: A client with default_company_id configured
        api_config.default_company_id = "default-company"
        client = VClient(config=api_config, set_as_default=False)

        # When: Getting users service with explicit company_id
        service = client.users("explicit-company")

        # Then: Service uses the explicit company_id
        assert service._company_id == "explicit-company"

    def test_client_users_raises_when_no_company_id_and_no_default(self, api_config) -> None:
        """Verify client.users() raises ValueError when no company_id and no default."""
        # Given: A client without default_company_id
        client = VClient(config=api_config, set_as_default=False)

        # When/Then: Calling users() without company_id raises ValueError
        with pytest.raises(ValueError, match="company_id is required"):
            client.users()
