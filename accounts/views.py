"""accountsアプリで使う画面表示の処理を書きます。"""

from django.shortcuts import render


def top(request):
    """トップページを表示します。"""
    # requestは、ブラウザから送られてきたアクセス情報を表す変数です。
    # template_nameは、表示するHTMLテンプレートの場所を表す変数です。
    template_name = "accounts/top.html"

    return render(request, template_name)
