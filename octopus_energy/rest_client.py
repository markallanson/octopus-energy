from functools import partial
from http import HTTPStatus
from typing import Optional, Callable

from aiohttp import BasicAuth, ClientSession
from furl import furl

from octopus_energy.exceptions import (
    ApiError,
    ApiAuthenticationError,
    ApiNotFoundError,
    ApiBadRequestError,
)
from octopus_energy.models import RateType, EnergyTariffType

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

    async def create_account(self, account_data: dict) -> dict:
        """Creates an account.

        Note that your API key must be a partner organisation API key in order for this API to
        correctly function.

        Args:
            account_data: The information required to create an account. The format is documented
                          in the octopus energy API documentation located at
                          https://developer.octopus.energy/docs/api/#create-an-account

        Returns:
            A dictionary containing the account creation response.
        """
        return await self._post(["v1", "accounts"], account_data)

    async def create_quote(self, quote_data: dict) -> dict:
        """Creates an energy quote.

        Note that your API key must be a partner organisation API key in order for this API to
        correctly function.

        Args:
            quote_data: The information required to generate a quote. The format is documented
                        in the octopus energy API documentation located at
                        https://developer.octopus.energy/docs/api/#quotes

        Returns:
            A dictionary containing the quote creation response.
        """
        return await self._post(["v1", "quotes"], quote_data)

    async def get_account_details(self, account_number: str) -> dict:
        """Gets account details for an account number.

        Note that your API key must have access to the account in order to get it's details.

        Args:
            account_number: The account number whose details are being requested

        Returns:
            A dictionary containing the account details
        """
        return await self._get(["v1", "accounts", account_number])

    async def get_electricity_consumption_v1(self, mpan: str, serial_number: str) -> dict:
        """Gets the consumption of electricity from a specific meter.

        Args:
            mpan: The MPAN (Meter Point Administration Number) of the location to query.
            serial_number: The serial number of the meter to query.

        Returns:
            A dictionary containing the electricity consumption response.

        """
        return await self._get(
            ["v1", "electricity-meter-points", mpan, "meters", serial_number, "consumption"]
        )

    async def get_electricity_meter_points_v1(self, mpan: str) -> dict:
        """Gets the Grid Supply Point (GSP) of electricity at a location.

        Args:
            mpan: The MPAN (Meter Point Administration Number) of the location to query.

        Returns:
            A dictionary containing the meters at the location.

        """
        return await self._get(["v1", "electricity-meter-points", mpan])

    async def get_gas_consumption_v1(self, mprn: str, serial_number: str) -> dict:
        """Gets the consumption of gas from a specific meter.

        Args:
            mprn: The MPRN (Meter Point Reference Number) of the location to query.
            serial_number: The serial number of the meter to query.

        Returns:
            A dictionary containing the gas consumption response.

        """
        return await self._get(
            ["v1", "gas-meter-points", mprn, "meters", serial_number, "consumption"]
        )

    async def get_products_v1(self) -> dict:
        """Gets octopus energy products.

        Returns:
            A dictionary containing the products response.

        """
        return await self._get(["v1", "products"])

    async def get_product_v1(self, product_code: str) -> dict:
        """Gets detailed information about a specific octopus energy product.

        Args:
            product_code: The product code to retrieve.

        Returns:
            A dictionary containing the product details response.

        """
        return await self._get(["v1", "products", product_code])

    async def get_tariff_v1(
        self,
        product_code: str,
        tariff_type: EnergyTariffType,
        tariff_code: str,
        rate_type: RateType,
    ) -> dict:
        """Gets tariff information about a specific octopus energy tariff.

        Args:
            product_code: The product code the tariff belongs to.
            tariff_type: The type of tariff to get the details of.
            tariff_code: The tariff code to get the details of.
            rate_type: The rate within the tariff to retrieve.

        Returns:
            A dictionary containing the tariff details response.

        """
        return await self._get(
            ["v1", "products", product_code, tariff_type.value, tariff_code, rate_type.value]
        )

    async def renew_business_tariff(self, account_number: str, renewal_data: dict) -> dict:
        """Creates an account.

        Note that your API key must be a partner organisation API key in order for this API to
        correctly function.

        Args:
            account_number: The account number to renew.
            renewal_data: The renewal information. The format is documented in the octopus energy
                          API documentation located at
                          https://developer.octopus.energy/docs/api/#business-tariff-renewal

        Returns:
            A dictionary containing the account creation response.
        """
        return await self._post(["v1", "accounts", account_number, "tariff-renewal"], renewal_data)

    async def _get(self, url_parts: list, **kwargs) -> dict:
        return await self._execute(self.session.get, url_parts, **kwargs)

    async def _post(self, url_parts: list, data: dict, **kwargs) -> dict:
        return await self._execute(partial(self.session.post, data=data), url_parts, **kwargs)

    async def _execute(self, func: Callable, url_parts: list, **kwargs) -> dict:
        """Executes an API call to Octopus energy and maps the response."""
        url = self.base_url.copy()
        url.path.segments.extend(url_parts)
        response = await func(url=str(url), **kwargs)
        if response.status > 399:
            if response.status == HTTPStatus.UNAUTHORIZED:
                raise ApiAuthenticationError()
            if response.status == HTTPStatus.NOT_FOUND:
                raise ApiNotFoundError()
            if response.status == HTTPStatus.BAD_REQUEST:
                raise ApiBadRequestError()
            raise ApiError(response, "API Call Failed")
        return await response.json()
