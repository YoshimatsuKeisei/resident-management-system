"""accountsアプリの設定ファイルです。"""

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """accountsアプリの基本設定をまとめるクラスです。"""

    # default_auto_fieldは、モデル作成時に自動追加される主キーの型を表す変数です。
    default_auto_field = "django.db.models.BigAutoField"
    # nameは、このアプリのPython上の名前を表す変数です。
    name = "accounts"
