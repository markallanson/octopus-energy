from datetime import datetime
from functools import partial
from http import HTTPStatus
from typing import Optional, Callable

from aiohttp import BasicAuth, ClientSession
from furl import furl

from .mappers import to_timestamp_str
from .exceptions import (
    ApiError,
    ApiAuthenticationError,
    ApiNotFoundError,
    ApiBadRequestError,
)
from .models import RateType, EnergyTariffType, Aggregate, SortOrder

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

    async def get_electricity_consumption_v1(
        self,
        mpan: str,
        serial_number: str,
        page_num: int = None,
        page_size: int = None,
        period_from: datetime = None,
        period_to: datetime = None,
        order: SortOrder = None,
        aggregate: Aggregate = None,
    ) -> dict:
        """Gets the consumption of electricity from a specific meter.

        Args:
            mpan: The MPAN (Meter Point Administration Number) of the location to query.
            serial_number: The serial number of the meter to query.
            page_num: (Optional) The page number to load.
            page_size: (Optional) How many results per page.
            period_from: (Optional) The timestamp from where to begin returning results.
            period_to: (Optional) The timestamp at which to end returning results.
            order: (Optional) The ordering to apply to the results.
            aggregate: (Optional) Over what period to aggregate the results. By default consumption
                       results are aggregated half hourly. You can override this setting by
                       explicitly stating an alternate aggregate.
        Returns:
            A dictionary containing the electricity consumption response.

        """
        return await self._get(
            ["v1", "electricity-meter-points", mpan, "meters", serial_number, "consumption"],
            {
                "page": page_num,
                "page_size": page_size,
                "period_from": to_timestamp_str(period_from),
                "period_to": to_timestamp_str(period_to),
                "order": order.value if order is not None else None,
                "group_by": aggregate.value if aggregate is not None else None,
            },
        )

    async def get_electricity_meter_points_v1(self, mpan: str) -> dict:
        """Gets the Grid Supply Point (GSP) of electricity at a location.

        Args:
            mpan: The MPAN (Meter Point Administration Number) of the location to query.

        Returns:
            A dictionary containing the meters at the location.

        """
        return await self._get(["v1", "electricity-meter-points", mpan])

    async def get_gas_consumption_v1(
        self,
        mprn: str,
        serial_number: str,
        page_num: int = None,
        page_size: int = None,
        period_from: datetime = None,
        period_to: datetime = None,
        order: SortOrder = None,
        aggregate: Aggregate = None,
    ) -> dict:
        """Gets the consumption of gas from a specific meter.

        Args:
            mprn: The MPRN (Meter Point Reference Number) of the location to query.
            serial_number: The serial number of the meter to query.
            page_num: (Optional) The page number to load.
            page_size: (Optional) How many results per page.
            period_from: (Optional) The timestamp from where to begin returning results.
            period_to: (Optional) The timestamp at which to end returning results.
            order: (Optional) The ordering to apply to the results.
            aggregate: (Optional) Over what period to aggregate the results. By default consumption
                       results are aggregated half hourly. You can override this setting by
                       explicitly stating an alternate aggregate.
        Returns:
            A dictionary containing the gas consumption response.

        """
        return await self._get(
            ["v1", "gas-meter-points", mprn, "meters", serial_number, "consumption"],
            {
                "page": page_num,
                "page_size": page_size,
                "period_from": to_timestamp_str(period_from),
                "period_to": to_timestamp_str(period_to),
                "order": order.value if order is not None else None,
                "group_by": aggregate.value if aggregate is not None else None,
            },
        )

    async def get_products_v1(
        self,
        page_num: int = None,
        page_size: int = None,
        is_variable: bool = None,
        is_green: bool = None,
        is_tracker: bool = None,
        is_prepay: bool = None,
        is_business: bool = None,
        available_at: datetime = None,
    ) -> dict:
        """Gets octopus energy products.

        Args:
            page_num: (Optional) The page number to load.
            page_size: (Optional) How many results per page.
            is_variable (Optional): Activate filter and include variable products in the results.
            is_green (Optional): Activate filter and include green products in the results.
            is_tracker (Optional): Activate filter and include tracker products in the results.
            is_prepay (Optional): Activate filter and include prepay products in the results.
            is_business (Optional): Activate filter and include business products in the results.
            available_at (Optional): Include products available for new agreements on the given
                                     timestamp. Defaults to current datetime, effectively showing
                                     products that are currently available.

        Returns:
            A dictionary containing the products response.

        """
        return await self._get(
            ["v1", "products"],
            {
                "page": page_num,
                "page_size": page_size,
                "is_variable": is_variable,
                "is_green": is_green,
                "is_tracker": is_tracker,
                "is_prepay": is_prepay,
                "is_business": is_business,
                "available_at": to_timestamp_str(available_at) if available_at else None,
            },
        )

    async def get_product_v1(self, product_code: str, tariffs_active_at: datetime = None) -> dict:
        """Gets detailed information about a specific octopus energy product.

        Args:
            product_code: The product code to retrieve.
            tariffs_active_at (Optional): If specified, returns the tariff rates at the timestamp
                                          requested.

        Returns:
            A dictionary containing the product details response.

        """
        return await self._get(
            ["v1", "products", product_code],
            {
                "tariffs_active_at": to_timestamp_str(tariffs_active_at)
                if tariffs_active_at is not None
                else None
            },
        )

    async def get_tariff_v1(
        self,
        product_code: str,
        tariff_type: EnergyTariffType,
        tariff_code: str,
        rate_type: RateType,
        page_num: int = None,
        page_size: int = None,
        period_from: datetime = None,
        period_to: datetime = None,
    ) -> dict:
        """Gets tariff information about a specific octopus energy tariff.

        Args:
            product_code: The product code the tariff belongs to.
            tariff_type: The type of tariff to get the details of.
            tariff_code: The tariff code to get the details of.
            rate_type: The rate within the tariff to retrieve.
            page_num: (Optional) The page number to load.
            page_size: (Optional) How many results per page.
            period_from: (Optional) The timestamp (inclusive) from where to begin returning results.
            period_to: (Optional) The timestamp (exclusive) at which to end returning results.

        Returns:
            A dictionary containing the tariff details response.

        """
        return await self._get(
            ["v1", "products", product_code, tariff_type.value, tariff_code, rate_type.value],
            {
                "page": page_num,
                "page_size": page_size,
                "period_from": to_timestamp_str(period_from),
                "period_to": to_timestamp_str(period_to),
            },
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

    async def _get(self, url_parts: list, query_params: dict = {}, **kwargs) -> dict:
        return await self._execute(self.session.get, url_parts, query_params, **kwargs)

    async def _post(self, url_parts: list, data: dict, query_params: dict = {}, **kwargs) -> dict:
        return await self._execute(
            partial(self.session.post, data=data), url_parts, query_params, **kwargs
        )

    async def _execute(
        self, func: Callable, url_parts: list, query_params: dict = {}, **kwargs
    ) -> dict:
        """Executes an API call to Octopus energy and maps the response."""
        url = self.base_url.copy()
        url.path.segments.extend(url_parts)
        url.query.params.update({p: v for p, v in query_params.items() if v is not None})
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
