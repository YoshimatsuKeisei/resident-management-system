"""accountsアプリで使う画面表示の処理を書きます。"""

import re
from datetime import date

from django.contrib.auth.hashers import make_password
from django.shortcuts import render

from .models import TenantProfile


def top(request):
    """トップページを表示します。"""
    # requestは、ブラウザから送られてきたアクセス情報を表す変数です。
    # template_nameは、表示するHTMLテンプレートの場所を表す変数です。
    template_name = "accounts/top.html"

    return render(request, template_name)


def signup(request):
    """新規登録ページの表示と、入力内容の保存を行います。"""
    # requestは、ブラウザから送られてきたアクセス情報を表す変数です。
    # template_nameは、表示するHTMLテンプレートの場所を表す変数です。
    template_name = "accounts/signup.html"
    context = {}

    if request.method == "POST":
        # request.POSTには、HTMLフォームから送られてきた入力値が入っています。
        tenant_name = request.POST.get("tenant_name", "").strip()
        email = request.POST.get("email", "").strip()
        phone_number = request.POST.get("phone_number", "").strip()
        postal_code = request.POST.get("postal_code", "").strip()
        prefecture = request.POST.get("prefecture", "").strip()
        city = request.POST.get("city", "").strip()
        street_address = request.POST.get("street_address", "").strip()
        building_name = request.POST.get("building_name", "").strip()
        birth_date_text = request.POST.get("birth_date", "").strip()
        password = request.POST.get("password", "")
        password_confirm = request.POST.get("password_confirm", "")

        # building_nameは任意なので、必須チェックには含めません。
        required_values = [
            tenant_name,
            email,
            phone_number,
            postal_code,
            prefecture,
            city,
            street_address,
            birth_date_text,
            password,
            password_confirm,
        ]

        if any(value == "" for value in required_values):
            context["error_message"] = "入力していない項目があります。"
            return render(request, template_name, context)

        # パスワードはサーバー側でも半角英数字だけか確認します。
        if not re.fullmatch(r"[A-Za-z0-9]+", password):
            context["error_message"] = "パスワードの形式が違います。半角英数字のみの入力です。"
            return render(request, template_name, context)

        # 確認用パスワードも半角英数字だけか確認します。
        if not re.fullmatch(r"[A-Za-z0-9]+", password_confirm):
            context["error_message"] = "パスワード確認の形式が違います。半角英数字のみの入力です。"
            return render(request, template_name, context)

        # 入力したパスワードと確認用パスワードが同じか確認します。
        if password != password_confirm:
            context["error_message"] = "パスワードが一致しません。"
            return render(request, template_name, context)

        try:
            # DateFieldに保存できるように、YYYY-MM-DD形式の文字列を日付に変換します。
            birth_date = date.fromisoformat(birth_date_text)
        except ValueError:
            context["error_message"] = "生年月日はYYYY-MM-DD形式で入力してください。"
            return render(request, template_name, context)

        # TenantProfileモデルのフィールド名に合わせて、入力値をDBに保存します。
        TenantProfile.objects.create(
            tenant_name=tenant_name,
            email=email,
            phone_number=phone_number,
            postal_code=postal_code,
            prefecture=prefecture,
            city=city,
            street_address=street_address,
            building_name=building_name,
            birth_date=birth_date,
            # 平文パスワードは保存せず、make_passwordで作ったハッシュだけを保存します。
            password_hash=make_password(password),
        )

        context["success_message"] = "登録が完了しました。"

    return render(request, template_name, context)


def tenant_list(request):
    """管理者用の入居者一覧ページを表示します。"""
    # DBに保存されている入居者データを、登録日時が新しい順に取得します。
    tenants = TenantProfile.objects.all().order_by("-created_at")

    # contextに入れたデータは、HTMLテンプレート側で使えるようになります。
    context = {
        "tenants": tenants,
    }

    return render(request, "accounts/tenant_list.html", context)
