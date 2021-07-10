from django.contrib import admin
from django.utils import timezone

from core.models import Vehicle, Rent


class VehicleAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'kind', 'code', 'status'
    ]
    list_filter = ['kind','status']


@admin.action(description='balablabla')
def make_returned(modeladmin, request, queryset):
    queryset.update(returned_at=timezone.now())


class RentAdmin(admin.ModelAdmin):
    actions = [make_returned]
    list_display = [
        'id', 'vehicle', 'user', 'started_at', 'finished_at', 'returned_at'
    ]


admin.site.register(Vehicle, VehicleAdmin)
admin.site.register(Rent, RentAdmin)
