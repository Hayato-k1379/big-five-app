#!/usr/bin/env python3
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def main() -> None:
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.config.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and available on your PATH? "
            "You might need to activate a virtual environment."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
