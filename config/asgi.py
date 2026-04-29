"""ASGIサーバーからDjangoを起動するためのファイルです。"""

import os

from django.core.asgi import get_asgi_application

# DJANGO_SETTINGS_MODULEは、Djangoが読み込む設定ファイルの場所を表します。
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# applicationは、ASGIサーバーがDjangoアプリを呼び出すための変数です。
application = get_asgi_application()
