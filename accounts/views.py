"""accountsアプリで使う画面表示とフォーム処理を書きます。"""

import re
from datetime import date

from django.contrib.auth.hashers import check_password, make_password
from django.db.models import Q
from django.shortcuts import redirect, render

from .models import LoginHistory, LoginSession, TenantProfile


LOGIN_ERROR_MESSAGE = "メールアドレスまたは電話番号、パスワードが異なります。"
REQUIRED_ERROR_MESSAGE = "入力していない項目があります。"
IDENTIFIER_FORMAT_ERROR_MESSAGE = "入力形式が正しくありません。"
PASSWORD_FORMAT_ERROR_MESSAGE = "形式が違います。半角英数字のみの入力です。"
PASSWORD_MISMATCH_ERROR_MESSAGE = "パスワードが一致しません。"
PASSWORD_RESET_SUCCESS_MESSAGE = "パスワード変更を受け付けました。"


def is_email_or_phone(value):
    """メールアドレスまたは電話番号の形になっているかを確認します。"""
    # 登録済みかどうかではなく、入力された文字の形だけを確認します。
    email_pattern = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
    phone_pattern = r"^0\d{1,4}-?\d{1,4}-?\d{3,4}$"
    return bool(re.fullmatch(email_pattern, value) or re.fullmatch(phone_pattern, value))


def is_alnum_password(value):
    """パスワードが半角英数字だけで入力されているかを確認します。"""
    return bool(re.fullmatch(r"[A-Za-z0-9]+", value))


def top(request):
    """トップページの表示と、ログイン判定を行います。"""
    template_name = "accounts/top.html"
    context = {}

    if request.method == "POST":
        # request.POSTには、ログインフォームから送られた入力値が入っています。
        login_identifier = request.POST.get("login_identifier", "").strip()
        password = request.POST.get("password", "")

        # TODO: ログイン失敗を5回繰り返したら30分ロックする処理を追加する。
        # TODO: ログイン成功/失敗をS/Fで記録する処理を追加する。
        # 未登録かパスワード違いかを分けると登録有無が推測できるため、同じ文言にします。
        if (
            login_identifier == ""
            or password == ""
            or not is_email_or_phone(login_identifier)
            or not is_alnum_password(password)
        ):
            context["login_error_message"] = LOGIN_ERROR_MESSAGE
            return render(request, template_name, context)

        # メールアドレスまたは電話番号が一致する入居者データを探します。
        tenant = TenantProfile.objects.filter(
            Q(email=login_identifier) | Q(phone_number=login_identifier)
        ).first()

        # check_passwordは、入力パスワードとDB内のハッシュが合うかを確認します。
        if tenant is None or not check_password(password, tenant.password_hash):
            context["login_error_message"] = LOGIN_ERROR_MESSAGE
        else:
            # ログイン成功1回分をLoginSessionに保存します。
            login_session = LoginSession.objects.create(tenant=tenant)

            # LoginSessionに紐づくINログをLoginHistoryに保存します。
            LoginHistory.objects.create(
                login_session=login_session,
                tenant=tenant,
                event_type=LoginHistory.EVENT_TYPE_IN,
            )

            # 後でログアウト処理でOUTログを残せるように、必要なIDをセッションに保存します。
            request.session["tenant_id"] = tenant.id
            request.session["login_session_id"] = login_session.id

            # ログインに成功した入居者だけが見られるマイページへ移動します。
            return redirect("accounts:mypage")

    return render(request, template_name, context)


def signup(request):
    """新規登録ページの表示と、入力内容の保存を行います。"""
    template_name = "accounts/signup.html"
    context = {}

    if request.method == "POST":
        # request.POSTには、HTMLフォームから送られた入力値が入っています。
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
        if not is_alnum_password(password):
            context["error_message"] = "パスワードの形式が違います。半角英数字のみの入力です。"
            return render(request, template_name, context)

        # 確認用パスワードも半角英数字だけか確認します。
        if not is_alnum_password(password_confirm):
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

        # TODO: 新規登録時に登録済みメールアドレスへ確認メッセージを送る。
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


def password_reset(request):
    """パスワード変更ページの表示と、仮のパスワード変更処理を行います。"""
    template_name = "accounts/password_reset.html"
    context = {}

    if request.method == "POST":
        # フォームから送られた値を取り出します。
        login_identifier = request.POST.get("login_identifier", "").strip()
        new_password = request.POST.get("new_password", "")
        new_password_confirm = request.POST.get("new_password_confirm", "")
        context["login_identifier"] = login_identifier

        if login_identifier == "" or new_password == "" or new_password_confirm == "":
            context["error_message"] = REQUIRED_ERROR_MESSAGE
            return render(request, template_name, context)

        if not is_email_or_phone(login_identifier):
            context["error_message"] = IDENTIFIER_FORMAT_ERROR_MESSAGE
            return render(request, template_name, context)

        if not is_alnum_password(new_password) or not is_alnum_password(new_password_confirm):
            context["error_message"] = PASSWORD_FORMAT_ERROR_MESSAGE
            return render(request, template_name, context)

        if new_password != new_password_confirm:
            context["error_message"] = PASSWORD_MISMATCH_ERROR_MESSAGE
            return render(request, template_name, context)

        # TODO: パスワード変更時に登録済みメールアドレスへ確認メッセージを送る。
        # 形式チェックが通った後だけDBを探します。見つからない場合も画面には同じ成功文を出します。
        tenant = TenantProfile.objects.filter(
            Q(email=login_identifier) | Q(phone_number=login_identifier)
        ).first()

        if tenant is not None:
            # 平文では保存せず、make_passwordでハッシュ化した値だけを保存します。
            tenant.password_hash = make_password(new_password)
            tenant.save(update_fields=["password_hash", "updated_at"])

        context["success_message"] = PASSWORD_RESET_SUCCESS_MESSAGE

    return render(request, template_name, context)


def mypage(request):
    """ログイン後に入居者が見るマイページ画面を表示します。"""
    # セッションにtenant_idがあるかどうかで、ログイン済みかを簡易的に確認します。
    tenant_id = request.session.get("tenant_id")

    if tenant_id is None:
        # 未ログインで直接/mypage/へ来た場合は、トップページへ戻します。
        return redirect("accounts:top")

    # セッションに保存されたIDを使って、ログイン中の入居者情報を取得します。
    tenant = TenantProfile.objects.filter(id=tenant_id).first()

    if tenant is None:
        # セッションにIDがあってもDBに入居者がいない場合は、安全のためトップへ戻します。
        return redirect("accounts:top")

    context = {
        "tenant": tenant,
    }

    return render(request, "accounts/mypage.html", context)


def tenant_list(request):
    """管理者用の入居者一覧ページを表示します。"""
    # DBに保存されている入居者データを、登録日時が新しい順に取得します。
    tenants = TenantProfile.objects.all().order_by("-created_at")

    # contextに入れたデータは、HTMLテンプレート側で使えるようになります。
    context = {
        "tenants": tenants,
    }

    return render(request, "accounts/tenant_list.html", context)


def login_history_list(request):
    """管理者用のログイン履歴一覧ページを表示します。"""
    # DBに保存されているログイン履歴を、発生日時が新しい順に取得します。
    login_histories = LoginHistory.objects.all().order_by("-occurred_at")

    # contextに入れたデータは、HTMLテンプレート側で使えるようになります。
    context = {
        "login_histories": login_histories,
    }

    return render(request, "accounts/login_history_list.html", context)
