import csv

from django import forms
from django.contrib import admin
from django.db.models import Q
from django.http import HttpResponse
from django.utils import timezone
from django.utils.html import format_html

from .models import Author, Book, Publisher, BookStock


class BookInline(admin.TabularInline):
    # ForeignKey を持っている側（多側）のモデルをインラインにする
    model = Book


class BookStockInline(admin.TabularInline):
    # OneToOne を持っているモデルもインラインOK
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


class BookModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'format_price', 'size', 'publish_date')
    list_display_links = ('id', 'title')
    # list_select_related = ('publisher',)
    ordering = ('id',)
    # search_fields = ('title', 'price', 'publish_date',)
    list_filter = ('size', 'price')
    list_per_page = 10
    list_max_show_all = 1000
    # date_hierarchy = 'publish_date'
    actions = ['download_as_csv', 'publish_today']
    # empty_value_display = '(なし)'

    # fields = (
    #     'id', 'title', 'price', 'size', 'publish_date', 'created_by', 'created_at',
    # )
    # exclude = ('publisher',)
    readonly_fields = ('id', 'created_by', 'created_at')
    form = BookAdminForm

    # inlines = [
    #     BookStockInline,
    # ]
    # prepopulated_fields = {'description': ('title', 'publish_date', )}

    class Media:
        css = {
            'all': ('admin/css/custom_forms.css',)
        }
        # js = ('custom_code.js',)

    # def get_queryset(self, request):
    #     qs = super().get_queryset(request)
    #     return qs.filter(created_by=request.user)

    def save_model(self, request, obj, form, change):
        """モデル保存前に処理を追加する"""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    # def has_add_permission(self, request):
    #     return False
    #
    # def has_change_permission(self, request, obj=None):
    #     has_perm = super().has_change_permission(request, obj)
    #     return has_perm and request.user.email.rpartition('@')[2] == 'example.com'
    #
    # def has_delete_permission(self, request, obj=None):
    #     has_perm = super().has_delete_permission(request, obj)
    #     if obj is None:
    #         return has_perm
    #     else:
    #         return has_perm and obj.created_by == request.user

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
        queryset.update(publish_date=timezone.now().date())

    publish_today.short_description = '出版日を今日に更新'
    publish_today.allowed_permissions = ('change',)

    def format_price(self, obj):
        """価格のフォーマットを変更する"""
        if obj.price is None:
            return None
        return '{:,d} 円'.format(obj.price)

    format_price.short_description = '価格'
    format_price.admin_order_field = 'price'

    def format_publisher_name(self, obj):
        """出版社のフォーマットを変更する"""
        if obj.publisher is None:
            return None
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
        if obj.publish_date is None:
            return None
        return obj.publish_date.strftime('%Y/%m/%d')

    format_publish_date.short_description = '出版日'
    format_publish_date.admin_order_field = 'publish_date'

    def format_image(self, obj):
        """画像をHTMLで修飾する"""
        if not obj.image:
            return None
        return format_html('<img src="{}" width="100" />', obj.image.url)

    format_image.short_description = '画像'
    format_image.empty_value_display = 'No image'


class PublisherModelAdmin(admin.ModelAdmin):
    inlines = [
        BookInline,
    ]


class PublishedBook(Book):
    """本（発売中）モデル"""

    class Meta:
        proxy = True
        verbose_name = '本'
        verbose_name_plural = '本（発売中）'


class UnpublishedBook(Book):
    """本（未発売）モデル"""

    class Meta:
        proxy = True
        verbose_name = '本'
        verbose_name_plural = '本（未発売）'


class PublishedBookModelAdmin(BookModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(publish_date__lte=timezone.now().date())


class UnpublishedBookModelAdmin(BookModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(
            Q(publish_date__gt=timezone.now().date()) |
            Q(publish_date__isnull=True)
        )


admin.site.register(Book, BookModelAdmin)
admin.site.register(PublishedBook, PublishedBookModelAdmin)
admin.site.register(UnpublishedBook, UnpublishedBookModelAdmin)
admin.site.register(Author)
# admin.site.register(BookStock)
admin.site.register(Publisher, PublisherModelAdmin)
