from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
# from django.http.response import HttpResponse
from django.urls import include, path

handler404 = 'common.handlers.handler404'
handler500 = 'common.handlers.handler500'


# def download_as_csv(modeladmin, request, queryset):
#     """選択されたレコードのCSVダウンロードをおこなう"""
#     meta = modeladmin.model._meta
#     response = HttpResponse(content_type='text/csv')
#     response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
#     writer = csv.writer(response)
#     field_names = [field.name for field in meta.fields]
#     writer.writerow(field_names)
#     for obj in queryset:
#         writer.writerow([getattr(obj, field) for field in field_names])
#     return response
#
#
# def has_permission(request):
#     return request.user.is_active and request.user.is_staff \
#            and request.user.last_name and request.user.first_name


# admin.site.site_header = '管理サイト'
# admin.site.site_title = 'XXプロジェクト'
# admin.site.index_title = 'ホーム'
# admin.site.site_url = None
# admin.site.add_action(download_as_csv, 'CSVダウンロード')
# admin.site.has_permission = has_permission

urlpatterns = [
    path('admin/', admin.site.urls),
    path('tinymce/', include('tinymce.urls')),
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
