from datetime import datetime
from typing import List

from .mappers import meters_from_response, consumption_from_response
from octopus_energy import (
    Meter,
    OctopusEnergyRestClient,
    Consumption,
    EnergyType,
    SortOrder,
    PageReference,
)


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

    async def get_consumption(
        self,
        meter: Meter,
        period_from: datetime = None,
        period_to: datetime = None,
        page_reference: PageReference = None,
    ) -> Consumption:
        """Get the energy consumption for a meter

        Args:
            meter: The meter to get consumption for.
            period_from: The timestamp for the earliest period of consumption to return.
            period_to: The timestamp for the latest period of consumption to return.
            page_reference: Get a specific page of results based on a page reference returned by
                            a previous call to get_consumption

        Returns:
            The consumption for the meter in the time period specified. The results are returned
            in ascending timestamp order from the start of the period.

        """
        func = (
            self.rest_client.get_electricity_consumption_v1
            if meter.energy_type == EnergyType.ELECTRICITY
            else self.rest_client.get_gas_consumption_v1
        )

        params = {}
        if page_reference:
            params.update(page_reference.options)
        else:
            params.update(
                {
                    "period_from": period_from,
                    "period_to": period_to,
                    "order": SortOrder.OLDEST_FIRST,
                }
            )

        response = await func(meter.meter_point.id, meter.serial_number, **params)
        return consumption_from_response(response, meter)
