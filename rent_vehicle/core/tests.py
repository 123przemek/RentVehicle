from django.test import TestCase
from core.models import Vehicle, User, Rent
from core.core import rent_vehicle, CollisionError, StatusError
from django.utils import timezone
from datetime import timedelta

NOW = timezone.now()
HOUR = timedelta(hours=1)
DAY = timedelta(days=1)


class UserRentLimitTest(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user('u1')
        self.u2 = User.objects.create_user('u2')
        self.v1 = Vehicle.objects.create(kind=Vehicle.KIND_CAR, code='c1', status=Vehicle.STATUS_AVAILABLE)
        self.v2 = Vehicle.objects.create(kind=Vehicle.KIND_CAR, code='c2', status=Vehicle.STATUS_AVAILABLE)

    def test_success_no_collision(self):
        rent = rent_vehicle(self.v1, self.u1, start_time=NOW+HOUR*4, end_time=NOW+HOUR*5)
        self.assertIsNotNone(rent)

    def test_success_multiple_rent_no_collision(self):
        self.assertTrue(NOW + HOUR *8 < NOW + DAY * 2)
        rent = rent_vehicle(self.v1, self.u1, start_time=NOW + HOUR, end_time=NOW + HOUR *8)
        rent2 = rent_vehicle(self.v1, self.u1, start_time=NOW + DAY * 2, end_time=NOW + DAY * 2 + HOUR * 3)
        self.assertIsNotNone(rent)
        self.assertIsNotNone(rent2)

    def test_past_date(self):
        self.assertRaises(ValueError, rent_vehicle, self.v1, self.u1,
                          start_time=NOW - HOUR * 4, end_time=NOW - HOUR * 2)

    def test_incorrect_time_range(self):
        self.assertRaises(ValueError, rent_vehicle, self.v1, self.u1,
                          start_time=NOW + HOUR * 4, end_time=NOW + HOUR * 2)
        self.assertRaises(ValueError, rent_vehicle, self.v1, self.u1,
                          start_time=NOW + HOUR * 4, end_time=NOW + HOUR * 4)

    def test_max_rent_time(self):
        self.assertEquals(Rent.MAX_RENT_TIME, DAY * 7)

        rent = rent_vehicle(self.v1, self.u1, start_time=NOW + DAY * 1, end_time=NOW + DAY * 8)
        self.assertIsNotNone(rent)

        self.assertRaises(ValueError, rent_vehicle, self.v2, self.u2,
                          start_time=NOW + DAY * 1, end_time=NOW + DAY * 8 + HOUR)

    def test_out_of_range_date(self):
        self.assertEquals(Rent.LAST_AVAILABLE_TIME, DAY * 90)

        self.assertRaises(ValueError, rent_vehicle, self.v1, self.u1,
                          start_time=NOW + DAY * 88, end_time=NOW + DAY * 91)

    def test_collision(self):
        rent = rent_vehicle(self.v1, self.u1, start_time=NOW+DAY*3, end_time=NOW+DAY*6)
        # z przodu
        self.assertRaises(CollisionError, rent_vehicle, self.v1, self.u1,
                          start_time=NOW + DAY * 2, end_time=NOW + DAY * 5)
        #z tylu
        self.assertRaises(CollisionError, rent_vehicle, self.v1, self.u1,
                          start_time=NOW + DAY * 4, end_time=NOW + DAY * 9)
        #w srodku
        self.assertRaises(CollisionError, rent_vehicle, self.v1, self.u1,
                          start_time=NOW + DAY * 4, end_time=NOW + DAY * 5)
        #otacza calosc
        self.assertRaises(CollisionError, rent_vehicle, self.v1, self.u1,
                          start_time=NOW + DAY * 2, end_time=NOW + DAY * 7)

    def test_status_not_available(self):
        self.v1.status = Vehicle.STATUS_BROKE_DOWN
        self.v1.save()

        self.assertRaises(StatusError, rent_vehicle, self.v1, self.u1,
                          start_time=NOW + DAY * 2, end_time=NOW + DAY * 7)
