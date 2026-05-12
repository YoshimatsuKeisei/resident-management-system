from django.db import models


class TenantProfile(models.Model):
    # 入居者の名前を保存します。
    tenant_name = models.CharField(max_length=100)

    # 入居者のメールアドレスを保存します。
    email = models.EmailField(max_length=254)

    # 入居者の電話番号を保存します。
    phone_number = models.CharField(max_length=20)

    # 郵便番号を保存します。
    postal_code = models.CharField(max_length=8)

    # 都道府県を保存します。
    prefecture = models.CharField(max_length=20)

    # 市区町村を保存します。
    city = models.CharField(max_length=100)

    # 町名・丁目・番地を保存します。
    street_address = models.CharField(max_length=150)

    # 建物名・部屋番号を保存します。任意入力なので空欄でも保存できます。
    building_name = models.CharField(max_length=150, blank=True)

    # 生年月日を日付として保存します。
    birth_date = models.DateField()

    # パスワードは平文では保存せず、Djangoでハッシュ化した文字列だけを保存します。
    password_hash = models.CharField(max_length=128, default="")

    # データが作成された日時を自動で保存します。
    created_at = models.DateTimeField(auto_now_add=True)

    # データが更新された日時を自動で保存します。
    updated_at = models.DateTimeField(auto_now=True)

    contact_by_phone = models.BooleanField(default=True)
    contact_by_app = models.BooleanField(default=True)
    contact_by_email = models.BooleanField(default=True)
    contact_by_sms = models.BooleanField(default=False)
    callable_start_time = models.TimeField(null=True, blank=True)
    callable_end_time = models.TimeField(null=True, blank=True)

    def __str__(self):
        return self.tenant_name


class LoginSession(models.Model):
    # どの入居者のログイン1回分かを保存します。
    tenant = models.ForeignKey(TenantProfile, on_delete=models.CASCADE)

    # ログインセッションが作られた日時を自動で保存します。
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"LoginSession {self.id}"


class LoginHistory(models.Model):
    # ログインしたことを表す種別です。
    EVENT_TYPE_IN = "IN"

    # 将来ログアウトしたことを表す種別として使います。
    EVENT_TYPE_OUT = "OUT"

    # event_typeに入れられる値をINとOUTだけに制限します。
    EVENT_TYPE_TEL = "TEL"
    EVENT_TYPE_MAIL = "MAIL"
    EVENT_TYPE_PASS = "PASS"
    EVENT_TYPE_EMERGENCY = "EMG"

    EVENT_TYPE_CHOICES = [
        (EVENT_TYPE_IN, "ログイン"),
        (EVENT_TYPE_OUT, "ログアウト"),
        (EVENT_TYPE_TEL, "電話番号"),
        (EVENT_TYPE_MAIL, "メールアドレス"),
        (EVENT_TYPE_PASS, "パスワード"),
        (EVENT_TYPE_EMERGENCY, "緊急連絡先"),
    ]

    # どのログインセッションに紐づく履歴かを保存します。
    login_session = models.ForeignKey(LoginSession, on_delete=models.CASCADE)

    # どの入居者の履歴かを保存します。
    tenant = models.ForeignKey(TenantProfile, on_delete=models.CASCADE)

    # ログインまたはログアウトの種別を保存します。
    event_type = models.CharField(max_length=4, choices=EVENT_TYPE_CHOICES)

    # ログインまたはログアウトが発生した日時を自動で保存します。
    occurred_at = models.DateTimeField(auto_now_add=True)

    remarks = models.TextField(blank=True, default="")

    def __str__(self):
        return f"{self.event_type} {self.id}"


class TenantPhoneNumber(models.Model):
    tenant = models.ForeignKey(
        TenantProfile,
        on_delete=models.CASCADE,
        related_name="phone_numbers",
    )
    phone_number = models.CharField(max_length=20, unique=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # TODO: TenantProfile.phone_numberをTenantPhoneNumberに完全移行する。
    # TODO: 電話番号変更時にSMS認証を行い、連絡設定変更履歴を保存する。

    def __str__(self):
        return self.phone_number


class EmergencyContact(models.Model):
    tenant = models.ForeignKey(
        TenantProfile,
        on_delete=models.CASCADE,
        related_name="emergency_contacts",
    )
    contact_name = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=20)
    relationship = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # TODO: 緊急連絡先に名前・続柄・優先順位をより詳しく設定する。
    # TODO: 設定変更後に確認通知を送る。

    def __str__(self):
        return self.contact_name or self.phone_number


class TenantNotice(models.Model):
    sender_company = models.CharField(max_length=50)
    recipient_tenant = models.ForeignKey(
        TenantProfile,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notices",
    )
    target_filter_type = models.CharField(max_length=50)
    subject = models.CharField(max_length=200)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_unread = models.BooleanField(default=True)
    is_starred = models.BooleanField(default=False)
    is_trash = models.BooleanField(default=False)

    # TODO: 本格運用ではNoticeとNoticeRecipientに分け、本文と入居者ごとの既読・スター・ゴミ箱状態を別管理する。
    # TODO: Gmail送信、スマホ通知、業者側マイページ、権限制御、送信履歴確認に拡張する。
    # TODO: 物件、契約状態、退去予定日、保証会社確認状況などで対象者を絞り込めるようにする。

    def __str__(self):
        return self.subject
