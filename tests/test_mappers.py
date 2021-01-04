from datetime import datetime
from unittest import TestCase

from dateutil.tz import tzoffset

from octopus_energy.mappers import (
    _calculate_unit,
    consumption_from_response,
)
from octopus_energy.models import UnitType, MeterType
from tests import load_fixture_json


class TestMappers(TestCase):
    def test_smets1_gas_mapping_kwh(self):
        response = load_fixture_json("consumption_response.json")
        consumption = consumption_from_response(response, MeterType.SMETS1_GAS, UnitType.KWH)
        with self.subTest("interval count"):
            self.assertEqual(len(consumption.intervals), 3, "Contains 3 periods of consumption")
        with self.subTest("units"):
            self.assertEqual(consumption.unit_type, UnitType.KWH)
        with self.subTest("first interval consumption"):
            self.assertEqual(consumption.intervals[0].consumed_units, 0.063)
        with self.subTest("first interval start"):
            self.assertEqual(
                consumption.intervals[0].interval_start,
                datetime(2018, 5, 19, 0, 30, tzinfo=tzoffset(None, 3600)),
            )
        with self.subTest("first interval end"):
            self.assertEqual(
                consumption.intervals[0].interval_end,
                datetime(2018, 5, 19, 1, 0, tzinfo=tzoffset(None, 3600)),
            )

    def test_smets1_gas_mapping_cubic_meters(self):
        response = load_fixture_json("consumption_response.json")
        consumption = consumption_from_response(
            response, MeterType.SMETS1_GAS, UnitType.CUBIC_METERS
        )
        with self.subTest("units"):
            self.assertEqual(consumption.unit_type, UnitType.CUBIC_METERS)
        with self.subTest("first interval consumption (in cubic meters)"):
            self.assertEqual(consumption.intervals[0].consumed_units, 0.0056316372868023025)

    def test_smets2_gas_mapping_kwh(self):
        response = load_fixture_json("consumption_response.json")
        consumption = consumption_from_response(response, MeterType.SMETS2_GAS, UnitType.KWH)
        with self.subTest("interval count"):
            self.assertEqual(len(consumption.intervals), 3, "Contains 3 periods of consumption")
        with self.subTest("units"):
            self.assertEqual(consumption.unit_type, UnitType.KWH)
        with self.subTest("first interval consumption (converted to kwh)"):
            self.assertEqual(consumption.intervals[0].consumed_units, 0.7047684)
        with self.subTest("first interval start"):
            self.assertEqual(
                consumption.intervals[0].interval_start,
                datetime(2018, 5, 19, 0, 30, tzinfo=tzoffset(None, 3600)),
            )
        with self.subTest("first interval end"):
            self.assertEqual(
                consumption.intervals[0].interval_end,
                datetime(2018, 5, 19, 1, 0, tzinfo=tzoffset(None, 3600)),
            )

    def test_smets2_gas_mapping_cubic_meters(self):
        response = load_fixture_json("consumption_response.json")
        consumption = consumption_from_response(
            response, MeterType.SMETS2_GAS, UnitType.CUBIC_METERS
        )
        with self.subTest("units"):
            self.assertEqual(consumption.unit_type, UnitType.CUBIC_METERS)
        with self.subTest("first interval consumption (converted to kwh)"):
            self.assertEqual(consumption.intervals[0].consumed_units, 0.063)

    def test_smets1_elec_mapping(self):
        response = load_fixture_json("consumption_response.json")
        consumption = consumption_from_response(
            response, MeterType.SMETS1_ELECTRICITY, UnitType.KWH
        )
        with self.subTest("interval count"):
            self.assertEqual(len(consumption.intervals), 3, "Contains 3 periods of consumption")
        with self.subTest("units"):
            self.assertEqual(consumption.unit_type, UnitType.KWH)
        with self.subTest("first interval consumption (converted to kwh)"):
            self.assertEqual(consumption.intervals[0].consumed_units, 0.063)
        with self.subTest("first interval start"):
            self.assertEqual(
                consumption.intervals[0].interval_start,
                datetime(2018, 5, 19, 0, 30, tzinfo=tzoffset(None, 3600)),
            )
        with self.subTest("first interval end"):
            self.assertEqual(
                consumption.intervals[0].interval_end,
                datetime(2018, 5, 19, 1, 0, tzinfo=tzoffset(None, 3600)),
            )

    def test_smets2_elec_mapping(self):
        response = load_fixture_json("consumption_response.json")
        consumption = consumption_from_response(
            response, MeterType.SMETS2_ELECTRICITY, UnitType.KWH
        )
        with self.subTest("interval count"):
            self.assertEqual(len(consumption.intervals), 3, "Contains 3 periods of consumption")
        with self.subTest("units"):
            self.assertEqual(consumption.unit_type, UnitType.KWH)
        with self.subTest("first interval consumption (converted to kwh)"):
            self.assertEqual(consumption.intervals[0].consumed_units, 0.063)
        with self.subTest("first interval start"):
            self.assertEqual(
                consumption.intervals[0].interval_start,
                datetime(2018, 5, 19, 0, 30, tzinfo=tzoffset(None, 3600)),
            )
        with self.subTest("first interval end"):
            self.assertEqual(
                consumption.intervals[0].interval_end,
                datetime(2018, 5, 19, 1, 0, tzinfo=tzoffset(None, 3600)),
            )

    def test_consumption_no_intervals(self):
        response = load_fixture_json("consumption_no_results_response.json")
        consumption = consumption_from_response(
            response, meter_type=MeterType.SMETS1_GAS, desired_unit_type=UnitType.KWH
        )
        with self.subTest("interval count"):
            self.assertEqual(len(consumption.intervals), 0, "Contains 0 periods of consumption")
        with self.subTest("units"):
            self.assertEqual(consumption.unit_type, UnitType.KWH)

    def test_consumption_missing_intervals(self):
        response = load_fixture_json("consumption_missing_results_response.json")
        consumption = consumption_from_response(
            response, meter_type=MeterType.SMETS1_GAS, desired_unit_type=UnitType.KWH
        )
        with self.subTest("interval count"):
            self.assertEqual(len(consumption.intervals), 0, "Contains 0 periods of consumption")
        with self.subTest("units"):
            self.assertEqual(consumption.unit_type, UnitType.KWH)


class TestUnitConversion(TestCase):
    def test_conversions(self):
        """Tests the unit conversions supported by the library."""
        conversion_tests = [
            (UnitType.CUBIC_METERS, UnitType.KWH, 100, 1118.68),
            (UnitType.KWH, UnitType.CUBIC_METERS, 100, 8.9391068044481),
            (UnitType.KWH, UnitType.KWH, 100, 100),
            (UnitType.CUBIC_METERS, UnitType.CUBIC_METERS, 100, 100),
        ]
        for conversion_test in conversion_tests:
            with self.subTest(f"{conversion_test[0]} to {conversion_test[1]}"):
                self.assertEqual(
                    _calculate_unit(conversion_test[2], conversion_test[0], conversion_test[1]),
                    conversion_test[3],
                )
