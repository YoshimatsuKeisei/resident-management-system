"""プロジェクト全体のURL設定ファイルです。"""

from django.contrib import admin
from django.urls import include, path

# urlpatternsは、URLと処理内容の対応表を表す変数です。
urlpatterns = [
    # admin/は、Django管理画面のURLです。
    path("admin/", admin.site.urls),
    # 空文字のURLは、トップページ「/」を表します。
    path("", include("accounts.urls")),
]
