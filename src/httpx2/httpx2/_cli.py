from __future__ import annotations

import sys


def main() -> None:
    try:
        from ._main import main as _main
    except ImportError:  # pragma: no cover
        print(
            "The httpx command line client could not run because the required "
            "dependencies were not installed.\nMake sure you've installed "
            "everything with: pip install 'httpx[cli]'"
        )
        sys.exit(1)
    _main()
