from django.contrib.auth import views as auth_views
# from django.contrib import admin
from django.urls import path

from .admin import admin_site

# admin.site.site_header = 'Site Header'
# admin.site.site_title = 'Site Title'
# admin.site.index_title = 'Index Title'

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('admin/', admin_site.urls),
    path('admin/password_reset/', auth_views.PasswordResetView.as_view(),
         name='admin_password_reset'),
    path('admin/password_reset/done/', auth_views.PasswordResetDoneView.as_view(),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(),
         name='password_reset_complete'),
]
