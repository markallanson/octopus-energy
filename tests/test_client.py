from unittest import TestCase
from unittest.mock import patch, Mock

from octopus_energy import OctopusEnergyConsumerClient
from tests import does_asyncio


class ClientTestCase(TestCase):
    def test_cannot_use_client_without_async(self):
        with self.assertRaises(TypeError):
            with OctopusEnergyConsumerClient("", ""):
                pass

    @does_asyncio
    @patch("octopus_energy.client.OctopusEnergyRestClient", autospec=True)
    async def test_init(self, mock_rest_client: Mock):
        account_number = "A_BVC"
        api_token = "A_BVC"
        async with OctopusEnergyConsumerClient(account_number, api_token) as client:
            with self.subTest("remembers account number"):
                self.assertEqual(client.account_number, account_number)
            with self.subTest("passes api token to rest client"):
                mock_rest_client.assert_called_once_with(api_token)

    @does_asyncio
    @patch("octopus_energy.client.OctopusEnergyRestClient", autospec=True)
    @patch("octopus_energy.client.meters_from_response", autospec=True)
    async def test_get_meters(self, mock_mapper: Mock, mock_rest_client: Mock):
        account = "Account"
        async with OctopusEnergyConsumerClient(account, "") as client:
            response = await client.get_meters()
            with self.subTest("calls get account details on rest client"):
                mock_rest_client.return_value.get_account_details.assert_called_with(account)
            with self.subTest("returns the result of mapping"):
                self.assertIsNotNone(response)
