from django.contrib import admin

from .models import TenantProfile


@admin.register(TenantProfile)
class TenantProfileAdmin(admin.ModelAdmin):
    list_display = (
        "tenant_name",
        "email",
        "phone_number",
        "prefecture",
        "city",
        "birth_date",
        "created_at",
    )
    # password_hashは管理画面で表示・編集しないようにします。
    exclude = ("password_hash",)
    search_fields = ("tenant_name", "email", "phone_number")
    list_filter = ("prefecture", "city")
