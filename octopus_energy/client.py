from typing import List

from .mappers import meters_from_response
from octopus_energy import Meter, OctopusEnergyRestClient


class OctopusEnergyConsumerClient:
    """An opinionated take on the consumer features of the Octopus Energy API.

    This client uses python model classes instead of raw json-as-a-dict. It does not expose all of
    the octopus energy API, only bits that are useful for a consumer of octopus energy products. It
    focuses on consumption and prices, and blending the two of them together to provide useful
    data for a consumer.

    This client is useful if you want to know your own personal energy consumption statistics.

    This client uses async i/o.
    """

    def __init__(self, account_number: str, api_token: str):
        """Initializes the Octopus Energy Consumer Client.

        Args:
            account_number: Your Octopus Energy Account Number.
            api_token: Your Octopus Energy API Key.
        """
        self.account_number = account_number
        self.rest_client = OctopusEnergyRestClient(api_token)

    def __enter__(self):
        raise TypeError("Use async context manager (async with) instead")

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        """Clean up resources used by the client.

        Once the client is closed, you cannot use it to make any further calls.
        """
        await self.rest_client.close()

    async def get_meters(self) -> List[Meter]:
        """Gets all meters associated with your account."""
        return meters_from_response(await self.rest_client.get_account_details(self.account_number))
