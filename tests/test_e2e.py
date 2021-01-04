import asyncio
from unittest import TestCase

from aioresponses import aioresponses

from octopus_energy import OctopusEnergyClient, MeterType
from octopus_energy.client import _API_BASE
from tests import load_fixture_json

_FAKE_API_TOKEN = "sk_live_xxxxxxxxxxxx"


class E2eTests(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.client = OctopusEnergyClient(_FAKE_API_TOKEN)

    @aioresponses()
    def test_get_gas_consumption_v1(self, aiomock: aioresponses):
        aiomock.get(
            f"{_API_BASE}/v1/gas-meter-points/mprn/meters/serial_number/consumption/",
            payload=load_fixture_json("consumption_response.json"),
        )
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self.client.get_gas_consumption_v1("mprn", "serial_number", MeterType.SMETS1_GAS)
        )
        self.assertEqual(len(response.intervals), 3)

    @aioresponses()
    def test_get_elec_consumption_v1(self, aiomock: aioresponses):
        aiomock.get(
            f"{_API_BASE}/v1/electricity-meter-points/mpan/meters/serial_number/consumption/",
            payload=load_fixture_json("consumption_response.json"),
        )
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self.client.get_electricity_consumption_v1(
                "mpan", "serial_number", MeterType.SMETS1_ELECTRICITY
            )
        )
        self.assertEqual(len(response.intervals), 3)
