import asyncio
from typing import Callable
from unittest import TestCase

from aioresponses import aioresponses

from octopus_energy import OctopusEnergyRestClient
from octopus_energy.rest_client import _API_BASE
from tests import load_fixture_json

_FAKE_API_TOKEN = "sk_live_xxxxxxxxxxxx"


class E2eTests(TestCase):
    def setUp(self) -> None:
        super().setUp()

    @aioresponses()
    def test_get_account_details_v1(self, aiomock: aioresponses):
        async def get():
            async with OctopusEnergyRestClient(_FAKE_API_TOKEN) as client:
                return await client.get_account_details("account_number")

        self._run_test("v1/accounts/account_number", "account_response.json", get, aiomock)

    @aioresponses()
    def test_get_elec_consumption_v1(self, aiomock: aioresponses):
        async def get():
            async with OctopusEnergyRestClient(_FAKE_API_TOKEN) as client:
                return await client.get_electricity_consumption_v1("mpan", "serial_number")

        self._run_test(
            "v1/electricity-meter-points/mpan/meters/serial_number/consumption",
            "consumption_response.json",
            get,
            aiomock,
        )

    @aioresponses()
    def test_get_gas_consumption_v1(self, aiomock: aioresponses):
        async def get():
            async with OctopusEnergyRestClient(_FAKE_API_TOKEN) as client:
                return await client.get_gas_consumption_v1("mprn", "serial_number")

        self._run_test(
            "v1/gas-meter-points/mprn/meters/serial_number/consumption",
            "consumption_response.json",
            get,
            aiomock,
        )

    @aioresponses()
    def test_get_products_v1(self, aiomock: aioresponses):
        async def get():
            async with OctopusEnergyRestClient(_FAKE_API_TOKEN) as client:
                return await client.get_products_v1()

        self._run_test("v1/products", "get_products_response.json", get, aiomock)

    @aioresponses()
    def test_get_product_v1(self, aiomock: aioresponses):
        async def get():
            async with OctopusEnergyRestClient(_FAKE_API_TOKEN) as client:
                return await client.get_product_v1("product_id")

        self._run_test("v1/products/product_id", "get_product_response.json", get, aiomock)

    def _run_test(self, path: str, response_resource: str, func: Callable, aiomock: aioresponses):
        aiomock.get(
            f"{_API_BASE}/{path}",
            payload=load_fixture_json(response_resource),
        )
        loop = asyncio.get_event_loop()

        response = loop.run_until_complete(func())
        self.assertEqual(response, load_fixture_json(response_resource))
