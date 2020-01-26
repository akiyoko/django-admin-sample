from django.contrib import admin
from django import forms

from .models import Author, Book, Publisher


class BookAdminForm(forms.ModelForm):
    pass
    # def clean_title(self):
    #     value = self.cleaned_data['title']
    #     if 'Django' not in value:
    #         raise forms.ValidationError("タイトルには「Django」という文字を含めてください")
    #     return value


class BookModelAdmin(admin.ModelAdmin):
    list_display = ('title', 'publisher', 'price')
    ordering = ('-price',)
    form = BookAdminForm
    list_per_page = 10

    class Media:
        css = {
            "all": ("my_styles.css",)
        }
        js = ("my_code.js",)


admin.site.register(Publisher)
admin.site.register(Author)
admin.site.register(Book, BookModelAdmin)
