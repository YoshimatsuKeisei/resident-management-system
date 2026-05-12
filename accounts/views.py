"""accountsアプリで使う画面表示とフォーム処理を書きます。"""

import json
import re
from datetime import date, time

from django.contrib.auth.hashers import check_password, make_password
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from .models import (
    EmergencyContact,
    LoginHistory,
    LoginSession,
    TenantNotice,
    TenantPhoneNumber,
    TenantProfile,
)


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


def is_phone_number(value):
    return bool(re.fullmatch(r"^0\d{1,4}-?\d{1,4}-?\d{3,4}$", value))


def get_logged_in_tenant(request):
    tenant_id = request.session.get("tenant_id")
    if tenant_id is None:
        return None
    return TenantProfile.objects.filter(id=tenant_id).first()


def json_success(message, **extra):
    data = {"success": True, "message": message}
    data.update(extra)
    return JsonResponse(data)


def json_error(message):
    return JsonResponse({"success": False, "message": message})


def get_json_body(request):
    try:
        return json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return {}


def create_tenant_log(request, tenant, event_type, remarks=""):
    login_session_id = request.session.get("login_session_id")
    login_session = LoginSession.objects.filter(id=login_session_id, tenant=tenant).first()
    if login_session is None:
        login_session = LoginSession.objects.create(tenant=tenant)
        request.session["login_session_id"] = login_session.id

    # TODO: 将来的にLoginHistoryではなくActivityLog / TenantActionLogのような操作履歴モデルへ整理する。
    # TODO: 操作履歴の改ざん防止を考慮し、必要に応じてIPアドレスやUser-Agentも保存する。
    return LoginHistory.objects.create(
        login_session=login_session,
        tenant=tenant,
        event_type=event_type,
        remarks=remarks,
    )


def format_phone_numbers_for_log(phone_numbers):
    return ",".join(phone_numbers) if phone_numbers else "なし"


def format_emergency_contacts_for_log(contacts):
    formatted_contacts = []
    for contact in contacts:
        contact_name = contact.get("contact_name") or "氏名未設定"
        relationship = contact.get("relationship") or "続柄未設定"
        phone_number = contact.get("phone_number") or "電話番号未設定"
        formatted_contacts.append(f"{contact_name}-{relationship}-{phone_number}")
    return ",".join(formatted_contacts) if formatted_contacts else "なし"


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

    # マイページ内の「ログイン履歴」画面で使うため、ログイン中の入居者の履歴だけ取得します。
    # セッションIDや入居者IDは画面に出さず、日時とログの種類だけを表示します。
    login_histories = LoginHistory.objects.filter(tenant=tenant).order_by("-occurred_at")

    tenant_notices = TenantNotice.objects.filter(
        recipient_tenant=tenant,
        is_trash=False,
    ).order_by("-created_at")
    notices = [
        {
            "id": f"db-{notice.id}",
            "title": notice.subject,
            "senderCompany": notice.sender_company,
            "dateTime": timezone.localtime(notice.created_at).strftime("%Y-%m-%d %H:%M"),
            "body": notice.body,
            "isUnread": notice.is_unread,
            "isStarred": notice.is_starred,
            "isTrash": notice.is_trash,
        }
        for notice in tenant_notices
    ]
    phone_numbers = list(
        tenant.phone_numbers.all().order_by("-is_primary", "created_at").values_list(
            "phone_number",
            flat=True,
        )
    )
    if not phone_numbers and tenant.phone_number:
        phone_numbers = [tenant.phone_number]
    emergency_contacts = [
        {
            "contact_name": contact.contact_name,
            "phone_number": contact.phone_number,
            "relationship": contact.relationship,
        }
        for contact in tenant.emergency_contacts.all().order_by("created_at")
    ]

    context = {
        "tenant": tenant,
        "login_histories": login_histories,
        "notices": notices,
        "phone_numbers": phone_numbers,
        "emergency_contacts": emergency_contacts,
        "callable_start_hour": tenant.callable_start_time.hour if tenant.callable_start_time else "",
        "callable_end_hour": tenant.callable_end_time.hour if tenant.callable_end_time else "",
    }

    return render(request, "accounts/mypage.html", context)


def update_email(request):
    tenant = get_logged_in_tenant(request)
    if tenant is None:
        return json_error("ログイン情報を確認できません。")

    new_email = request.POST.get("new_email", "").strip()
    if new_email == "":
        return json_error("メールアドレスを入力してください。")
    if not re.fullmatch(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", new_email):
        return json_error("メールアドレスの形式が正しくありません。")
    if TenantProfile.objects.exclude(id=tenant.id).filter(email=new_email).exists():
        return json_error("このメールアドレスは使用できません。")

    # TODO: メールアドレス変更時に確認メールを送る。
    old_email = tenant.email
    tenant.email = new_email
    tenant.save(update_fields=["email", "updated_at"])
    create_tenant_log(request, tenant, LoginHistory.EVENT_TYPE_MAIL, f"{old_email}\u2192{new_email}")
    return json_success("メールアドレスを変更しました。", email=new_email)


def update_phone_numbers(request):
    tenant = get_logged_in_tenant(request)
    if tenant is None:
        return json_error("ログイン情報を確認できません。")

    phone_numbers = [
        str(value).strip()
        for value in get_json_body(request).get("phone_numbers", [])
        if str(value).strip() != ""
    ]
    if not phone_numbers:
        return json_error("必ず1個以上電話番号を登録してください。")
    if any(not is_phone_number(value) for value in phone_numbers):
        return json_error("電話番号の形式が正しくありません。")
    if len(phone_numbers) != len(set(phone_numbers)):
        return json_error("同じ電話番号が入力されています。")

    other_profile_exists = TenantProfile.objects.exclude(id=tenant.id).filter(
        phone_number__in=phone_numbers
    ).exists()
    other_phone_exists = TenantPhoneNumber.objects.exclude(tenant=tenant).filter(
        phone_number__in=phone_numbers
    ).exists()
    if other_profile_exists or other_phone_exists:
        return json_error("この電話番号は使用できません。")

    # TODO: 電話番号変更時にSMS認証を行う。
    old_phone_numbers = list(
        tenant.phone_numbers.all().order_by("-is_primary", "created_at").values_list(
            "phone_number",
            flat=True,
        )
    )
    if not old_phone_numbers and tenant.phone_number:
        old_phone_numbers = [tenant.phone_number]

    TenantPhoneNumber.objects.filter(tenant=tenant).delete()
    for index, phone_number in enumerate(phone_numbers):
        TenantPhoneNumber.objects.create(
            tenant=tenant,
            phone_number=phone_number,
            is_primary=index == 0,
        )
    tenant.phone_number = phone_numbers[0]
    tenant.save(update_fields=["phone_number", "updated_at"])
    create_tenant_log(
        request,
        tenant,
        LoginHistory.EVENT_TYPE_TEL,
        f"{format_phone_numbers_for_log(old_phone_numbers)}\u2192{format_phone_numbers_for_log(phone_numbers)}",
    )
    return json_success("電話番号を変更しました。", phone_numbers=phone_numbers)


def update_password_from_mypage(request):
    tenant = get_logged_in_tenant(request)
    if tenant is None:
        return json_error("ログイン情報を確認できません。")

    current_password = request.POST.get("current_password", "")
    new_password = request.POST.get("new_password", "")
    new_password_confirm = request.POST.get("new_password_confirm", "")

    if current_password == "" or new_password == "" or new_password_confirm == "":
        return json_error("入力していない項目があります。")
    if not check_password(current_password, tenant.password_hash):
        return json_error("現在のパスワードが正しくありません。")
    if not is_alnum_password(new_password):
        return json_error("形式が違います。半角英数字のみの入力です。")
    if new_password != new_password_confirm:
        return json_error("パスワードが一致しません。")
    if current_password == new_password:
        return json_error("現在のパスワードと同じものは使用できません。")

    tenant.password_hash = make_password(new_password)
    tenant.save(update_fields=["password_hash", "updated_at"])
    create_tenant_log(request, tenant, LoginHistory.EVENT_TYPE_PASS, "\u30d1\u30b9\u30ef\u30fc\u30c9\u304c\u5909\u66f4\u3055\u308c\u307e\u3057\u305f")
    return json_success("パスワードを変更しました。")


def update_contact_methods(request):
    tenant = get_logged_in_tenant(request)
    if tenant is None:
        return json_error("ログイン情報を確認できません。")

    data = get_json_body(request)
    contact_by_phone = bool(data.get("contact_by_phone"))
    contact_by_app = bool(data.get("contact_by_app"))
    contact_by_email = bool(data.get("contact_by_email"))
    contact_by_sms = bool(data.get("contact_by_sms"))

    if not any([contact_by_phone, contact_by_app, contact_by_email, contact_by_sms]):
        return json_error("少なくとも1つはオンにしてください。")

    # TODO: 連絡設定変更履歴を保存する。
    tenant.contact_by_phone = contact_by_phone
    tenant.contact_by_app = contact_by_app
    tenant.contact_by_email = contact_by_email
    tenant.contact_by_sms = contact_by_sms
    tenant.save(
        update_fields=[
            "contact_by_phone",
            "contact_by_app",
            "contact_by_email",
            "contact_by_sms",
            "updated_at",
        ]
    )
    return json_success("希望連絡方法を変更しました。")


def update_callable_time(request):
    tenant = get_logged_in_tenant(request)
    if tenant is None:
        return json_error("ログイン情報を確認できません。")

    start_value = request.POST.get("callable_start_time", "").strip()
    end_value = request.POST.get("callable_end_time", "").strip()

    if (start_value == "") != (end_value == ""):
        return json_error("開始時間と終了時間を両方選択してください。")

    if start_value == "" and end_value == "":
        tenant.callable_start_time = None
        tenant.callable_end_time = None
    else:
        try:
            start_hour = int(start_value)
            end_hour = int(end_value)
            start_time = time(hour=start_hour)
            end_time = time(hour=end_hour)
        except ValueError:
            return json_error("電話可能時間帯の形式が正しくありません。")
        if end_time <= start_time:
            return json_error("終了時間は開始時間より後にしてください。")
        tenant.callable_start_time = start_time
        tenant.callable_end_time = end_time

    tenant.save(update_fields=["callable_start_time", "callable_end_time", "updated_at"])
    return json_success(
        "電話可能時間帯を変更しました。",
        callable_start_time=start_value,
        callable_end_time=end_value,
    )


def update_emergency_contacts(request):
    tenant = get_logged_in_tenant(request)
    if tenant is None:
        return json_error("ログイン情報を確認できません。")

    contacts = []
    for raw_contact in get_json_body(request).get("emergency_contacts", []):
        contact_name = str(raw_contact.get("contact_name", "")).strip()
        phone_number = str(raw_contact.get("phone_number", "")).strip()
        relationship = str(raw_contact.get("relationship", "")).strip()
        if contact_name == "" and phone_number == "" and relationship == "":
            continue
        if phone_number == "" or not is_phone_number(phone_number):
            return json_error("電話番号の形式が正しくありません。")
        contacts.append(
            {
                "contact_name": contact_name,
                "phone_number": phone_number,
                "relationship": relationship,
            }
        )

    old_contacts = [
        {
            "contact_name": contact.contact_name,
            "phone_number": contact.phone_number,
            "relationship": contact.relationship,
        }
        for contact in EmergencyContact.objects.filter(tenant=tenant).order_by("created_at")
    ]

    EmergencyContact.objects.filter(tenant=tenant).delete()
    for contact in contacts:
        EmergencyContact.objects.create(tenant=tenant, **contact)
    create_tenant_log(
        request,
        tenant,
        LoginHistory.EVENT_TYPE_EMERGENCY,
        f"{format_emergency_contacts_for_log(old_contacts)}\u2192{format_emergency_contacts_for_log(contacts)}",
    )
    # TODO: ???????????????????????????????
    return json_success("緊急連絡先を変更しました。", emergency_contacts=contacts)


def company_message(request):
    """不動産会社側の簡易メッセージ送信画面を表示し、入居者向けお知らせを保存します。"""
    tenants = TenantProfile.objects.all().order_by("tenant_name", "id")
    context = {
        "tenants": tenants,
        "target_filter_type": "all",
        "selected_tenant_id": "",
        "subject": "",
        "body": "",
    }

    if request.method == "POST":
        target_filter_type = request.POST.get("target_filter_type", "all")
        selected_tenant_id = request.POST.get("selected_tenant_id", "").strip()
        subject = request.POST.get("subject", "").strip()
        body = request.POST.get("body", "").strip()

        context.update(
            {
                "target_filter_type": target_filter_type,
                "selected_tenant_id": selected_tenant_id,
                "subject": subject,
                "body": body,
            }
        )

        if subject == "":
            context["error_message"] = "件名を入力してください。"
            return render(request, "accounts/company_message.html", context)

        if body == "":
            context["error_message"] = "メッセージ本文を入力してください。"
            return render(request, "accounts/company_message.html", context)

        if target_filter_type == "personal" and selected_tenant_id == "":
            context["error_message"] = "送信先の入居者を選択してください。"
            return render(request, "accounts/company_message.html", context)

        if target_filter_type == "personal":
            selected_tenant = TenantProfile.objects.filter(id=selected_tenant_id).first()
            recipients = [selected_tenant] if selected_tenant is not None else []
            if not recipients:
                context["error_message"] = "送信先の入居者を選択してください。"
                return render(request, "accounts/company_message.html", context)
        else:
            # TODO: 退去予定日が1週間以内、特定アパート、契約更新間近、保証会社確認が必要な入居者などで絞り込む。
            recipients = list(tenants)

        for tenant in recipients:
            TenantNotice.objects.create(
                sender_company="不動産会社",
                recipient_tenant=tenant,
                target_filter_type=target_filter_type,
                subject=subject,
                body=body,
                is_unread=True,
                is_starred=False,
                is_trash=False,
            )

        # TODO: Gmailにもメッセージを送信する。
        # TODO: スマホ通知を送る。
        # TODO: 業者側マイページ、業者ごとの権限制御、送信履歴確認を本格実装する。
        context["success_message"] = "メッセージを送信しました。"
        context["selected_tenant_id"] = ""
        context["subject"] = ""
        context["body"] = ""

    return render(request, "accounts/company_message.html", context)


def tenant_list(request):
    """管理者用の入居者一覧ページを表示します。"""
    # DBに保存されている入居者データを、登録日時が新しい順に取得します。
    tenants = TenantProfile.objects.prefetch_related("emergency_contacts").all().order_by("-created_at")

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
