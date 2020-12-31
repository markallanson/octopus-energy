import re
from http import HTTPStatus
from unittest import TestCase

from requests_mock import Mocker

from octopus_energy import OctopusEnergyClient, MeterType, ApiAuthenticationError, ApiError

_MOCK_TOKEN = "sk_live_xxxxxx"


class ClientTest(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.client = OctopusEnergyClient(_MOCK_TOKEN)

    @Mocker()
    def test_raises_api_auth_error_when_authentication_fails(self, requests_mock):
        requests_mock.get(re.compile(".*"), status_code=HTTPStatus.UNAUTHORIZED.value)
        with self.subTest("elec consumption v1"):
            with self.assertRaises(ApiAuthenticationError):
                self.client.get_electricity_consumption_v1(
                    "mpan", "serial_number", MeterType.SMETS1_ELECTRICITY
                )
        with self.subTest("gas consumption v1"):
            with self.assertRaises(ApiAuthenticationError):
                self.client.get_gas_consumption_v1("mprn", "serial_number", MeterType.SMETS1_GAS)

    @Mocker()
    def test_raises_api_error_when_not_ok(self, requests_mock):
        requests_mock.get(re.compile(".*"), status_code=HTTPStatus.INTERNAL_SERVER_ERROR.value)
        with self.subTest("elec consumption v1"):
            with self.assertRaises(ApiError):
                self.client.get_electricity_consumption_v1(
                    "mpan", "serial_number", MeterType.SMETS1_ELECTRICITY
                )
        with self.subTest("gas consumption v1"):
            with self.assertRaises(ApiError):
                self.client.get_gas_consumption_v1("mprn", "serial_number", MeterType.SMETS1_GAS)

    @Mocker()
    def test_get_elec_consumption_v1(self, requests_mock):
        mock = requests_mock.get(
            re.compile(".*"), status_code=HTTPStatus.OK.value, json={"results": []}
        )
        self.client.get_electricity_consumption_v1(
            "mpan", "serial_number", MeterType.SMETS1_ELECTRICITY
        )
        with self.subTest("call made"):
            self.assertTrue(mock.called)
        with self.subTest("auth header supplied"):
            self.assertTrue("Authorization" in mock.last_request.headers, "has header")
            self.assertIn("Basic", mock.last_request.headers["Authorization"], "uses basic auth")

    @Mocker()
    def test_get_gas_consumption_v1(self, requests_mock):
        mock = requests_mock.get(
            re.compile(".*"), status_code=HTTPStatus.OK.value, json={"results": []}
        )
        self.client.get_electricity_consumption_v1("mpan", "serial_number", MeterType.SMETS1_GAS)
        with self.subTest("call made"):
            self.assertTrue(mock.called)
        with self.subTest("auth header supplied"):
            self.assertTrue("Authorization" in mock.last_request.headers, "has header")
            self.assertIn("Basic", mock.last_request.headers["Authorization"], "uses basic auth")
