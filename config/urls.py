from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

handler404 = 'common.handlers.handler404'
handler500 = 'common.handlers.handler500'

# admin.site.site_header = '管理サイト'
# admin.site.site_title = 'XXプロジェクト'
# admin.site.index_title = 'ホーム'
# admin.site.site_url = None

urlpatterns = [
    path('admin/', admin.site.urls),
    # パスワード再設定用のURLパターンを登録
    path('admin/password_reset/', auth_views.PasswordResetView.as_view(),
         name='admin_password_reset'),
    path('admin/password_reset/done/', auth_views.PasswordResetDoneView.as_view(),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(),
         name='password_reset_complete'),
]
# DEBUG が True の場合に runserver でメディアファイルを配信するための設定
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
