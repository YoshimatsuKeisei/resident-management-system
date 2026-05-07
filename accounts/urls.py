"""accountsアプリ内のURL設定ファイルです。"""

from django.urls import path

from . import views

# app_nameは、URLに名前を付けるときのグループ名を表す変数です。
app_name = "accounts"

# urlpatternsは、accountsアプリ内のURLと処理内容の対応表を表す変数です。
urlpatterns = [
    # 空文字のURLは、プロジェクト側でつながれたトップページ「/」を表します。
    path("", views.top, name="top"),
    # signup/は、新規登録ページを表示するURLです。
    path("signup/", views.signup, name="signup"),
    # management/tenants/は、管理者用の入居者一覧ページを表示するURLです。
    path("management/tenants/", views.tenant_list, name="tenant_list"),
]
