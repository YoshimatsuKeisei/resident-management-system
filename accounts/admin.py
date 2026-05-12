from django.contrib import admin

from .models import (
    EmergencyContact,
    LoginHistory,
    LoginSession,
    TenantNotice,
    TenantPhoneNumber,
    TenantProfile,
)


@admin.register(TenantProfile)
class TenantProfileAdmin(admin.ModelAdmin):
    list_display = (
        "tenant_name",
        "email",
        "phone_number",
        "prefecture",
        "city",
        "birth_date",
        "contact_methods_display",
        "callable_time_display",
        "created_at",
    )
    # password_hashは管理画面で表示・編集しないようにします。
    exclude = ("password_hash",)
    search_fields = ("tenant_name", "email", "phone_number")
    list_filter = ("prefecture", "city")

    @admin.display(description="希望連絡方法")
    def contact_methods_display(self, obj):
        methods = []
        if obj.contact_by_phone:
            methods.append("電話")
        if obj.contact_by_app:
            methods.append("アプリ")
        if obj.contact_by_email:
            methods.append("メール")
        if obj.contact_by_sms:
            methods.append("SMS")
        return " / ".join(methods) if methods else "未設定"

    @admin.display(description="電話可能時間帯")
    def callable_time_display(self, obj):
        if obj.callable_start_time and obj.callable_end_time:
            return f"{obj.callable_start_time:%H:%M}〜{obj.callable_end_time:%H:%M}"
        return "未設定"


@admin.register(LoginSession)
class LoginSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "tenant", "created_at")


@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = ("id", "login_session", "tenant", "event_type", "occurred_at")
    list_filter = ("event_type",)


@admin.register(TenantNotice)
class TenantNoticeAdmin(admin.ModelAdmin):
    list_display = (
        "sender_company",
        "recipient_tenant",
        "subject",
        "created_at",
        "is_unread",
        "is_starred",
        "is_trash",
    )
    list_filter = ("sender_company", "target_filter_type", "is_unread", "is_starred", "is_trash")
    search_fields = ("subject", "body", "recipient_tenant__tenant_name")


@admin.register(TenantPhoneNumber)
class TenantPhoneNumberAdmin(admin.ModelAdmin):
    list_display = ("tenant", "phone_number", "is_primary", "created_at")
    list_filter = ("is_primary",)
    search_fields = ("tenant__tenant_name", "phone_number")


@admin.register(EmergencyContact)
class EmergencyContactAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "tenant_id_display",
        "tenant_name_display",
        "contact_name",
        "relationship",
        "phone_number",
    )
    search_fields = ("tenant__tenant_name", "contact_name", "phone_number", "relationship")

    @admin.display(description="緊急連絡先ID")
    def id(self, obj):
        return obj.pk

    @admin.display(description="入居者ID")
    def tenant_id_display(self, obj):
        return obj.tenant.id

    @admin.display(description="入居者名")
    def tenant_name_display(self, obj):
        return str(obj.tenant)
