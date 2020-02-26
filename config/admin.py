from django.contrib.admin import AdminSite

APP_MODEL_ORDER = (
    ('auth', ('User', 'Group')),
    ('shop', ('Book', 'Author', 'Publisher')),
)


class CustomAdminSite(AdminSite):
    """AdminSite をカスタマイズしたクラス"""

    site_header = '管理サイト'
    site_title = 'XXプロジェクト'
    index_title = 'ホーム'
    site_url = None

    def _sort_app_list(self, app_list):
        """アプリケーションとモデルの並び順を変更する"""
        # APP_MODEL_ORDER のキーの並び順通りにソート
        app_labels = [app_model[0] for app_model in APP_MODEL_ORDER]
        app_list.sort(
            key=lambda x: app_labels.index(x['app_label'])
            if x['app_label'] in app_labels else len(app_labels)
        )

        # APP_MODEL_ORDER のバリューの並び順通りにソート
        for app in app_list:
            object_names = dict(APP_MODEL_ORDER).get(app['app_label'], ())
            app['models'].sort(
                key=lambda x: object_names.index(x['object_name'])
                if x['object_name'] in object_names else len(object_names)
            )

    def index(self, request, extra_context=None):
        """ダッシュボード画面を表示するためのビュー"""
        response = super().index(request, extra_context)
        self._sort_app_list(response.context_data['app_list'])
        return response

    def app_index(self, request, app_label, extra_context=None):
        """アプリケーションダッシュボード画面を表示するためのビュー"""
        response = super().app_index(request, app_label, extra_context)
        self._sort_app_list(response.context_data['app_list'])
        return response
