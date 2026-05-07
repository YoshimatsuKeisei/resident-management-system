from django.contrib import admin

from .models import LoginHistory, LoginSession, TenantProfile


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


@admin.register(LoginSession)
class LoginSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "tenant", "created_at")


@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = ("id", "login_session", "tenant", "event_type", "occurred_at")
    list_filter = ("event_type",)
