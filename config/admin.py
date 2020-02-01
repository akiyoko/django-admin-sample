from collections import OrderedDict

from django.contrib.admin import AdminSite

APP_LIST_ORDER = OrderedDict((
    ('shop', ('Book', 'Author', 'Publisher')),
    ('auth', ('User', 'Group')),
))


class MyAdminSite(AdminSite):
    """AdminSite をカスタマイズしたクラス"""

    site_header = '管理サイト'
    index_title = 'ホーム'
    site_url = None

    def get_app_list(self, request):
        """app_list を取得してソートする"""

        app_dict = self._build_app_dict(request)

        # APP_LIST_ORDER のキーの並び順通りにソート
        app_list = sorted(
            app_dict.values(),
            key=lambda x: list(APP_LIST_ORDER.keys()).index(
                x['app_label'])
        )

        # APP_LIST_ORDER のバリューの並び順通りにソート
        for app in app_list:
            app['models'].sort(
                key=lambda x: list(APP_LIST_ORDER[app['app_label']]).index(
                    x['object_name']))

        return app_list
