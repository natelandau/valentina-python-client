"""Verify that Routes constants and _ROUTE_DEFAULTS stay in sync."""

from vclient.testing._router import _ROUTE_DEFAULTS
from vclient.testing._routes import Routes, RouteSpec


def _collect_route_specs() -> dict[tuple[str, str], str]:
    """Collect all RouteSpec values from the Routes class.

    Returns:
        dict mapping (method, pattern) to the style string.
    """
    specs: dict[tuple[str, str], str] = {}
    for name in dir(Routes):
        val = getattr(Routes, name)
        if isinstance(val, RouteSpec):
            specs[(val.method, val.pattern)] = val.style
    return specs


def _collect_route_defaults() -> dict[tuple[str, str], str]:
    """Collect all entries from _ROUTE_DEFAULTS.

    Returns:
        dict mapping (method, pattern) to the style string.
    """
    return {(method, pattern): style for method, pattern, _, style in _ROUTE_DEFAULTS}


class TestRoutesCompleteness:
    """Verify that Routes constants and _ROUTE_DEFAULTS are fully aligned."""

    def test_all_defaults_covered(self) -> None:
        """Verify every _ROUTE_DEFAULTS entry has a matching Routes constant."""
        # Given
        route_specs = _collect_route_specs()
        defaults = _collect_route_defaults()

        # When
        missing = {key for key in defaults if key not in route_specs}

        # Then
        assert not missing, f"_ROUTE_DEFAULTS entries missing from Routes: {missing}"

    def test_no_extra_routes(self) -> None:
        """Verify no Routes constant exists without a matching _ROUTE_DEFAULTS entry."""
        # Given
        route_specs = _collect_route_specs()
        defaults = _collect_route_defaults()

        # When
        extra = {key for key in route_specs if key not in defaults}

        # Then
        assert not extra, f"Routes constants without matching _ROUTE_DEFAULTS entry: {extra}"

    def test_styles_match(self) -> None:
        """Verify the style field matches between each Routes constant and its _ROUTE_DEFAULTS entry."""
        # Given
        route_specs = _collect_route_specs()
        defaults = _collect_route_defaults()

        # When
        mismatches: list[str] = []
        for key, routes_style in route_specs.items():
            if key in defaults and defaults[key] != routes_style:
                mismatches.append(
                    f"{key}: Routes has '{routes_style}', _ROUTE_DEFAULTS has '{defaults[key]}'"
                )

        # Then
        assert not mismatches, "Style mismatches:\n" + "\n".join(mismatches)
