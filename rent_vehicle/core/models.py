from datetime import timedelta

from django.db import models
from django.contrib.auth.models import User


class Vehicle(models.Model):
    KIND_CAR = 'C'
    KIND_BIKE = 'B'
    KIND_SCOOTER = 'S'
    KIND_ELECTRIC_SCOOTER = 'ES'
    KIND_CHOICES = [
        (KIND_CAR, 'car'),
        (KIND_BIKE, 'bike'),
        (KIND_SCOOTER, 'scooter'),
        (KIND_ELECTRIC_SCOOTER, 'electric scooter')
    ]

    STATUS_AVAILABLE = 'AV'
    STATUS_BROKE_DOWN = 'BD'
    STATUS_CHOICES = [
        (STATUS_AVAILABLE, 'available'),
        (STATUS_BROKE_DOWN, 'broke down')
    ]

    kind = models.CharField(max_length=2, choices=KIND_CHOICES)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=3, choices=STATUS_CHOICES)

    def __str__(self):
        return self.code


class Rent(models.Model):
    MAX_RENT_TIME = timedelta(days=7)
    LAST_AVAILABLE_TIME = timedelta(days=90)
    started_at = models.DateTimeField()
    finished_at = models.DateTimeField()
    returned_at = models.DateTimeField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.RESTRICT)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.RESTRICT)
    notes = models.TextField(blank=True, null=True)
