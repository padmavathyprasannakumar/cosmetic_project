"""
Django settings for cosmeticproject project.
Ready for local development, Render deployment, Cloudinary media storage,
Cashfree payment, and Brevo SMTP email.
"""

from pathlib import Path
import os
from urllib.parse import urlparse, unquote

import dj_database_url

# =========================================================
# BASE DIRECTORY
# =========================================================
BASE_DIR = Path(__file__).resolve().parent.parent

# =========================================================
# SECURITY SETTINGS
# =========================================================
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "django-insecure-local-dev-only-change-this-key"
)

DEBUG = os.getenv("DEBUG", "False").lower() == "true"

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "cosmetic-project-2.onrender.com",
    ".onrender.com",
]

RENDER_EXTERNAL_HOSTNAME = os.getenv("RENDER_EXTERNAL_HOSTNAME")
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

EXTRA_ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "")
if EXTRA_ALLOWED_HOSTS:
    ALLOWED_HOSTS += [
        host.strip()
        for host in EXTRA_ALLOWED_HOSTS.split(",")
        if host.strip()
    ]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "https://cosmetic-project-2.onrender.com",
    "https://*.onrender.com",
]

EXTRA_CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS", "")
if EXTRA_CSRF_TRUSTED_ORIGINS:
    CSRF_TRUSTED_ORIGINS += [
        origin.strip()
        for origin in EXTRA_CSRF_TRUSTED_ORIGINS.split(",")
        if origin.strip()
    ]

if RENDER_EXTERNAL_HOSTNAME:
    render_origin = f"https://{RENDER_EXTERNAL_HOSTNAME}"
    if render_origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(render_origin)

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG

# =========================================================
# APPLICATIONS
# =========================================================
INSTALLED_APPS = [
    # Cloudinary
    # Do not add "cloudinary_storage" here because it can break collectstatic on Render.
    "cloudinary",

    # Django apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Custom apps
    "dashboard",
]

# =========================================================
# MIDDLEWARE
# =========================================================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# =========================================================
# URLS / WSGI
# =========================================================
ROOT_URLCONF = "cosmeticproject.urls"
WSGI_APPLICATION = "cosmeticproject.wsgi.application"

# =========================================================
# TEMPLATES
# =========================================================
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "dashboard.context_processors.global_site_data",
                "dashboard.context_processors.footer_data",
            ],
        },
    },
]

# =========================================================
# DATABASE
# =========================================================
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            ssl_require=not DEBUG,
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# =========================================================
# PASSWORD VALIDATION
# =========================================================
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

# =========================================================
# INTERNATIONALIZATION
# =========================================================
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kuala_Lumpur"
USE_I18N = True
USE_TZ = True

# =========================================================
# STATIC FILES
# =========================================================
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_DIRS = []

if (BASE_DIR / "dashboard" / "static").exists():
    STATICFILES_DIRS.append(BASE_DIR / "dashboard" / "static")

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# =========================================================
# MEDIA FILES / CLOUDINARY
# =========================================================
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

CLOUDINARY_URL = os.getenv("CLOUDINARY_URL", "")

USE_CLOUDINARY = os.getenv(
    "USE_CLOUDINARY",
    "True" if CLOUDINARY_URL or os.getenv("CLOUDINARY_CLOUD_NAME") else "False"
).lower() == "true"

# Option 1 for Render:
# CLOUDINARY_URL=cloudinary://API_KEY:API_SECRET@CLOUD_NAME
#
# Option 2:
# CLOUDINARY_CLOUD_NAME=your_cloud_name
# CLOUDINARY_API_KEY=your_api_key
# CLOUDINARY_API_SECRET=your_api_secret

if CLOUDINARY_URL:
    parsed_cloudinary_url = urlparse(CLOUDINARY_URL)

    CLOUDINARY_STORAGE = {
        "CLOUD_NAME": parsed_cloudinary_url.hostname or "",
        "API_KEY": unquote(parsed_cloudinary_url.username or ""),
        "API_SECRET": unquote(parsed_cloudinary_url.password or ""),
    }
else:
    CLOUDINARY_STORAGE = {
        "CLOUD_NAME": os.getenv("CLOUDINARY_CLOUD_NAME", ""),
        "API_KEY": os.getenv("CLOUDINARY_API_KEY", ""),
        "API_SECRET": os.getenv("CLOUDINARY_API_SECRET", ""),
    }

# Django 6 storage settings
STORAGES = {
    "default": {
        "BACKEND": (
            "cloudinary_storage.storage.MediaCloudinaryStorage"
            if USE_CLOUDINARY
            else "django.core.files.storage.FileSystemStorage"
        ),
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Compatibility setting for older storage packages
if USE_CLOUDINARY:
    DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"
else:
    DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"

# =========================================================
# LOGIN / LOGOUT
# =========================================================
LOGIN_URL = "dashboard:login"
LOGIN_REDIRECT_URL = "dashboard:home"
LOGOUT_REDIRECT_URL = "dashboard:login"

# =========================================================
# DEFAULT PRIMARY KEY FIELD
# =========================================================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# =========================================================
# SEARCH FUNCTIONALITY
# =========================================================
SEARCH_RESULTS_PER_PAGE = 12

# =========================================================
# CASHFREE PAYMENT SETTINGS
# =========================================================
CASHFREE_ENV = os.getenv("CASHFREE_ENV", "sandbox").strip().lower()
CASHFREE_CLIENT_ID = os.getenv("CASHFREE_CLIENT_ID", "").strip()
CASHFREE_CLIENT_SECRET = os.getenv("CASHFREE_CLIENT_SECRET", "").strip()
CASHFREE_API_VERSION = "2025-01-01"

if CASHFREE_ENV == "production":
    CASHFREE_BASE_URL = "https://api.cashfree.com/pg"
else:
    CASHFREE_BASE_URL = "https://sandbox.cashfree.com/pg"

# =========================================================
# SITE SETTINGS
# =========================================================
SITE_NAME = "Glowify"
SITE_DESCRIPTION = "Glowify Cosmetic Products Online Store"
SITE_KEYWORDS = "cosmetics, beauty, skincare, makeup, Glowify"

# =========================================================
# EMAIL SETTINGS - BREVO SMTP
# =========================================================
EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND",
    "django.core.mail.backends.smtp.EmailBackend"
)

EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp-relay.brevo.com").strip()
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True").lower() == "true"
EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL", "False").lower() == "true"
EMAIL_TIMEOUT = int(os.getenv("EMAIL_TIMEOUT", "30"))

EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "").strip()
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "").strip()

DEFAULT_FROM_EMAIL = os.getenv(
    "DEFAULT_FROM_EMAIL",
    EMAIL_HOST_USER
).strip()

SERVER_EMAIL = os.getenv(
    "SERVER_EMAIL",
    DEFAULT_FROM_EMAIL
).strip()

# =========================================================
# BREVO / CONTACT SETTINGS
# =========================================================
BREVO_API_KEY = os.getenv("BREVO_API_KEY", "").strip()
BREVO_SENDER_EMAIL = os.getenv(
    "BREVO_SENDER_EMAIL",
    DEFAULT_FROM_EMAIL
).strip()
BREVO_SENDER_NAME = os.getenv("BREVO_SENDER_NAME", "Glowify").strip()

CONTACT_RECEIVER_EMAIL = os.getenv(
    "CONTACT_RECEIVER_EMAIL",
    BREVO_SENDER_EMAIL
).strip()

# =========================================================
# SECURITY SETTINGS FOR RENDER PRODUCTION
# =========================================================
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
