#from django.contrib import admin

#from .models import TenantProfile


#admin.site.register(TenantProfile)

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
    search_fields = ("tenant_name", "email", "phone_number")
    list_filter = ("prefecture", "city")
