import os
from datetime import datetime
from unittest import TestCase
from unittest.mock import Mock

import jsonpickle
from dateutil.tz import tzoffset

from octopus_energy.mappers import (
    _calculate_unit,
    consumption_from_response,
    to_timestamp_str,
    meters_from_response,
    _get_page_reference,
    tariff_rates_from_response,
)
from octopus_energy.models import UnitType, MeterGeneration, SortOrder, Aggregate
from tests import load_fixture_json, load_json


def load_mapping_response_json(filename: str) -> dict:
    return jsonpickle.decode(load_json(os.path.join("mapping_results", filename)))


def _gen_mapping_response_json(obj) -> dict:
    print(jsonpickle.encode(obj))


class TestAccountMappers(TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.maxDiff = None

    def test_account_mapping(self):
        """Verifies that the result of mapping a known input produces a known output."""
        meters = meters_from_response(load_fixture_json("account_response.json"))
        expected_response = load_mapping_response_json("account_mapping.json")
        self.assertCountEqual(meters, expected_response)


class TestTariffMappers(TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.maxDiff = None

    def test_rate_mapping(self):
        """Verifies that the result of mapping a known input produces a known output."""
        rates = tariff_rates_from_response(load_fixture_json("get_tariff_response.json"))
        expected_response = load_mapping_response_json("tariff_rate_mapping.json")
        self.assertCountEqual(rates, expected_response)

    def test_no_results(self):
        self.assertEqual([], tariff_rates_from_response({}))


class TestConsumptionMappers(TestCase):
    def test_smets1_gas_mapping_kwh(self):
        response = load_fixture_json("consumption_response.json")
        consumption = consumption_from_response(
            response, Mock(generation=MeterGeneration.SMETS1_GAS), UnitType.KWH
        )
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
            response, Mock(generation=MeterGeneration.SMETS1_GAS), UnitType.CUBIC_METERS
        )
        with self.subTest("units"):
            self.assertEqual(consumption.unit_type, UnitType.CUBIC_METERS)
        with self.subTest("first interval consumption (in cubic meters)"):
            self.assertEqual(consumption.intervals[0].consumed_units, 0.0056316372868023025)

    def test_smets2_gas_mapping_kwh(self):
        response = load_fixture_json("consumption_response.json")
        consumption = consumption_from_response(
            response, Mock(generation=MeterGeneration.SMETS2_GAS), UnitType.KWH
        )
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
            response, Mock(generation=MeterGeneration.SMETS2_GAS), UnitType.CUBIC_METERS
        )
        with self.subTest("units"):
            self.assertEqual(consumption.unit_type, UnitType.CUBIC_METERS)
        with self.subTest("first interval consumption (converted to kwh)"):
            self.assertEqual(consumption.intervals[0].consumed_units, 0.063)

    def test_smets1_elec_mapping(self):
        response = load_fixture_json("consumption_response.json")
        consumption = consumption_from_response(
            response, Mock(generation=MeterGeneration.SMETS1_ELECTRICITY), UnitType.KWH
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
            response, Mock(generation=MeterGeneration.SMETS2_ELECTRICITY), UnitType.KWH
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
            response,
            meter=Mock(generation=MeterGeneration.SMETS1_GAS),
            desired_unit_type=UnitType.KWH,
        )
        with self.subTest("interval count"):
            self.assertEqual(len(consumption.intervals), 0, "Contains 0 periods of consumption")
        with self.subTest("units"):
            self.assertEqual(consumption.unit_type, UnitType.KWH)

    def test_consumption_missing_intervals(self):
        response = load_fixture_json("consumption_missing_results_response.json")
        consumption = consumption_from_response(
            response,
            meter=Mock(generation=MeterGeneration.SMETS1_GAS),
            desired_unit_type=UnitType.KWH,
        )
        with self.subTest("interval count"):
            self.assertEqual(len(consumption.intervals), 0, "Contains 0 periods of consumption")
        with self.subTest("units"):
            self.assertEqual(consumption.unit_type, UnitType.KWH)

    def test_timestamp_format(self):
        """Verifies timestamps.

        * microseconds are stripped
        * formatted as iso8601
        """
        timestamp = datetime.utcnow().replace(microsecond=0)
        str = to_timestamp_str(timestamp)
        assert str == timestamp.isoformat()

    def test_conversions(self):
        """Tests the unit conversions supported by the library."""
        for test in [
            (UnitType.CUBIC_METERS, UnitType.KWH, 100, 1118.68),
            (UnitType.KWH, UnitType.CUBIC_METERS, 100, 8.9391068044481),
            (UnitType.KWH, UnitType.KWH, 100, 100),
            (UnitType.CUBIC_METERS, UnitType.CUBIC_METERS, 100, 100),
            (None, None, 100, 100),
        ]:
            self.assertEqual(_calculate_unit(test[2], test[0], test[1]), test[3])

    def test_page_reference(self):
        with self.subTest("Page that does not exist in the response returns None"):
            response = {}
            self.assertIsNone(_get_page_reference(response, "next"))

        with self.subTest("The page has no value in the response returns None"):
            response = {
                "next": None,
            }
            self.assertIsNone(_get_page_reference(response, "next"))

        with self.subTest("page url with no arguments returns None"):
            response = {
                "next": "http://octopus.energy",
            }
            self.assertIsNone(_get_page_reference(response, "next"))

        with self.subTest("period from extracted from url"):
            response = {
                "next": "http://octopus.energy?period_from=2020-01-01",
            }
            self.assertEqual(
                _get_page_reference(response, "next").options["period_from"],
                datetime(year=2020, month=1, day=1),
            )

        with self.subTest("period to extracted from url"):
            response = {
                "next": "http://octopus.energy?period_to=2020-01-01",
            }
            self.assertEqual(
                _get_page_reference(response, "next").options["period_to"],
                datetime(year=2020, month=1, day=1),
            )

        with self.subTest("order extracted from url"):
            response = {
                "next": f"http://octopus.energy?order={SortOrder.NEWEST_FIRST.value}",
            }
            self.assertEqual(
                _get_page_reference(response, "next").options["order"], SortOrder.NEWEST_FIRST
            )

        with self.subTest("group by extracted from url"):
            response = {
                "next": f"http://octopus.energy?group_by={Aggregate.QUARTER.value}",
            }
            self.assertEqual(
                _get_page_reference(response, "next").options["group_by"], Aggregate.QUARTER
            )

        with self.subTest("arguments with no special handling are stored in raw form"):
            response = {
                "next": "http://octopus.energy?some_arg=some_value",
            }
            self.assertEqual(
                _get_page_reference(response, "next").options["some_arg"], "some_value"
            )
