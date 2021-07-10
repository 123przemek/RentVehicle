import itertools

from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, ListView
from django.utils.decorators import method_decorator
from django.urls import reverse

from core.forms import CreateRentForm
from core.models import Rent, Vehicle


@method_decorator(login_required, name='dispatch')
class CreateRent(CreateView):
    template_name = 'rent_form.html'

    def get_success_url(self):
        return reverse('rent_list')

    def get_form(self, form_class=None):
        if self.request.method == 'GET':
            return CreateRentForm(user=self.request.user)

        return CreateRentForm(self.request.POST, user=self.request.user)


@method_decorator(login_required, name='dispatch')
class UserRentList(ListView):
    template_name = 'rent_list.html'

    def get_queryset(self):
        return (
            Rent.objects
            .select_related('vehicle')
            .filter(user=self.request.user, returned_at__isnull=True)
            .order_by("vehicle__kind", "started_at")
        )

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = object_list if object_list is not None else self.object_list
        groups = {}
        for kind, group in itertools.groupby(queryset, key=lambda r: r.vehicle.kind):
            kind_name = Vehicle.KIND_NAME_DICT[kind]
            groups[kind_name] = list(group)
        return {"groups": groups}
