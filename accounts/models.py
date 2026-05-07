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

    def __str__(self):
        return self.tenant_name
