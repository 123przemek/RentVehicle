from django.contrib import admin
from core.models import Vehicle, Rent


class VehicleAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'kind', 'code', 'status'
    ]
    list_filter = ['kind','status']

class RentAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'vehicle', 'user', 'started_at', 'finished_at', 'returned_at'
    ]

admin.site.register(Vehicle, VehicleAdmin)
admin.site.register(Rent, RentAdmin)