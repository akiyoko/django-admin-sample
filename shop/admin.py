import csv

from django import forms
from django.contrib import admin
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html
from import_export import resources

from .models import Author, Book, BookStock, PublishedBook, Publisher, \
    UnpublishedBook


class BookInline(admin.TabularInline):
    # ForeignKey を持っている側（多側）のモデルをインラインにする
    model = Book


class BookStockInline(admin.TabularInline):
    # OneToOneField を持っているモデルもインラインOK
    model = BookStock


class BookAdminForm(forms.ModelForm):
    def clean_title(self):
        value = self.cleaned_data['title']
        if 'Java' in value:
            raise forms.ValidationError(
                "タイトルには「Java」を含めないでください。")
        return value

    def clean(self):
        title = self.cleaned_data.get('title')
        price = self.cleaned_data.get('price')
        if title and '薄い本' in title and price and price > 3000:
            raise forms.ValidationError(
                "薄い本は3,000円を超えてはいけません。")


class BookResource(resources.ModelResource):
    class Meta:
        model = Book


# class BookAdmin(ExportActionMixin, admin.ModelAdmin):
class BookAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'format_price', 'size', 'publish_date')
    list_display_links = ('id', 'title')
    # list_select_related = ('publisher',)
    ordering = ('id',)
    search_fields = ('title', 'price', 'publish_date')
    list_per_page = 10
    list_max_show_all = 1000
    # date_hierarchy = 'publish_date'
    # list_editable = ('publish_date',)
    resource_class = BookResource
    # empty_value_display = '(なし)'
    # autocomplete_fields = ('publisher',)

    # fields = (
    #     'id', 'title', 'price', 'size', 'publish_date', 'created_by', 'created_at',
    # )
    # exclude = ('publisher',)
    # readonly_fields = ('id', 'created_by', 'created_at')
    form = BookAdminForm

    # radio_fields = {'size': admin.HORIZONTAL}
    # formfield_overrides = {
    #     models.CharField: {'widget': TextInput(attrs={'size': '80'})},
    #     models.TextField: {
    #         'widget': Textarea(attrs={'cols': '80', 'rows': '10'}),
    #     }
    # }

    class PriceListFilter(admin.SimpleListFilter):
        """価格で絞り込むためのフィルタクラス"""

        title = '価格'
        # クエリ文字列のキー名
        parameter_name = 'prices'

        def lookups(self, request, model_admin):
            """クエリ文字列として使用する値と表示ラベルのペアを定義"""
            return (
                (',1000', '1,000円未満'),
                ('1000,2000', '1,000円以上 2,000円未満'),
                ('2000,', '2,000円以上'),
            )

        def queryset(self, request, queryset):
            # 絞り込み条件が指定されていない場合は検索条件は変更しない
            if self.value() is None:
                return queryset
            # 値をカンマで分割して、0番目を検索の下限値、1番目を上限値とする
            prices = self.value().split(',')
            if prices[0]:
                # 下限値「以上」の検索条件を付加
                queryset = queryset.filter(price__gte=prices[0])
            if prices[1]:
                # 上限値「未満」の検索条件を付加
                queryset = queryset.filter(price__lt=prices[1])
            return queryset

    list_filter = ('size', PriceListFilter)
    # list_filter = ('size', 'price')

    # inlines = [
    #     BookStockInline,
    # ]
    # prepopulated_fields = {'description': ('title', 'publish_date', )}

    class Media:
        css = {
            'all': (
                'admin/css/changelists_book.css',
                # 'admin/css/forms_book.css',
            )
        }
        # js = ('custom_code.js',)

    # def get_queryset(self, request):
    #     queryset = super().get_queryset(request)
    #     return queryset.filter(created_by=request.user)

    def save_model(self, request, obj, form, change):
        """モデル保存前に処理を追加する"""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    # def has_add_permission(self, request):
    #     # ログインユーザーのメールアドレスのドメインが「example.com」の場合に True
    #     return request.user.email.rpartition('@')[2] == 'example.com'
    #
    # def has_change_permission(self, request, obj=None):
    #     has_perm = super().has_change_permission(request, obj)
    #     # モデル変更画面表示時および変更実行時以外では obj の値は None
    #     if obj is None:
    #         return has_perm
    #     else:
    #         return has_perm and obj.created_by == request.user
    #
    # def has_delete_permission(self, request, obj=None):
    #     return False

    # def has_view_permission(self, request, obj=None):
    #     return True

    # def has_module_permission(self, request):
    #     return request.user.is_superuser or getattr(request.user, 'email', None)

    # actions = ['download_as_various_formats']
    actions = ['download_as_csv', 'publish_today']

    def download_as_various_formats(self, request, queryset):
        return super().export_admin_action(request, queryset)

    download_as_various_formats.short_description = 'データエクスポート'

    def download_as_csv(self, request, queryset):
        """選択されたレコードのCSVダウンロードをおこなう"""
        meta = self.model._meta
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)
        field_names = [field.name for field in meta.fields]
        writer.writerow(field_names)
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])
        return response

    download_as_csv.short_description = 'CSVダウンロード'

    def publish_today(self, request, queryset):
        """選択されたレコードの出版日を今日に更新する"""
        queryset.update(publish_date=timezone.localdate())

    publish_today.short_description = '出版日を今日に更新'
    publish_today.allowed_permissions = ('change',)

    def format_price(self, obj):
        """価格のフォーマットを変更する"""
        if obj.price is not None:
            return '{:,d} 円'.format(obj.price)

    format_price.short_description = '価格'
    format_price.admin_order_field = 'price'

    def format_publisher_name(self, obj):
        """出版社のフォーマットを変更する"""
        if obj.publisher is not None:
            return obj.publisher.name
            # return format_html(
            #     '<a href="{}">{}</a>',
            #     reverse('admin:shop_publisher_change', args=[obj.publisher.id]),
            #     obj.publisher.name,
            # )

    format_publisher_name.short_description = '出版社'
    format_publisher_name.admin_order_field = 'publisher__name'

    def format_publish_date(self, obj):
        """出版日のフォーマットを変更する"""
        if obj.publish_date is not None:
            return obj.publish_date.strftime('%Y/%m/%d')

    format_publish_date.short_description = '出版日'
    format_publish_date.admin_order_field = 'publish_date'

    def format_image(self, obj):
        """画像をHTMLで修飾する"""
        if obj.image:
            return format_html('<img src="{}" width="100" />', obj.image.url)

    format_image.short_description = '画像'
    format_image.empty_value_display = 'No image'

    # def format_created_by(self, obj):
    #     """登録ユーザーのフォーマットを変更する"""
    #     if obj.created_by:
    #         return format_html(
    #             '<a href="{}">{}</a>',
    #             reverse('admin:auth_user_change', args=[obj.created_by.id]),
    #             obj.created_by.username,
    #         )
    #     return getattr(self.format_created_by, 'empty_value_display',
    #                    self.get_empty_value_display())
    #
    # format_created_by.short_description = '登録ユーザー'


class PublisherAdmin(admin.ModelAdmin):
    search_fields = ('name',)

    inlines = [
        BookInline,
    ]


class PublishedBookAdmin(BookAdmin):
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # 出版日が今日以前になっているレコードのみを対象とする
        return queryset.filter(publish_date__lte=timezone.localdate())


class UnpublishedBookAdmin(BookAdmin):
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # 出版日が未来または未設定になっているレコードのみを対象とする
        return queryset.filter(
            Q(publish_date__gt=timezone.localdate()) |
            Q(publish_date__isnull=True)
        )


admin.site.register(Book, BookAdmin)
admin.site.register(PublishedBook, PublishedBookAdmin)
admin.site.register(UnpublishedBook, UnpublishedBookAdmin)
admin.site.register(Author)
# admin.site.register(BookStock)
admin.site.register(Publisher, PublisherAdmin)
