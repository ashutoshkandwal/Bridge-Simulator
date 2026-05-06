"""Package entrypoint for the ECDIS display.

The current upload still keeps the original ecdis.py at the repository root.
This wrapper preserves main.py imports until the project is fully reorganized.
"""

from ecdis import ECDISDisplay  # noqa: F401
