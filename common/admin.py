from django.contrib.admin import AdminSite
from django.template.response import TemplateResponse
from django.urls import path
from django.utils import timezone

from shop.models import Book

APP_MODEL_ORDER = (
    ('auth', ('User', 'Group')),
    ('shop', ('Book', 'Author', 'Publisher')),
)


class CustomAdminSite(AdminSite):
    """AdminSite をカスタマイズしたクラス"""

    site_header = '管理サイト'
    site_title = 'マイプロジェクト'
    index_title = 'ホーム'
    site_url = None

    def get_urls(self):
        """URLパターンと対応するビューを定義"""
        return [
            # お知らせ画面のURLパターン
            path('info/', self.admin_view(self.info_view)),
        ] + super().get_urls()

    def info_view(self, request):
        """お知らせ画面を表示するためのビュー"""
        context = {
            # 本日の登録件数を表示するための変数
            'books_created_today': Book.objects.filter(
                created_at__date=timezone.localdate()),
            # 共通で利用する変数
            **self.each_context(request),
        }
        return TemplateResponse(request, 'admin/info.html', context)

    def index(self, request, extra_context=None):
        """ホーム画面を表示するためのビュー"""
        response = super().index(request, extra_context)
        self._sort_app_list(response.context_data['app_list'])
        return response

    def app_index(self, request, app_label, extra_context=None):
        """アプリケーションホーム画面を表示するためのビュー"""
        response = super().app_index(request, app_label, extra_context)
        self._sort_app_list(response.context_data['app_list'])
        return response

    def _sort_app_list(self, app_list):
        """アプリケーションとモデルの並び順を変更する"""
        # アプリケーションの並び順を変更
        app_labels = [app_model[0] for app_model in APP_MODEL_ORDER]
        app_list.sort(
            key=lambda x: app_labels.index(x['app_label'])
            if x['app_label'] in app_labels else len(app_labels)
        )

        # モデルの並び順を変更
        for app in app_list:
            object_names = dict(APP_MODEL_ORDER).get(app['app_label'], ())
            app['models'].sort(
                key=lambda x: object_names.index(x['object_name'])
                if x['object_name'] in object_names else len(object_names)
            )

    def logout(self, request, extra_context=None):
        # extra_context = extra_context or {}
        # extra_context['next_page'] = 'admin:login'
        ret = super().logout(request, extra_context=extra_context)
        return ret
