import re
from asyncio import get_event_loop
from http import HTTPStatus
from unittest import TestCase

from aioresponses import aioresponses

from octopus_energy import (
    OctopusEnergyClient,
    MeterType,
    ApiAuthenticationError,
    ApiError,
    ApiNotFoundError,
)

_MOCK_TOKEN = "sk_live_xxxxxx"


class ClientTest(TestCase):
    def setUp(self) -> None:
        super().setUp()
        # self.client = OctopusEnergyClient(_MOCK_TOKEN)
        self.client = OctopusEnergyClient("sk_live_kCF8cGXPuMu5tJrIaQEn84CL")

    @aioresponses()
    def test_raises_api_auth_error_when_authentication_fails(self, aiomock: aioresponses):
        with self.subTest("elec consumption v1"):
            with self.assertRaises(ApiAuthenticationError):
                aiomock.get(re.compile(".*"), status=HTTPStatus.UNAUTHORIZED.value)
                get_event_loop().run_until_complete(
                    self.client.get_electricity_consumption_v1(
                        "mpan", "serial_number", MeterType.SMETS1_ELECTRICITY
                    )
                )
        with self.subTest("gas consumption v1"):
            with self.assertRaises(ApiAuthenticationError):
                aiomock.get(re.compile(".*"), status=HTTPStatus.UNAUTHORIZED.value)
                get_event_loop().run_until_complete(
                    self.client.get_gas_consumption_v1(
                        "mprn", "serial_number", MeterType.SMETS1_GAS
                    )
                )

    @aioresponses()
    def test_raises_api_error_when_not_ok(self, aiomock: aioresponses):
        with self.subTest("elec consumption v1"):
            with self.assertRaises(ApiError):
                aiomock.get(re.compile(".*"), status=HTTPStatus.INTERNAL_SERVER_ERROR.value)
                get_event_loop().run_until_complete(
                    self.client.get_electricity_consumption_v1(
                        "mpan", "serial_number", MeterType.SMETS1_ELECTRICITY
                    )
                )
        with self.subTest("gas consumption v1"):
            with self.assertRaises(ApiError):
                aiomock.get(re.compile(".*"), status=HTTPStatus.INTERNAL_SERVER_ERROR.value)
                get_event_loop().run_until_complete(
                    self.client.get_gas_consumption_v1(
                        "mprn", "serial_number", MeterType.SMETS1_GAS
                    )
                )

    @aioresponses()
    def test_raises_not_found_api_error_when_not_ok(self, aiomock: aioresponses):
        with self.subTest("elec consumption v1"):
            with self.assertRaises(ApiNotFoundError):
                aiomock.get(re.compile(".*"), status=HTTPStatus.NOT_FOUND.value)
                get_event_loop().run_until_complete(
                    self.client.get_electricity_consumption_v1(
                        "mpan", "serial_number", MeterType.SMETS1_ELECTRICITY
                    )
                )
        with self.subTest("gas consumption v1"):
            with self.assertRaises(ApiNotFoundError):
                aiomock.get(re.compile(".*"), status=HTTPStatus.NOT_FOUND.value)
                get_event_loop().run_until_complete(
                    self.client.get_gas_consumption_v1(
                        "mprn", "serial_number", MeterType.SMETS1_GAS
                    )
                )

    @aioresponses()
    def test_get_elec_consumption_v1(self, aiomock: aioresponses):
        aiomock.get(re.compile(".*"), status=HTTPStatus.OK.value, payload={"results": []})
        resp = get_event_loop().run_until_complete(
            self.client.get_electricity_consumption_v1(
                "mpan", "serial_number", MeterType.SMETS1_ELECTRICITY
            )
        )
        with self.subTest("call made"):
            self.assertEqual(len(aiomock.requests), 1)
        with self.subTest("response returned"):
            self.assertIsNotNone(resp)

    @aioresponses()
    def test_get_gas_consumption_v1(self, aiomock: aioresponses):
        aiomock.get(re.compile(".*"), status=HTTPStatus.OK.value, payload={"results": []})
        resp = get_event_loop().run_until_complete(
            self.client.get_electricity_consumption_v1(
                "mpan", "serial_number", MeterType.SMETS1_GAS
            )
        )
        with self.subTest("call made"):
            self.assertEqual(len(aiomock.requests), 1)
        with self.subTest("response returned"):
            self.assertIsNotNone(resp)