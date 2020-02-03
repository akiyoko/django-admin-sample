import csv

from django import forms
from django.contrib import admin
from django.http import HttpResponse
from django.urls import reverse
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
    pass
    # def clean_title(self):
    #     value = self.cleaned_data['title']
    #     if 'Django' not in value:
    #         raise forms.ValidationError("タイトルには「Django」という文字を含めてください")
    #     return value


class BookModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'price', 'size', 'publish_date')
    # list_display = ('id', 'title', 'display_price', 'display_size', 'display_publisher',
    #                 'publish_date')  # 'display_image',
    list_display_links = ('id', 'title')
    # list_select_related = ('publisher',)
    # ordering = ('-publish_date', 'id')
    ordering = ('id',)
    # search_fields = ('title', 'price', 'publish_date',)
    # list_filter = ('size', 'price')
    list_per_page = 10
    list_max_show_all = 1000
    # date_hierarchy = 'publish_date'
    actions = ['download_as_csv', 'publish_today']
    # empty_value_display = '(なし)'

    # fields = (
    #     'id', 'title', 'price', 'size', 'image', 'publish_date', 'created_by', 'created_at'
    # )
    # exclude = ('publisher',)
    # readonly_fields = ('id', 'created_by', 'created_at')
    form = BookAdminForm
    # inlines = [
    #     BookStockInline,
    # ]

    class Media:
        css = {
            'all': ('my_styles.css',)
        }
        js = ('my_code.js',)

    def save_model(self, request, obj, form, change):
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
    download_as_csv.allowed_permissions = ('view',)

    def publish_today(self, request, queryset):
        queryset.update(publish_date=timezone.now().date())

    publish_today.short_description = '出版日を今日に更新'
    publish_today.allowed_permissions = ('change',)

    def display_price(self, obj):
        if not obj.price:
            return None
        return '{:,d} 円'.format(obj.price)

    display_price.short_description = '価格'
    # Note: Django のソートは全て DB のクエリレベルで行うので、実際にDBにカラムが存在しないフィールドはソートできない。
    #       ただ、カスタムフィールドが、あるフィールドの代理になっているときは、そのフィールド名を指定するとソートできる
    #       https://qiita.com/zenwerk/items/044c149d93db097cdaf8
    display_price.admin_order_field = 'price'
    display_price.empty_value_display = '(価格未定)'

    # def display_size(self, obj):
    #     # Note: これは勝手にやってくれるっぽい！
    #     return obj.get_size_display()
    #
    # display_size.short_description = 'サイズ'
    # display_size.admin_order_field = 'size'

    def display_publisher(self, obj):
        if not obj.publisher:
            return None
        return format_html(
            '<a href="{}">{}</a>',
            reverse('admin:shop_publisher_change', args=[obj.publisher.id]),
            obj.publisher.name,
        )

    display_publisher.short_description = '出版社'
    display_publisher.admin_order_field = 'publisher__name'

    def display_image(self, obj):
        if not obj.image:
            return None
        return format_html('<img src="{}" width="200" />', obj.image.url)

    display_image.short_description = '画像'
    # 値が None の場合に利用される（空文字では利用されない）
    display_image.empty_value_display = 'No image.........'

    # def display_publish_date(self, obj):
    #     if not obj.publish_date:
    #         return None
    #     return obj.publish_date.strftime('%d %b %Y %H:%M:%S')
    #
    # display_publish_date.short_description = '出版日'

    # def save_model(self, request, obj, form, change):
    #     obj.save()


class PublisherModelAdmin(admin.ModelAdmin):
    inlines = [
        BookInline,
    ]


admin.site.register(Book, BookModelAdmin)
admin.site.register(Author)
# # admin.site.register(BookStock)
admin.site.register(Publisher, PublisherModelAdmin)
