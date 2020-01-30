from django import forms
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse

from .models import Author, Book, Publisher


class BookAdminForm(forms.ModelForm):
    pass
    # def clean_title(self):
    #     value = self.cleaned_data['title']
    #     if 'Django' not in value:
    #         raise forms.ValidationError("タイトルには「Django」という文字を含めてください")
    #     return value


class BookModelAdmin(admin.ModelAdmin):
    # fields = ('display_image',)
    # readonly_fields = ('display_image',)
    list_display = ('title', 'display_price', 'display_size', 'display_publisher',
                    'publish_date')  # 'display_image',
    list_display_links = ('title',)
    list_filter = ('size', 'price')
    list_select_related = ('publisher',)
    ordering = ('id',)  # '-publish_date',)
    search_fields = ('title', 'price', 'publish_date',)
    date_hierarchy = 'publish_date'
    form = BookAdminForm
    list_per_page = 10
    empty_value_display = '-'

    class Media:
        css = {
            'all': ('my_styles.css',)
        }
        js = ('my_code.js',)

    def display_price(self, obj):
        if not obj.price:
            return None
        return '{:,d} 円'.format(obj.price)

    display_price.short_description = '価格'
    # Note: Django のソートは全て DB のクエリレベルで行うので、実際にDBにカラムが存在しないフィールドはソートできない。
    #       ただ、カスタムフィールドが、あるフィールドの代理になっているときは、そのフィールド名を指定するとソートできる
    #       https://qiita.com/zenwerk/items/044c149d93db097cdaf8
    display_price.admin_order_field = 'price'

    def display_size(self, obj):
        if not obj.size:
            return None
        return obj.get_size_display()

    display_size.short_description = 'サイズ'
    display_size.admin_order_field = 'size'

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


admin.site.register(Publisher)
admin.site.register(Author)
admin.site.register(Book, BookModelAdmin)
