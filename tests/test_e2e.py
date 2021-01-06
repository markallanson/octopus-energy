import asyncio
from unittest import TestCase

from aioresponses import aioresponses

from octopus_energy import OctopusEnergyRestClient, MeterType
from octopus_energy.rest_client import _API_BASE
from tests import load_fixture_json

_FAKE_API_TOKEN = "sk_live_xxxxxxxxxxxx"


class E2eTests(TestCase):
    def setUp(self) -> None:
        super().setUp()

    @aioresponses()
    def test_get_gas_consumption_v1(self, aiomock: aioresponses):
        aiomock.get(
            f"{_API_BASE}/v1/gas-meter-points/mprn/meters/serial_number/consumption",
            payload=load_fixture_json("consumption_response.json"),
        )
        loop = asyncio.get_event_loop()

        async def get():
            async with OctopusEnergyRestClient(_FAKE_API_TOKEN) as client:
                return await client.get_gas_consumption_v1("mprn", "serial_number")

        response = loop.run_until_complete(get())
        self.assertEqual(response, load_fixture_json("consumption_response.json"))

    @aioresponses()
    def test_get_elec_consumption_v1(self, aiomock: aioresponses):
        aiomock.get(
            f"{_API_BASE}/v1/electricity-meter-points/mpan/meters/serial_number/consumption",
            payload=load_fixture_json("consumption_response.json"),
        )
        loop = asyncio.get_event_loop()

        async def get():
            async with OctopusEnergyRestClient(_FAKE_API_TOKEN) as client:
                return await client.get_electricity_consumption_v1("mpan", "serial_number")

        response = loop.run_until_complete(get())
        self.assertEqual(response, load_fixture_json("consumption_response.json"))
