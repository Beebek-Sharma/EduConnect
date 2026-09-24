import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SITE_ID = 1
AUTH_USER_MODEL = "api.CustomUser"

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "django-insecure-development-only-change-me")
DEBUG = os.environ.get("DJANGO_DEBUG", "True").lower() == "true"
IS_PRODUCTION = os.environ.get("DJANGO_ENV") == "production"
ALLOWED_HOSTS = [h.strip() for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if h.strip()]

INSTALLED_APPS = [
    "django.contrib.admin", "django.contrib.sites", "django.contrib.auth",
    "django.contrib.contenttypes", "django.contrib.sessions", "django.contrib.messages",
    "django.contrib.staticfiles", "rest_framework", "rest_framework.authtoken",
    "rest_framework_simplejwt", "rest_framework_simplejwt.token_blacklist", "corsheaders",
    "dj_rest_auth", "dj_rest_auth.registration", "allauth", "allauth.account",
    "allauth.socialaccount", "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.linkedin_oauth2", "api.apps.ApiConfig",
]

GROK_API_KEY = os.environ.get("GROK_API_KEY")
GROK_API_ENDPOINT = os.environ.get("GROK_API_ENDPOINT", "https://api.openai.com/v1/chat/completions")
GROK_MODEL_NAME = os.environ.get("GROK_MODEL_NAME", "grok-1")

ACCOUNT_LOGIN_METHODS = {"username", "email"}
SIGNUP_FIELDS = {
    "username": {"required": True}, "email": {"required": True},
    "password1": {"required": True}, "password2": {"required": True},
}
ACCOUNT_EMAIL_VERIFICATION = "optional"
REST_USE_JWT = True
JWT_AUTH_COOKIE = "access_token"
JWT_AUTH_REFRESH_COOKIE = "refresh_token"
REST_AUTH_SERIALIZERS = {"USER_DETAILS_SERIALIZER": "api.serializers.UserSerializer"}
SOCIALACCOUNT_PROVIDERS = {
    "google": {"SCOPE": ["profile", "email"], "AUTH_PARAMS": {"access_type": "online"}},
    "linkedin_oauth2": {"SCOPE": ["r_liteprofile", "r_emailaddress"], "PROFILE_FIELDS": ["id", "first-name", "last-name", "email-address"]},
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware", "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware", "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware", "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware", "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "backend.urls"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [], "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request", "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
    ]},
}]
WSGI_APPLICATION = "backend.wsgi.application"

# Local development keeps the existing SQLite database. Cloudflare Workers
# switches to the SQLite-compatible D1 backend through django-cf.
if os.environ.get("CLOUDFLARE_D1") == "1":
    DATABASES = {
        "default": {
            "ENGINE": "django_cf.db.backends.d1",
            "CLOUDFLARE_BINDING": "DB",
        }
    }
else:
    DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "True").lower() == "true"
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER or "webmaster@localhost")
if DEBUG and not IS_PRODUCTION:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "api.authentication.JWTCookieAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticatedOrReadOnly",),
}

CORS_ALLOW_ALL_ORIGINS = not IS_PRODUCTION
CORS_ALLOWED_ORIGINS = [o.strip() for o in os.environ.get("CORS_ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",") if o.strip()]
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = [o.strip() for o in os.environ.get("CSRF_TRUSTED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",") if o.strip()]
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SECURE = IS_PRODUCTION
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SECURE = IS_PRODUCTION

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "JTI_CLAIM": "jti",
}

JWT_AUTH_COOKIE = "access_token"
JWT_AUTH_REFRESH_COOKIE = "refresh_token"
JWT_AUTH_HTTPONLY = True
JWT_AUTH_SECURE = IS_PRODUCTION
JWT_AUTH_SAMESITE = "Lax"
JWT_AUTH_DOMAIN = None

FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:5173")
LOGIN_REDIRECT_URL = FRONTEND_URL

if IS_PRODUCTION:
    try:
        from .production_settings import *
    except ImportError:
        pass
