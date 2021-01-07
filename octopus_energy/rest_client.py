from http import HTTPStatus
from typing import Any, Optional

from aiohttp import BasicAuth, ClientSession
from furl import furl

from octopus_energy.exceptions import ApiError, ApiAuthenticationError, ApiNotFoundError

_API_BASE = "https://api.octopus.energy"


class OctopusEnergyRestClient:
    """A client for interacting with the Octopus Energy RESTful API.

    This is a basic wrapper around the REST endpoints and all methods return dictionary
    representation of the response json. IT handles authentication and everything else
    related to interacting with the API endpoints. It does not do any interpretation of
    the data returned.

    This client can operate either as an async context manager, or as a regular object.
    If you use the latter ensure that you call close at the end to release any underlying
    resources this client uses.
    """

    def __init__(self, api_token: Optional[str] = None, base_url: str = _API_BASE):
        """Create a new instance of the Octopus API rest client.

        Args:
            api_token: [Optional] The API token to use to access the APIs. If not specified only
                       octopus public APIs can be called.
            base_url: The Octopus Energy API address.
        """
        self.base_url = furl(base_url)
        self.session = ClientSession(
            auth=BasicAuth(api_token, "") if api_token is not None else None
        )

    def __enter__(self):
        raise TypeError("Use async context manager (await with) instead")

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
        await self.session.close()

    async def get_account_details(self, account_number: str):
        """Gets account details for an account number.

        Note that your API key must have access to the account in order to get it's details.

        Args:
            account_number: The account number whose details are being requested

        Returns:
            A dictionary containing the account details
        """
        return await self._execute(["v1", "accounts", account_number])

    async def get_electricity_consumption_v1(self, mpan: str, serial_number: str) -> dict:
        """Gets the consumption of electricity from a specific meter.

        Args:
            mpan: The MPAN (Meter Point Administration Number) of the meter to query.
            serial_number: The serial number of the meter to query.

        Returns:
            A dictionary containing the electricity consumption response.

        """
        return await self._execute(
            ["v1", "electricity-meter-points", mpan, "meters", serial_number, "consumption"]
        )

    async def get_gas_consumption_v1(self, mprn: str, serial_number: str) -> dict:
        """Gets the consumption of gas from a specific meter.

        Args:
            mprn: The MPRN (Meter Point Reference Number) of the meter to query.
            serial_number: The serial number of the meter to query.

        Returns:
            A dictionary containing the gas consumption response.

        """
        return await self._execute(
            ["v1", "gas-meter-points", mprn, "meters", serial_number, "consumption"]
        )

    async def get_products_v1(self) -> dict:
        """Gets octopus energy products.

        Returns:
            A dictionary containing the products response.

        """
        return await self._execute(["v1", "products"])

    async def get_product_v1(self, product_code: str) -> dict:
        """Gets detailed information about a specific octopus energy product.

        Args:
            product_code: The product code to retrieve.

        Returns:
            A dictionary containing the product details response.

        """
        return await self._execute(["v1", "products", product_code])

    async def _execute(self, url_parts: list, **kwargs) -> Any:
        """Executes an API call to Octopus energy and maps the response."""
        url = self.base_url.copy()
        url.path.segments.extend(url_parts)
        response = await self.session.get(str(url), **kwargs)
        if response.status > 399:
            if response.status == HTTPStatus.UNAUTHORIZED:
                raise ApiAuthenticationError()
            if response.status == HTTPStatus.NOT_FOUND:
                raise ApiNotFoundError()
            raise ApiError(response, "API Call Failed")
        return await response.json()
