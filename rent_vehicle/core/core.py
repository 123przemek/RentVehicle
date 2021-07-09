from core.models import Rent, Vehicle
from django.utils import timezone
from django.db import transaction


class CollisionError(Exception):
    pass


class StatusError(Exception):
    pass


def rent_vehicle(vehicle, user, start_time, end_time):
    now = timezone.now()
    if start_time < now or end_time <= now:
        raise ValueError("required current or future time")
    elif start_time >= end_time:
        raise ValueError("end_time must be greater than start_time")
    elif end_time - start_time > Rent.MAX_RENT_TIME:
        raise ValueError("too long rent time")
    elif end_time > now + Rent.LAST_AVAILABLE_TIME:
        raise ValueError("end date out of range")

    with transaction.atomic():
        vehicle = Vehicle.objects.select_for_update().get(id=vehicle.id)

        if not vehicle.for_rent():
            raise StatusError("The vehicle is not available./"
                              "It's either broken down or has been already booked.")

        base_query = Rent.objects.filter(returned_at__isnull=True, vehicle=vehicle)
        is_collision = (
                (base_query
                 # db.started_at < end_time and db.finished_at > end_time
                 .filter(started_at__lt=end_time, finished_at__gt=end_time)
                 .exists()) or
                (base_query
                 # db.started_at < start_time and db.finished_at < end_time
                 .filter(started_at__lte=start_time, finished_at__gt=start_time)
                 .exists()) or
                (base_query
                 # db.started_at > start_time and db.finished_at < end_time
                 .filter(started_at__gte=start_time, finished_at__lt=end_time)
                 .exists())
        )
        if is_collision:
            raise CollisionError("time collision")

        return Rent.objects.create(started_at=start_time, finished_at=end_time,
                                   user=user, vehicle=vehicle)
