from django import forms
from tinymce.widgets import AdminTinyMCE


class BookAdminForm(forms.ModelForm):
    class Meta:
        widgets = {
            # 'publish_date': forms.widgets.SelectDateWidget(),
            'description': AdminTinyMCE(),
        }

    def clean_title(self):
        value = self.cleaned_data['title']
        if 'Java' in value:
            raise forms.ValidationError("タイトルには「Java」を含めないでください。")
        return value

    def clean(self):
        title = self.cleaned_data.get('title')
        price = self.cleaned_data.get('price')
        if title and '薄い本' in title and price and price > 3000:
            raise forms.ValidationError("薄い本は3,000円を超えてはいけません。")
