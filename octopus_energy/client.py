from datetime import datetime, timedelta
from typing import List, Optional

from .mappers import meters_from_response, consumption_from_response, tariff_rates_from_response
from octopus_energy import (
    Meter,
    OctopusEnergyRestClient,
    Consumption,
    EnergyType,
    SortOrder,
    PageReference,
    EnergyTariffType,
    RateType,
    TariffRate,
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

    def __init__(self, api_token: Optional[str] = None):
        """Initializes the Octopus Energy Consumer Client.

        Args:
            api_token: Your Octopus Energy API Key.
        """
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

    async def get_meters(self, account_number: str) -> List[Meter]:
        """Gets all meters associated with your account.

        Args:
            account_number: Your Octopus Energy Account Number.
        """
        return meters_from_response(await self.rest_client.get_account_details(account_number))

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

    async def get_tariff_cost(
        self,
        product_code: str,
        tariff_code: str,
        tariff_type: EnergyTariffType,
        rate_type: RateType,
        timestamp: datetime,
    ) -> Optional[TariffRate]:
        """Gets the cost of a tariff cost at a point in time.

        Args:
            product_code: The product code.
            tariff_code: The tariff code.
            tariff_type: The type of energy within the tariff.
            rate_type: The type of rate.
            timestamp: The timestamp.

        Returns:
            The cost per unit of energy for the requested rate at a point in time.

        """
        response = await self.rest_client.get_tariff_v1(
            product_code,
            tariff_type,
            tariff_code,
            rate_type,
            period_from=timestamp,
            # Add a millisecond as the API doesn't like requests with the same start and end
            period_to=timestamp + timedelta(seconds=1),
        )
        rates = tariff_rates_from_response(response)
        return None if not rates else rates[0]

    async def get_daily_flexible_rate_pricing(
        self,
        product_code: str,
        tariff_code: str,
        tariff_type: EnergyTariffType,
        rate_type: RateType,
        timestamp: datetime,
    ) -> List[TariffRate]:
        """Gets the cost of a flexible rate tariff for each half hour interval on a specific day.

        Note that this will yield indeterminate/meaningless results for standard but it may work,
        OK for "go" tariffs which do change price during the course of the day.

        Args:
            product_code: The product code.
            tariff_code: The tariff code.
            tariff_type: The type of energy within the tariff.
            rate_type: The type of rate.
            timestamp: The timestamp whose date portion will be used to determine which day to
                       get the pricing for. The start date will be the truncated date time, and
                       the end period will be midnight on the truncated date time.

        Returns:
            The cost per unit of energy for the requested rate for the day requested.

        """
        period_from = datetime(year=timestamp.year, month=timestamp.month, day=timestamp.day)
        response = await self.rest_client.get_tariff_v1(
            product_code,
            tariff_type,
            tariff_code,
            rate_type,
            period_from=period_from,
            period_to=period_from + timedelta(days=1),
        )
        rates = tariff_rates_from_response(response)
        return rates
