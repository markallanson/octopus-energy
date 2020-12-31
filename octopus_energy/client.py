from http import HTTPStatus
from typing import Any

import requests
from requests.auth import HTTPBasicAuth

from octopus_energy.models import UnitType, Consumption, MeterType
from octopus_energy.exceptions import ApiError, ApiAuthenticationError
from octopus_energy.mappers import consumption_from_response

_API_BASE = "https://api.octopus.energy"


class OctopusEnergyClient:
    """A client for interacting with the Octopus Energy RESTful API."""

    def __init__(self, api_token, default_unit: UnitType = UnitType.KWH):
        self.auth = HTTPBasicAuth(api_token, "")
        self.default_unit = default_unit

    def get_gas_consumption_v1(
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
        return self._execute(
            requests.get,
            f"v1/gas-meter-points/{mprn}/meters/{serial_number}/consumption/",
            consumption_from_response,
            meter_type=meter_type,
            desired_unit_type=desired_unit_type,
        )

    def get_electricity_consumption_v1(
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
        return self._execute(
            requests.get,
            f"v1/electricity-meter-points/{mpan}/meters/{serial_number}/consumption/",
            consumption_from_response,
            meter_type=meter_type,
            desired_unit_type=desired_unit_type,
        )

    def _execute(self, func, url: str, response_mapper, **kwargs) -> Any:
        """Executes an API call to Octopus energy and maps the response."""
        response = func(f"{_API_BASE}/{url}", auth=self.auth)
        if not response.ok:
            if response.status_code == HTTPStatus.UNAUTHORIZED:
                raise ApiAuthenticationError()
            raise ApiError("Error", response=response)
        return response_mapper(response, **kwargs)
