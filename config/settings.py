"""Djangoプロジェクト全体の設定ファイルです。"""

from pathlib import Path

# BASE_DIRは、このプロジェクトの一番上のフォルダを表す変数です。
BASE_DIR = Path(__file__).resolve().parent.parent

# SECRET_KEYは、Djangoが暗号署名などに使う秘密の文字列です。
SECRET_KEY = "django-insecure-resident-management-system-dev-key"

# DEBUGは、開発中のエラー詳細表示を有効にするかどうかを表す変数です。
DEBUG = True

# ALLOWED_HOSTSは、このDjangoアプリにアクセスを許可するホスト名の一覧です。
ALLOWED_HOSTS = []

# INSTALLED_APPSは、このプロジェクトで使うDjangoアプリの一覧です。
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "accounts",
]

# MIDDLEWAREは、リクエストとレスポンスの間で共通処理を行う仕組みの一覧です。
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ROOT_URLCONFは、最初に読み込むURL設定ファイルの場所を表す変数です。
ROOT_URLCONF = "config.urls"

# TEMPLATESは、HTMLテンプレートをDjangoが探す場所や使い方の設定です。
TEMPLATES = [
    {
        # BACKENDは、Django標準のテンプレートエンジンを使うことを表します。
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # DIRSは、プロジェクト共通のtemplatesフォルダの場所を表す変数です。
        "DIRS": [BASE_DIR / "templates"],
        # APP_DIRSは、各アプリ内のtemplatesフォルダも探すかどうかを表します。
        "APP_DIRS": True,
        # OPTIONSは、テンプレート内で使える共通情報などの設定です。
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# WSGI_APPLICATIONは、WSGIサーバーが読み込むアプリケーションの場所を表す変数です。
WSGI_APPLICATION = "config.wsgi.application"

# DATABASESは、Djangoが使うデータベースの設定です。
DATABASES = {
    "default": {
        # ENGINEは、使用するデータベースの種類を表します。
        "ENGINE": "django.db.backends.sqlite3",
        # NAMEは、SQLiteデータベースファイルの保存場所を表します。
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# AUTH_PASSWORD_VALIDATORSは、パスワードの安全性チェック設定です。
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

# LANGUAGE_CODEは、このプロジェクトで使う言語を表す変数です。
LANGUAGE_CODE = "ja"

# TIME_ZONEは、このプロジェクトで使うタイムゾーンを表す変数です。
TIME_ZONE = "Asia/Tokyo"

# USE_I18Nは、Djangoの翻訳機能を有効にするかどうかを表す変数です。
USE_I18N = True

# USE_TZは、タイムゾーンを考慮した日時を使うかどうかを表す変数です。
USE_TZ = True

# STATIC_URLは、CSSやJavaScriptなどの静的ファイルを配信するときのURLです。
STATIC_URL = "static/"

# DEFAULT_AUTO_FIELDは、モデル作成時に自動追加される主キーの型を表す変数です。
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
