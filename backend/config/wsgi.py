"""WSGI config for the Big-Five survey project."""
from __future__ import annotations

import os
import sys
from pathlib import Path

from django.core.wsgi import get_wsgi_application

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.config.settings")

application = get_wsgi_application()
