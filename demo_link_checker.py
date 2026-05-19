#!/usr/bin/env python3
"""Back-compat shim — see substack_link_checker.demo."""

import os
import sys

_SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
if os.path.isdir(_SRC) and _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from substack_link_checker.demo import main  # noqa: E402

if __name__ == "__main__":
    main()
