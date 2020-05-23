from django.views.defaults import page_not_found, server_error


def handler404(request, exception):
    if request.path.startswith('/admin/'):
        return page_not_found(request, exception, template_name='admin/404.html')
    else:
        return page_not_found(request, exception)


def handler500(request):
    if request.path.startswith('/admin/'):
        return server_error(request, template_name='admin/500.html')
    else:
        return server_error(request)
