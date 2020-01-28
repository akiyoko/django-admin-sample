from django.contrib.admin import site, AdminSite


class MyAdminSite(AdminSite):
    site_header = 'Site Header'
    site_title = 'Site Title'
    index_title = 'Index Title'

    def __init__(self, *args, **kwargs):
        # Note: カスタマイズしたAdminSiteをURLconfで読み込む前に
        #       本家のAdminSiteオブジェクトが生成されてモデルクラスの登録も完了してしまうので、
        #       ここで改めて保持しているオブジェクトの入れ替えをおこなう
        super().__init__(*args, **kwargs)
        # Note: admin.siteに登録されたモデルを引き継ぐ
        #       https://stackoverflow.com/a/35003223
        self._registry.update(site._registry)
        # Note: ModelAdminのadmin_siteが本家AdminSiteになってしまうことで、
        #       モデルごとの画面でsite_header, site_titleが反映されないなどの不具合が出る。
        #       https://stackoverflow.com/a/54790209
        for model, model_admin in self._registry.items():
            model_admin.admin_site = self


admin_site = MyAdminSite()
