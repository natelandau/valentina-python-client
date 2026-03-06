"""Testing utilities for downstream applications using vclient.

Requires the 'testing' extra: pip install vclient[testing]
"""

try:
    import polyfactory  # noqa: F401
except ImportError as e:
    msg = (
        "vclient.testing requires the 'testing' extra. "
        "Install it with: pip install vclient[testing]"
    )
    raise ImportError(msg) from e
