from django.forms.models import model_to_dict
from django.http.response import JsonResponse
from django.views import View

from .models import Address


class AddressSearchAjaxView(View):
    def get(self, request, *args, **kwargs):
        postal_code = request.GET.get('postalCode')
        addresses = Address.objects.filter(postal_code=postal_code)
        data = [
            model_to_dict(address, ['prefecture', 'city', 'section'])
            for address in addresses
        ]
        return JsonResponse(data, safe=False)
