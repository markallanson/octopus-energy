from typing import Callable

import pytest
from aioresponses import aioresponses

from octopus_energy import OctopusEnergyRestClient
from octopus_energy.models import EnergyTariffType, RateType
from octopus_energy.rest_client import _API_BASE
from tests import load_fixture_json

_FAKE_API_TOKEN = "sk_live_xxxxxxxxxxxx"


@pytest.fixture
def mock_aioresponses():
    with aioresponses() as mock_aioresponses:
        yield mock_aioresponses


@pytest.mark.asyncio
async def test_get_account_details_v1(mock_aioresponses: aioresponses):
    async def get(client):
        return await client.get_account_details("account_number")

    await _run_get_test(
        "v1/accounts/account_number", "account_response.json", get, mock_aioresponses
    )


@pytest.mark.asyncio
async def test_get_elec_consumption_v1(mock_aioresponses: aioresponses):
    async def get(client):
        return await client.get_electricity_consumption_v1("mpan", "serial_number")

    await _run_get_test(
        "v1/electricity-meter-points/mpan/meters/serial_number/consumption",
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


@pytest.mark.asyncio
async def test_get_gas_consumption_v1(mock_aioresponses: aioresponses):
    async def get(client):
        return await client.get_gas_consumption_v1("mprn", "serial_number")

    await _run_get_test(
        "v1/gas-meter-points/mprn/meters/serial_number/consumption",
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
    mock_aioresponses.post(
        f"{_API_BASE}/{path}",
        payload=load_fixture_json(response_resource),
    )
    async with OctopusEnergyRestClient(_FAKE_API_TOKEN) as client:
        response = await func(client)
    assert response == load_fixture_json(response_resource)
