#!/usr/bin/env python
"""Djangoの管理コマンドを実行するためのファイルです。"""

import os
import sys


def main():
    """Djangoの管理コマンドを実行します。"""
    # DJANGO_SETTINGS_MODULEは、Djangoが読み込む設定ファイルの場所を表します。
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

    try:
        # execute_from_command_lineは、runserverやmigrateなどのコマンドを実行する関数です。
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Djangoがインストールされていません。仮想環境を有効化して、Djangoをインストールしてください。"
        ) from exc

    # sys.argvは、ターミナルで入力されたコマンドの内容を表す変数です。
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
