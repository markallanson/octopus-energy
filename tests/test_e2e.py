from datetime import datetime
from typing import Callable

import pytest
from aioresponses import aioresponses
from dateutil.tz import tzoffset
from freezegun import freeze_time

from octopus_energy import OctopusEnergyRestClient
from octopus_energy.models import EnergyTariffType, RateType, SortOrder, Aggregate
from octopus_energy.rest_client import _API_BASE
from tests import load_fixture_json

_FAKE_API_TOKEN = "sk_live_xxxxxxxxxxxx"


@pytest.fixture
def mock_aioresponses():
    with aioresponses() as mock_aioresponses:
        yield mock_aioresponses


@pytest.mark.asyncio
async def test_create_account_v1(mock_aioresponses: aioresponses):
    async def post(client, request):
        return await client.create_account(request)

    await _run_post_test(
        "v1/accounts",
        "create_account_request.json",
        "create_account_response.json",
        post,
        mock_aioresponses,
    )


@pytest.mark.asyncio
async def test_create_quote_v1(mock_aioresponses: aioresponses):
    async def post(client, request):
        return await client.create_quote(request)

    await _run_post_test(
        "v1/quotes",
        "create_quote_request.json",
        "create_quote_response.json",
        post,
        mock_aioresponses,
    )


@pytest.mark.asyncio
async def test_get_account_details_v1(mock_aioresponses: aioresponses):
    async def get(client):
        return await client.get_account_details("account_number")

    await _run_get_test(
        "v1/accounts/account_number", "account_response.json", get, mock_aioresponses
    )


@freeze_time("2021-01-01 01:11:11")
@pytest.mark.asyncio
async def test_get_elec_consumption_v1(mock_aioresponses: aioresponses):
    async def get(client):
        return await client.get_electricity_consumption_v1(
            "mpan",
            "serial_number",
            page_num=1,
            page_size=10,
            period_from=datetime.now(tz=tzoffset("CEST", 2)),
            period_to=datetime.now(tz=tzoffset("CEST", 2)),
            order=SortOrder.NEWEST_FIRST,
            aggregate=Aggregate.DAY,
        )

    await _run_get_test(
        "v1/electricity-meter-points/mpan/meters/serial_number/consumption?page=1&page_size=10"
        "&period_from=2021-01-01T01%3A11%3A13%2B00%3A00%3A02"
        "&period_to=2021-01-01T01%3A11%3A13%2B00%3A00%3A02&order=-period&group_by=day",
        "consumption_response.json",
        get,
        mock_aioresponses,
    )


@pytest.mark.asyncio
async def test_get_electricity_meter_points_v1(mock_aioresponses: aioresponses):
    async def get(client):
        return await client.get_electricity_meter_points_v1("mpan")

    await _run_get_test(
        "v1/electricity-meter-points/mpan",
        "get_electricity_meter_points.json",
        get,
        mock_aioresponses,
    )


@freeze_time("2021-01-01 01:11:11")
@pytest.mark.asyncio
async def test_get_gas_consumption_v1(mock_aioresponses: aioresponses):
    async def get(client):
        return await client.get_gas_consumption_v1(
            "mprn",
            "serial_number",
            page_num=1,
            page_size=10,
            period_from=datetime.now(tz=tzoffset("CEST", 2)),
            period_to=datetime.now(tz=tzoffset("CEST", 2)),
            order=SortOrder.NEWEST_FIRST,
            aggregate=Aggregate.DAY,
        )

    await _run_get_test(
        "v1/gas-meter-points/mprn/meters/serial_number/consumption?page=1&page_size=10"
        "&period_from=2021-01-01T01%3A11%3A13%2B00%3A00%3A02"
        "&period_to=2021-01-01T01%3A11%3A13%2B00%3A00%3A02&order=-period&group_by=day",
        "consumption_response.json",
        get,
        mock_aioresponses,
    )


@pytest.mark.asyncio
async def test_get_products_v1(mock_aioresponses: aioresponses):
    async def get(client):
        return await client.get_products_v1()

    await _run_get_test("v1/products", "get_products_response.json", get, mock_aioresponses)


@pytest.mark.asyncio
async def test_get_product_v1(mock_aioresponses: aioresponses):
    async def get(client):
        return await client.get_product_v1("product_id")

    await _run_get_test(
        "v1/products/product_id", "get_product_response.json", get, mock_aioresponses
    )


@pytest.mark.asyncio
async def test_get_tariff_v1(mock_aioresponses: aioresponses):
    async def get(client):
        return await client.get_tariff_v1(
            "product_id", EnergyTariffType.GAS, "tariff_code", RateType.STANDING_CHARGES
        )

    await _run_get_test(
        "v1/products/product_id/gas-tariffs/tariff_code/standing-charges",
        "get_tariff_response.json",
        get,
        mock_aioresponses,
    )


@pytest.mark.asyncio
async def test_renew_business_tariff(mock_aioresponses: aioresponses):
    async def post(client, request):
        return await client.renew_business_tariff("account_num", request)

    await _run_post_test(
        "v1/accounts/account_num/tariff-renewal",
        "business_tariff_renewal_request.json",
        "business_tariff_renewal_response.json",
        post,
        mock_aioresponses,
    )


async def _run_get_test(
    path: str, response_resource: str, func: Callable, mock_aioresponses: aioresponses
):
    mock_aioresponses.get(
        f"{_API_BASE}/{path}",
        payload=load_fixture_json(response_resource),
    )
    async with OctopusEnergyRestClient(_FAKE_API_TOKEN) as client:
        response = await func(client)
    assert response == load_fixture_json(response_resource)


async def _run_post_test(
    path: str,
    request_resource: str,
    response_resource: str,
    func: Callable,
    mock_aioresponses: aioresponses,
):
    request = load_fixture_json(request_resource)
    mock_aioresponses.post(
        f"{_API_BASE}/{path}",
        payload=load_fixture_json(response_resource),
    )
    async with OctopusEnergyRestClient(_FAKE_API_TOKEN) as client:
        response = await func(client, request)
    assert response == load_fixture_json(response_resource)
