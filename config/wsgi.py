"""WSGIサーバーからDjangoを起動するためのファイルです。"""

import os

from django.core.wsgi import get_wsgi_application

# DJANGO_SETTINGS_MODULEは、Djangoが読み込む設定ファイルの場所を表します。
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# applicationは、WSGIサーバーがDjangoアプリを呼び出すための変数です。
application = get_wsgi_application()
