"""Django settings for the Big-Five personality survey project."""
from __future__ import annotations

import os
from pathlib import Path
import logging.config
from urllib.parse import urlsplit, urlparse, unquote

from django.core.exceptions import ImproperlyConfigured

try:
    import dj_database_url
except ImportError:  # pragma: no cover - fallback when library missing locally
    dj_database_url = None

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent


def env_bool(name: str, default: bool = False) -> bool:
    """Return a boolean for the environment variable ``name``."""

    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.lower() in {"1", "true", "yes", "on"}


def env_list(name: str, default: list[str] | None = None, separator: str = ",") -> list[str]:
    """Split a comma-separated environment variable into a list."""

    raw = os.environ.get(name)
    if not raw:
        return default or []
    return [item.strip() for item in raw.split(separator) if item.strip()]


DEBUG = env_bool("DJANGO_DEBUG", default=False)

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = "django-insecure-change-me"
    else:
        raise ImproperlyConfigured("DJANGO_SECRET_KEY must be set when DEBUG is False.")

ALLOWED_HOSTS: list[str] = env_list("DJANGO_ALLOWED_HOSTS", ["*"])
CSRF_TRUSTED_ORIGINS: list[str] = env_list("DJANGO_CSRF_TRUSTED_ORIGINS")


SITE_BASE_URL = os.environ.get("SITE_BASE_URL", "").rstrip("/")
if SITE_BASE_URL:
    parsed_site = urlsplit(SITE_BASE_URL)
    if parsed_site.scheme and parsed_site.netloc:
        origin = f"{parsed_site.scheme}://{parsed_site.netloc}"
        if origin not in CSRF_TRUSTED_ORIGINS:
            CSRF_TRUSTED_ORIGINS.append(origin)
        host = parsed_site.hostname
        if host and host not in ALLOWED_HOSTS:
            ALLOWED_HOSTS.append(host)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "survey",
    "analytics",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "analytics.middleware.EnsureSessionIdMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

WSGI_APPLICATION = "config.wsgi.application"

def _absolute_sqlite_path(parsed_url) -> str:
    if parsed_url.path in {"", "/"}:
        return ":memory:"
    if parsed_url.netloc:
        # Handles sqlite:///var/db.sqlite3 (netloc empty) vs sqlite:////absolute/path
        path = f"//{parsed_url.netloc}{parsed_url.path}"
    else:
        path = parsed_url.path
    return os.path.abspath(os.path.join("/", path.lstrip("/")))


def database_config_from_env() -> dict:
    """Return Django DATABASES['default'] configuration from env vars."""

    url = os.environ.get("DATABASE_URL") or os.environ.get("DJANGO_DATABASE_URL")
    conn_max_age = int(os.environ.get("DJANGO_DB_CONN_MAX_AGE", "600") or "600")
    ssl_required = env_bool("DJANGO_DB_SSL_REQUIRED", default=not DEBUG)

    default_sqlite = f"sqlite:///{BASE_DIR / 'db.sqlite3'}"

    def _force_sqlite_config() -> dict:
        return {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
            "CONN_MAX_AGE": conn_max_age,
        }

    if dj_database_url is not None:
        parsed_config = dj_database_url.config(
            default=url or default_sqlite,
            conn_max_age=conn_max_age,
            ssl_require=ssl_required,
        )
        if parsed_config:
            engine = parsed_config.get("ENGINE")
            if engine == "django.db.backends.sqlite3":
                return _force_sqlite_config()
            options = parsed_config.get("OPTIONS")
            if isinstance(options, dict) and "sslmode" in options:
                options.pop("sslmode", None)
            return parsed_config

    if not url:
        return _force_sqlite_config()

    parsed = urlparse(url)
    scheme = parsed.scheme.lower()

    if scheme in {"postgres", "postgresql", "postgresql_psycopg2"}:
        engine = "django.db.backends.postgresql"
    elif scheme in {"mysql"}:
        engine = "django.db.backends.mysql"
    elif scheme in {"sqlite", "sqlite3"}:
        engine = "django.db.backends.sqlite3"
    else:
        raise ImproperlyConfigured(f"Unsupported database scheme '{parsed.scheme}'.")

    config: dict[str, object] = {
        "ENGINE": engine,
        "CONN_MAX_AGE": conn_max_age,
    }

    if engine == "django.db.backends.sqlite3":
        return _force_sqlite_config()
    else:
        config["NAME"] = parsed.path.lstrip("/")
        if not config["NAME"]:
            raise ImproperlyConfigured("Database name must be provided in DATABASE_URL.")
        if parsed.hostname:
            config["HOST"] = parsed.hostname
        if parsed.port:
            config["PORT"] = parsed.port
        if parsed.username:
            config["USER"] = unquote(parsed.username)
        if parsed.password:
            config["PASSWORD"] = unquote(parsed.password)
        if ssl_required:
            options = config.setdefault("OPTIONS", {})
            if isinstance(options, dict):
                options.setdefault("sslmode", "require")

    return config


DATABASES = {"default": database_config_from_env()}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "ja"
TIME_ZONE = "Asia/Tokyo"
USE_I18N = True
USE_TZ = True

STATIC_URL = os.environ.get("DJANGO_STATIC_URL", "/static/")
if not STATIC_URL.endswith("/"):
    STATIC_URL += "/"

STATICFILES_DIRS = [BASE_DIR / "static"]
FRONTEND_DIST_DIR = PROJECT_ROOT / "frontend" / "dist"
if FRONTEND_DIST_DIR.exists():
    STATICFILES_DIRS.append(FRONTEND_DIST_DIR)
STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

NOTE_DETAIL_URL = os.environ.get("NOTE_DETAIL_URL", "https://note.com/your_account/n/xxxxxxxx")

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
}

def _normalize_origin(raw: str) -> str:
    candidate = raw.strip()
    if not candidate:
        return ""
    if "://" not in candidate:
        candidate = f"https://{candidate}"
    return candidate.rstrip("/")


FRONTEND_ORIGIN = _normalize_origin(os.environ.get("FRONTEND_ORIGIN", "https://example.vercel.app"))

RENDER_EXTERNAL_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if RENDER_EXTERNAL_HOSTNAME:
    if RENDER_EXTERNAL_HOSTNAME not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
    render_origin = _normalize_origin(f"https://{RENDER_EXTERNAL_HOSTNAME}")
    if render_origin and render_origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(render_origin)

_DEFAULT_DEV_CORS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

def _unique(seq: list[str]) -> list[str]:
    seen: set[str] = set()
    return [x for x in seq if not (x in seen or seen.add(x))]


CORS_ALLOWED_ORIGINS = _unique(
    [origin for origin in (_normalize_origin(o) for o in env_list("DJANGO_CORS_ALLOWED_ORIGINS")) if origin]
)
if not CORS_ALLOWED_ORIGINS:
    fallback_origins: list[str] = []
    if FRONTEND_ORIGIN:
        fallback_origins.append(FRONTEND_ORIGIN)
    if DEBUG:
        fallback_origins.extend(_DEFAULT_DEV_CORS)
    CORS_ALLOWED_ORIGINS = _unique(fallback_origins)
CORS_ALLOW_CREDENTIALS = env_bool("DJANGO_CORS_ALLOW_CREDENTIALS", default=False)

if FRONTEND_ORIGIN and FRONTEND_ORIGIN not in CSRF_TRUSTED_ORIGINS:
    CSRF_TRUSTED_ORIGINS.append(FRONTEND_ORIGIN)

CORS_ALLOWED_ORIGIN_REGEXES = [r"^https://.*\\.vercel\\.app$"]

# Ensure well-known Vercel deployments are whitelisted even without env vars.
_DEFAULT_DEPLOYED_ORIGINS = _unique(
    [
        "https://big-five-app-git-main-hayatokimuras-projects.vercel.app",
        "https://big-five-app.vercel.app",
    ]
)

for origin in _DEFAULT_DEPLOYED_ORIGINS:
    if origin not in CORS_ALLOWED_ORIGINS:
        CORS_ALLOWED_ORIGINS.append(origin)
    if origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(origin)


USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SECURE_SSL_REDIRECT = env_bool("DJANGO_SECURE_SSL_REDIRECT", default=not DEBUG)
SESSION_COOKIE_SECURE = env_bool("DJANGO_SESSION_COOKIE_SECURE", default=not DEBUG)
CSRF_COOKIE_SECURE = env_bool("DJANGO_CSRF_COOKIE_SECURE", default=not DEBUG)
SECURE_HSTS_SECONDS = int(
    os.environ.get("DJANGO_SECURE_HSTS_SECONDS", "0" if DEBUG else "31536000")
    or ("0" if DEBUG else "31536000")
)
SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool(
    "DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS",
    default=not DEBUG,
)
SECURE_HSTS_PRELOAD = env_bool("DJANGO_SECURE_HSTS_PRELOAD", default=False)
SECURE_REFERRER_POLICY = os.environ.get(
    "DJANGO_SECURE_REFERRER_POLICY", "strict-origin-when-cross-origin"
)
X_FRAME_OPTIONS = os.environ.get("DJANGO_X_FRAME_OPTIONS", "DENY")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s [%(name)s] %(message)s",
        },
        "simple": {
            "format": "%(levelname)s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "verbose",
        }
    },
    "root": {
        "handlers": ["console"],
        "level": os.environ.get("DJANGO_LOG_LEVEL", "INFO"),
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": os.environ.get("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        "django.security": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}
