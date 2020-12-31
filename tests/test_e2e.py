import re
from unittest import TestCase

from requests_mock import Mocker

from octopus_energy import OctopusEnergyClient, MeterType
from octopus_energy.client import _API_BASE
from tests import load_fixture

_FAKE_API_TOKEN = "sk_live_xxxxxxxxxxxx"


class E2eTests(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.client = OctopusEnergyClient(_FAKE_API_TOKEN)

    @Mocker()
    def test_get_gas_consumption_v1(self, requests_mock: Mocker):
        requests_mock.get(
            re.compile(f"{_API_BASE}/v1/gas-meter-points/mprn/meters/serial_number/consumption/"),
            text=load_fixture("consumption_response.json"),
        )
        response = self.client.get_gas_consumption_v1("mprn", "serial_number", MeterType.SMETS1_GAS)
        self.assertEqual(len(response.intervals), 3)

    @Mocker()
    def test_get_elec_consumption_v1(self, requests_mock: Mocker):
        requests_mock.get(
            re.compile(
                f"{_API_BASE}/v1/electricity-meter-points/mpan/meters/serial_number/consumption/"
            ),
            text=load_fixture("consumption_response.json"),
        )
        response = self.client.get_electricity_consumption_v1(
            "mpan", "serial_number", MeterType.SMETS1_ELECTRICITY
        )
        self.assertEqual(len(response.intervals), 3)
