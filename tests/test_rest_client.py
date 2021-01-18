import re
from http import HTTPStatus
from unittest import TestCase

from aioresponses import aioresponses

from octopus_energy import (
    OctopusEnergyRestClient,
    ApiAuthenticationError,
    ApiError,
    ApiNotFoundError,
    ApiBadRequestError,
)
from tests import does_asyncio

_MOCK_TOKEN = "sk_live_xxxxxx"


class ClientTest(TestCase):
    def setUp(self) -> None:
        super().setUp()

    @staticmethod
    async def get_electricity_consumption_v1() -> dict:
        async with OctopusEnergyRestClient(_MOCK_TOKEN) as client:
            return await client.get_electricity_consumption_v1("mpan", "serial_number")

    @staticmethod
    async def get_gas_consumption_v1() -> dict:
        async with OctopusEnergyRestClient(_MOCK_TOKEN) as client:
            return await client.get_gas_consumption_v1("mprn", "serial_number")

    @does_asyncio
    @aioresponses()
    async def test_raises_api_auth_error_when_authentication_fails(self, mock_aioresponses):
        with self.subTest("elec consumption v1"):
            with self.assertRaises(ApiAuthenticationError):
                mock_aioresponses.get(re.compile(".*"), status=HTTPStatus.UNAUTHORIZED.value)
                await self.get_electricity_consumption_v1()

        with self.subTest("gas consumption v1"):
            with self.assertRaises(ApiAuthenticationError):
                mock_aioresponses.get(re.compile(".*"), status=HTTPStatus.UNAUTHORIZED.value)
                await self.get_gas_consumption_v1()

    @does_asyncio
    @aioresponses()
    async def test_raises_api_error_when_not_ok(self, aiomock: aioresponses):
        with self.subTest("elec consumption v1"):
            with self.assertRaises(ApiError):
                aiomock.get(re.compile(".*"), status=HTTPStatus.INTERNAL_SERVER_ERROR.value)
                await self.get_electricity_consumption_v1()

        with self.subTest("gas consumption v1"):
            with self.assertRaises(ApiError):
                aiomock.get(re.compile(".*"), status=HTTPStatus.INTERNAL_SERVER_ERROR.value)
                await self.get_gas_consumption_v1()

    @does_asyncio
    @aioresponses()
    async def test_raises_not_found_api_error_when_not_ok(self, aiomock: aioresponses):
        with self.subTest("elec consumption v1"):
            with self.assertRaises(ApiNotFoundError):
                aiomock.get(re.compile(".*"), status=HTTPStatus.NOT_FOUND.value)
                await self.get_electricity_consumption_v1()

        with self.subTest("gas consumption v1"):
            with self.assertRaises(ApiNotFoundError):
                aiomock.get(re.compile(".*"), status=HTTPStatus.NOT_FOUND.value)
                await self.get_gas_consumption_v1()

    @does_asyncio
    @aioresponses()
    async def test_raises_bad_request_api_error_when_not_ok(self, aiomock: aioresponses):
        with self.subTest("elec consumption v1"):
            with self.assertRaises(ApiBadRequestError):
                aiomock.get(re.compile(".*"), status=HTTPStatus.BAD_REQUEST.value)
                await self.get_electricity_consumption_v1()

        with self.subTest("gas consumption v1"):
            with self.assertRaises(ApiBadRequestError):
                aiomock.get(re.compile(".*"), status=HTTPStatus.BAD_REQUEST.value)
                await self.get_gas_consumption_v1()

    def test_cannot_use_client_without_async(self):
        with self.assertRaises(TypeError):
            with OctopusEnergyRestClient(""):
                pass
