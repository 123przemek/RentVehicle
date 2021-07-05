from core.models import Rent
from django.utils import timezone

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
    #szukamy wypozyczen nachodzacych na nasz czas
    is_right_collision = (
        Rent.objects
         .filter(returned_at__isnull=True)
         .filter(started_at__lt=end_time, finished_at__gt=end_time)
         .exists())
    if is_right_collision:
        raise ValueError("time collision")

    return Rent.objects.create(started_at=start_time, finished_at=end_time,
                               user=user, vehicle=vehicle)