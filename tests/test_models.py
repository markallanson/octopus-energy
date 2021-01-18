from datetime import datetime, timedelta
from unittest import TestCase

from octopus_energy.models import Tariff, Meter, MeterGeneration, EnergyType


class MeterTests(TestCase):
    def test_meter_get_tariff(self):
        for test in [
            (
                "Open ended, check date within range",
                datetime.utcnow() + timedelta(days=-10),
                None,
                datetime.utcnow(),
                False,
            ),
            (
                "Closed, check date within range",
                datetime.utcnow() + timedelta(days=-10),
                datetime.utcnow() + timedelta(days=1),
                datetime.utcnow(),
                False,
            ),
            (
                "Check date outside of range",
                datetime.utcnow() + timedelta(days=-10),
                datetime.utcnow() + timedelta(days=1),
                datetime.utcnow(),
                False,
            ),
        ]:
            with self.subTest(test[0]):
                tariff = Tariff("ABC", test[1], test[2])
                meter = Meter("", "", EnergyType.GAS, MeterGeneration.SMETS1_GAS, [tariff])
                self.assertTrue(
                    (tariff is None and test[4]) or meter.get_tariff_at(test[3]) == tariff
                )
