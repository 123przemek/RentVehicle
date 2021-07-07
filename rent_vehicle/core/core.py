from core.models import Rent, Vehicle
from django.utils import timezone
from django.db import transaction
import time


# blad jest klasa ktora dziedziczy po wyjatku

class CollisionError(Exception):
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

    # transakcja dziala wg zasady: wszystko albo nic
    # w ramach transakcji mozna zalozyc blokade na dany zasob w obrebie calego systemu
    with transaction.atomic():
        # select_for_update zaklada blokade na zasob
        vehicle = Vehicle.objects.select_for_update().get(id=vehicle.id)
        print('zaczynamy rezerwację')
        time.sleep(10)
        # if vehicle.status != Vehicle.STATUS_AVAILABLE:
        #     raise ValueError("vehicle is not available")
        if not vehicle.for_rent():
            raise ValueError("vehicle is not available")

        # szukamy wypozyczen nachodzacych na nasz czas
        base_query = Rent.objects.filter(returned_at__isnull=True, vehicle=vehicle)
        is_collision = (
                (base_query
                 .filter(started_at__lt=end_time, finished_at__gt=end_time)
                 .exists()) or
                (base_query
                 .filter(started_at__lt=start_time, finished_at__lt=end_time)
                 .exists()) or
                (base_query
                 .filter(started_at__gt=start_time, finished_at__lt=end_time)
                 .exists())
        )
        if is_collision:
            raise CollisionError("time collision")
        # is_right_collision = (
        #     base_query
        #         .filter(started_at__lt=end_time, finished_at__gt=end_time)
        #         .exists())
        # if is_right_collision:
        #     raise CollisionError("time collision")
        #
        # is_left_collision = (
        #     base_query
        #         .filter(started_at__lt=start_time, finished_at__lt=end_time)
        #         .exists())
        # if is_left_collision:
        #     raise CollisionError("time collision")
        #
        # is_container_collision = (
        #     base_query
        #         .filter(started_at__gt=start_time, finished_at__lt=end_time)
        #         .exists())
        # if is_container_collision:
        #     raise CollisionError("time collision")

        # blokada sie konczy w momencie opuszczania 'with' czyli w tym wypadku przy 'return'
        return Rent.objects.create(started_at=start_time, finished_at=end_time,
                                   user=user, vehicle=vehicle)
