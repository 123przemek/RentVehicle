from django.test import TestCase
from core.models import Vehicle, User, Rent
from core.core import rent_vehicle
from django.utils import timezone
from datetime import timedelta

NOW = timezone.now()
HOUR = timedelta(hours=1)
DAY = timedelta(days=1)
# Create your tests here.

class UserRentLimitTest(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user('u1')
        self.u2 = User.objects.create_user('u2')
        self.v1 = Vehicle.objects.create(kind=Vehicle.KIND_CAR, code='c1', status=Vehicle.STATUS_AVAILABLE)
        self.v2 = Vehicle.objects.create(kind=Vehicle.KIND_CAR, code='c2', status=Vehicle.STATUS_AVAILABLE)

    def test_success_no_collision(self):
        rent = rent_vehicle(self.v1, self.u1, start_time=NOW+HOUR*4, end_time=NOW+HOUR*5)
        self.assertIsNotNone(rent)

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
        self.assertRaises(ValueError, rent_vehicle, self.v1, self.u1,
                          start_time=NOW + DAY * 2, end_time=NOW + DAY * 5)
        #z tylu
        #w srodku
        #otacza calosc

    #time_margin
    #status pojazdu ma znaczenie