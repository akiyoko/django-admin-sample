from django.contrib import admin

from .models import Address


class AddressAdmin(admin.ModelAdmin):
    ###############################
    # モデル一覧画面のカスタマイズ
    ###############################
    list_display = (
        'postal_code', 'prefecture', 'city', 'town_area', 'local_goverment_code',
    )
    search_fields = (
        'local_goverment_code', 'postal_code', 'prefecture', 'city', 'town_area',
    )
    ordering = ('postal_code', 'id',)
    list_filter = (
        'is_one_town_by_multi_postal_code', 'is_need_small_area_address',
        'is_chome', 'is_multi_town_by_one_postal_code',
    )


admin.site.register(Address, AddressAdmin)
