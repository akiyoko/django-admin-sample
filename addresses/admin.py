from django.contrib import admin

from .models import Address


class AddressAdmin(admin.ModelAdmin):
    ###############################
    # モデル一覧画面のカスタマイズ
    ###############################
    list_display = (
        'postal_code', 'prefecture', 'city', 'section', 'local_goverment_code',
    )
    search_fields = (
        'local_goverment_code', 'postal_code', 'prefecture', 'city', 'section',
    )
    ordering = ('postal_code', 'id',)
    list_filter = (
        'has_multiple_postal_codes', 'has_banchi', 'has_chome', 'has_multiple_sections',
        'update_status', 'update_reason',
    )


admin.site.register(Address, AddressAdmin)
