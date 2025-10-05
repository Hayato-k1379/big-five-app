"""ASGI config for the Big-Five survey project."""
from __future__ import annotations

import os
import sys
from pathlib import Path

from django.core.asgi import get_asgi_application

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_asgi_application()
