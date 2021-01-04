from http import HTTPStatus
from typing import Any, Callable

import aiohttp
from aiohttp import BasicAuth

from octopus_energy.models import UnitType, Consumption, MeterType
from octopus_energy.exceptions import ApiError, ApiAuthenticationError, ApiNotFoundError
from octopus_energy.mappers import consumption_from_response

_API_BASE = "https://api.octopus.energy"


class OctopusEnergyClient:
    """A client for interacting with the Octopus Energy RESTful API."""

    def __init__(self, api_token, default_unit: UnitType = UnitType.KWH):
        self.auth = BasicAuth(api_token, "")
        self.default_unit = default_unit

    async def get_gas_consumption_v1(
        self, mprn, serial_number, meter_type: MeterType, desired_unit_type: UnitType = UnitType.KWH
    ) -> Consumption:
        """Gets the consumption of gas from a specific meter.

        Args:
            mprn: The MPRN (Meter Point Reference Number) of the meter to query
            serial_number: The serial number of the meter to query
            meter_type: The type of the meter being queried. The octopus energy API does not tell
                        us what the type of meter is, so we need to define this in the request
                        to query.
            desired_unit_type: The desired units you want the results in. This defaults to
                               Kilowatt Hours.

        Returns:
            The consumption of gas for the meter.

        """
        return await self._execute(
            f"v1/gas-meter-points/{mprn}/meters/{serial_number}/consumption/",
            consumption_from_response,
            meter_type=meter_type,
            desired_unit_type=desired_unit_type,
        )

    async def get_electricity_consumption_v1(
        self,
        mpan: str,
        serial_number: str,
        meter_type: MeterType,
        desired_unit_type: UnitType = UnitType.KWH,
    ) -> Consumption:
        """Gets the consumption of electricity from a specific meter.

        Args:
            mpan: The MPAN (Meter Point Administration Number) of the meter to query
            serial_number: The serial number of the meter to query
            meter_type: The type of the meter being queried. The octopus energy API does not tell
                        us what the type of meter is, so we need to define this in the request to
                        query.
            desired_unit_type: The desired units you want the results in. This defaults to
                               Kilowatt Hours.

        Returns:
            The consumption of gas for the meter.

        """
        return await self._execute(
            f"v1/electricity-meter-points/{mpan}/meters/{serial_number}/consumption/",
            consumption_from_response,
            meter_type=meter_type,
            desired_unit_type=desired_unit_type,
        )

    async def _execute(self, url: str, response_mapper: Callable[[dict], Any], **kwargs) -> Any:
        """Executes an API call to Octopus energy and maps the response."""
        async with aiohttp.ClientSession(auth=self.auth) as session:
            response = await session.get(f"{_API_BASE}/{url}")
            if response.status > 399:
                if response.status == HTTPStatus.UNAUTHORIZED:
                    raise ApiAuthenticationError()
                if response.status == HTTPStatus.NOT_FOUND:
                    raise ApiNotFoundError()
                raise ApiError(response, "API Call Failed")
            return response_mapper(await response.json(), **kwargs)
