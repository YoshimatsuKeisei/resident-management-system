"""accountsアプリ内のURL設定ファイルです。"""

from django.urls import path

from . import views

# app_nameは、URLに名前を付けるときのグループ名です。
app_name = "accounts"

# urlpatternsは、URLと処理内容の対応表です。
urlpatterns = [
    # 空文字のURLは、プロジェクト側でつながれたトップページを表示します。
    path("", views.top, name="top"),
    # signup/は、新規登録ページを表示するURLです。
    path("signup/", views.signup, name="signup"),
    # password-reset/は、パスワード変更ページを表示するURLです。
    path("password-reset/", views.password_reset, name="password_reset"),
    # mypage/は、ログイン後に入居者が使うマイページ画面を表示するURLです。
    path("mypage/", views.mypage, name="mypage"),
    # management/tenants/は、管理者用の入居者一覧ページを表示するURLです。
    path("management/tenants/", views.tenant_list, name="tenant_list"),
    # management/login-histories/は、管理者用のログイン履歴一覧ページを表示するURLです。
    path(
        "management/login-histories/",
        views.login_history_list,
        name="login_history_list",
    ),
]
