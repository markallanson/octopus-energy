from datetime import datetime, timedelta
from unittest import TestCase
from unittest.mock import patch, Mock

from octopus_energy import (
    OctopusEnergyConsumerClient,
    Meter,
    EnergyType,
    SortOrder,
    PageReference,
    Aggregate,
    EnergyTariffType,
    RateType,
)
from tests import does_asyncio


class ClientTestCase(TestCase):
    def test_cannot_use_client_without_async(self):
        with self.assertRaises(TypeError):
            with OctopusEnergyConsumerClient(""):
                pass

    @does_asyncio
    @patch("octopus_energy.client.OctopusEnergyRestClient", autospec=True)
    async def test_init(self, mock_rest_client: Mock):
        api_token = "A_BVC"
        async with OctopusEnergyConsumerClient(api_token):
            with self.subTest("passes api token to rest client"):
                mock_rest_client.assert_called_once_with(api_token)

    @does_asyncio
    @patch("octopus_energy.client.OctopusEnergyRestClient", autospec=True)
    @patch("octopus_energy.client.meters_from_response", autospec=True)
    async def test_get_meters(self, mock_mapper: Mock, mock_rest_client: Mock):
        account = "Account"
        async with OctopusEnergyConsumerClient("") as client:
            response = await client.get_meters(account)
            with self.subTest("calls get account details on rest client"):
                mock_rest_client.return_value.get_account_details.assert_called_with(account)
            with self.subTest("returns the result of mapping"):
                self.assertIsNotNone(response)

    @does_asyncio
    @patch("octopus_energy.client.OctopusEnergyRestClient", autospec=True)
    @patch("octopus_energy.client.consumption_from_response", autospec=True)
    async def test_get_consumption(self, mock_mapper: Mock, mock_rest_client: Mock):
        mpxn = "mpxn"
        sn = "sn"
        meter: Meter = Mock()
        meter.meter_point.id = mpxn
        meter.serial_number = sn

        with self.subTest("electricity meter"):
            async with OctopusEnergyConsumerClient("") as client:
                meter.energy_type = EnergyType.ELECTRICITY
                response = await client.get_consumption(meter)
                with self.subTest("calls rest client with expected parameters"):
                    mock_rest_client.return_value.get_electricity_consumption_v1.assert_called_with(
                        mpxn, sn, period_from=None, period_to=None, order=SortOrder.OLDEST_FIRST
                    )
                with self.subTest("returns the result of mapping"):
                    self.assertIsNotNone(response)

        with self.subTest("gas meter"):
            async with OctopusEnergyConsumerClient("") as client:
                meter.energy_type = EnergyType.GAS
                response = await client.get_consumption(meter)
                with self.subTest("calls rest client with expected parameters"):
                    mock_rest_client.return_value.get_gas_consumption_v1.assert_called_with(
                        mpxn, sn, period_from=None, period_to=None, order=SortOrder.OLDEST_FIRST
                    )
                with self.subTest("returns the result of mapping"):
                    self.assertIsNotNone(response)

        with self.subTest("paging support"):
            async with OctopusEnergyConsumerClient("") as client:
                meter.energy_type = EnergyType.GAS
                page_reference = PageReference(
                    {
                        "page": 1,
                        "page_size": 100,
                        "order": SortOrder.NEWEST_FIRST,
                        "group_by": Aggregate.QUARTER,
                    }
                )
                response = await client.get_consumption(meter, page_reference=page_reference)
                with self.subTest("uses page reference parameters when supplied"):
                    mock_rest_client.return_value.get_gas_consumption_v1.assert_called_with(
                        mpxn,
                        sn,
                        page=1,
                        page_size=100,
                        order=SortOrder.NEWEST_FIRST,
                        group_by=Aggregate.QUARTER,
                    )
                with self.subTest("returns the result of mapping"):
                    self.assertIsNotNone(response)

    @does_asyncio
    @patch("octopus_energy.client.OctopusEnergyRestClient", autospec=True)
    @patch("octopus_energy.client.tariff_rates_from_response", autospec=True)
    async def test_get_tariff_cost(self, mock_mapper: Mock, mock_rest_client: Mock):
        product_code = "pc"
        tariff_code = "tc"
        tariff_type = EnergyTariffType.ELECTRICITY
        rate_type = RateType.STANDARD_UNIT_RATES
        timestamp = datetime.utcnow()
        async with OctopusEnergyConsumerClient("") as client:
            response = await client.get_tariff_cost(
                product_code, tariff_code, tariff_type, rate_type, timestamp
            )
            with self.subTest("calls get_tariff_v1 on rest client"):
                mock_rest_client.return_value.get_tariff_v1.assert_called_with(
                    product_code,
                    tariff_type,
                    tariff_code,
                    rate_type,
                    period_from=timestamp,
                    period_to=timestamp + timedelta(seconds=1),
                )
            with self.subTest("returns the result of mapping"):
                self.assertIsNotNone(response)

    @does_asyncio
    @patch("octopus_energy.client.OctopusEnergyRestClient", autospec=True)
    @patch("octopus_energy.client.tariff_rates_from_response", autospec=True)
    async def test_get_daily_agile_pricing(self, mock_mapper: Mock, mock_rest_client: Mock):
        product_code = "pc"
        tariff_code = "tc"
        tariff_type = EnergyTariffType.ELECTRICITY
        rate_type = RateType.STANDARD_UNIT_RATES
        timestamp = datetime.utcnow()
        async with OctopusEnergyConsumerClient("") as client:
            response = await client.get_daily_flexible_rate_pricing(
                product_code, tariff_code, tariff_type, rate_type, timestamp
            )
            with self.subTest("calls get_tariff_v1 on rest client"):
                mock_rest_client.return_value.get_tariff_v1.assert_called_with(
                    product_code,
                    tariff_type,
                    tariff_code,
                    rate_type,
                    period_from=datetime(
                        year=timestamp.year, month=timestamp.month, day=timestamp.day
                    ),
                    period_to=datetime(
                        year=timestamp.year, month=timestamp.month, day=timestamp.day
                    )
                    + timedelta(days=1),
                )
            with self.subTest("returns the result of mapping"):
                self.assertIsNotNone(response)
