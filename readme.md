# Octopus Energy Python API Client Library

A Python client library for the [Octopus Energy](https://octopus.energy) RESTful API. It lets you
read your electricity and gas meter consumption, look up tariff rates, and inspect product pricing.

> **Warning:** The API is currently undergoing active development and should be considered
> unstable — even volatile — until it reaches version 1.0.0.

[![PyPI version](https://badge.fury.io/py/octopus-energy.svg)](https://badge.fury.io/py/octopus-energy)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/octopus-energy)

[![Build Status](https://travis-ci.com/markallanson/octopus-energy.svg?branch=main)](https://travis-ci.com/markallanson/octopus-energy)
[![Coverage Status](https://coveralls.io/repos/github/markallanson/octopus-energy/badge.svg?branch=main)](https://coveralls.io/github/markallanson/octopus-energy?branch=main)

## What & why

This library is for consumers (and the curious) who want programmatic access to their own Octopus
Energy data — half-hourly consumption from SMETS1/SMETS2 smart meters, the tariff rates that apply
to them, and the wider product/tariff catalogue exposed by Octopus. It ships two complementary
clients so you can choose the level of abstraction that fits your use case:

- **`OctopusEnergyConsumerClient`** — an opinionated, model-based client for personal/consumer use
  cases. Returns typed Python dataclasses (`Meter`, `Consumption`, `TariffRate`, …) and focuses on
  the blend of consumption + pricing that's useful for understanding your own energy usage.
- **`OctopusEnergyRestClient`** — a thin, low-level wrapper over the raw REST endpoints. Returns
  plain `dict`s straight from the API JSON, and covers the full surface area including partner-only
  endpoints (account creation, quoting, business tariff renewal).

Both clients are **fully async** (built on `aiohttp`) and are designed to be used as an
`async with` context manager.

## Installation

`octopus-energy` is published on [PyPI](https://pypi.org/project/octopus-energy/) and supports
Python 3.8+:

```shell
pip install octopus-energy
```

## Getting an API key

Obtain your API token and meter information (MPAN/MPRN + serial numbers) from the
[Octopus Energy Developer Dashboard][octo dashboard]. The token is used for HTTP Basic auth against
the API. Without a token you can still call the public product/tariff endpoints.

## Quickstart — Consumer client (recommended for personal use)

The consumer client maps API responses into typed dataclasses and exposes the most useful consumer
operations: listing your meters, fetching consumption, and looking up tariff rates.

```python
import asyncio
from datetime import datetime, timedelta

from octopus_energy import (
    OctopusEnergyConsumerClient,
    EnergyTariffType,
    RateType,
)


async def main():
    async with OctopusEnergyConsumerClient(api_token="sk_live_your-token") as client:
        # 1. List all meters on your account.
        meters = await client.get_meters(account_number="A-1234567")

        # 2. Pull consumption for the last day on the first meter.
        meter = meters[0]
        consumption = await client.get_consumption(
            meter, period_from=datetime.utcnow() - timedelta(days=1)
        )
        for interval in consumption.intervals:
            print(f"{interval.interval_start}: {interval.consumed_units} {consumption.unit_type.value}")

        # 3. Look up the unit rate in effect for a tariff right now.
        rate = await client.get_tariff_cost(
            product_code="AGILE-18-02-21",
            tariff_code="E-1R-AGILE-18-02-21-J",
            tariff_type=EnergyTariffType.ELECTRICITY,
            rate_type=RateType.STANDARD_UNIT_RATES,
            timestamp=datetime.utcnow(),
        )
        if rate is not None:
            print(f"Current rate: £{rate.cost_inc_vat}/unit (valid {rate.valid_from} → {rate.valid_to})")


asyncio.run(main())
```

The consumer client's main methods:

| Method | Returns | Notes |
| --- | --- | --- |
| `get_meters(account_number)` | `List[Meter]` | All gas & electricity meters on the account. |
| `get_consumption(meter, period_from=None, period_to=None, page_reference=None)` | `Consumption` | Handles paging via `consumption.previous_page` / `consumption.next_page`. |
| `get_tariff_cost(product_code, tariff_code, tariff_type, rate_type, timestamp)` | `Optional[TariffRate]` | Unit rate / standing charge at a single point in time. |
| `get_daily_flexible_rate_pricing(product_code, tariff_code, tariff_type, rate_type, timestamp)` | `List[TariffRate]` | All half-hourly rates for the day containing `timestamp` (Agile/Go-style tariffs). |

## Quickstart — REST client (full API, raw dicts)

The REST client is a thin shim that returns dictionaries and covers the complete API surface. It's
the right choice if you need endpoints the consumer client doesn't expose (accounts, quotes,
products, business tariff renewal) or just prefer raw JSON. See the
[Octopus Energy API documentation][octo api] for response shapes and parameter details.

```python
import asyncio
from octopus_energy import OctopusEnergyRestClient, Aggregate, SortOrder

api_token = "sk_live_your-token"
mprn = "your-mprn"
serial_number = "your-meter-serial-number"


async def main():
    async with OctopusEnergyRestClient(api_token) as client:
        consumption = await client.get_gas_consumption_v1(
            mprn,
            serial_number,
            order=SortOrder.NEWEST_FIRST,
            group_by=Aggregate.DAY,
        )
        print(consumption)


asyncio.run(main())
```

REST client methods (all `async`):

- `get_account_details(account_number)`
- `get_electricity_meter_points_v1(mpan)`
- `get_electricity_consumption_v1(mpan, serial_number, …)` — supports `period_from`/`period_to`,
  `order` (`SortOrder`), `group_by` (`Aggregate`), and paging.
- `get_gas_consumption_v1(mprn, serial_number, …)` — same parameters as electricity.
- `get_products_v1(…)` / `get_product_v1(product_code, tariffs_active_at=None)`
- `get_tariff_v1(product_code, tariff_type, tariff_code, rate_type, …)`
- `create_account(account_data)` / `create_quote(quote_data)` / `renew_business_tariff(…)` —
  **partner-only**: require a partner-organisation API key.

## Error handling

Failed calls raise one of the library's exceptions (all in `octopus_energy.exceptions`):

| Exception | When |
| --- | --- |
| `ApiAuthenticationError` | HTTP 401 — token rejected. |
| `ApiNotFoundError` | HTTP 404 — resource does not exist. |
| `ApiBadRequestError` | HTTP 400 — request data rejected. |
| `ApiError` | Any other HTTP error; carries the underlying `response`. |

## Project structure

```
octopus_energy/
├── __init__.py        # Public API surface (re-exports clients, models, exceptions)
├── rest_client.py     # OctopusEnergyRestClient — low-level async wrapper returning dicts
├── client.py          # OctopusEnergyConsumerClient — opinionated client returning dataclasses
├── models.py          # Dataclass models + enums (Meter, Consumption, Tariff, TariffRate, …)
├── mappers.py         # Functions mapping API JSON dicts ↔ Python models
└── exceptions.py      # ApiError / ApiAuthenticationError / ApiNotFoundError / ApiBadRequestError
tests/                 # unittest suite (aioresponses, requests-mock, freezegun) + JSON fixtures
```

## Development

The project uses [Poetry](https://python-poetry.org/) for dependency management and
[tox](https://tox.wiki/) for running the test matrix and linters (configured in `tox.ini`).

```shell
poetry install            # install dependencies into the virtualenv
tox                       # run the full suite: py38/py39 unit tests + black + flake8
tox -e black              # check formatting
tox -e flake8             # lint
```

Testing uses Python's `unittest`; run a single suite directly with, e.g.
`poetry run python -m unittest tests.test_client -v`.

## Contributing

Contributions are welcome. Please run `tox` (or at least the `black` and `flake8` environments)
before submitting a change so tests pass and the style stays consistent. Keep the public API
additive until the library reaches 1.0.0, since consumers depend on the current shapes.

## License

[MIT](LICENSE) © 2020 Mark Allanson.

## Links

- Source: [octopus-energy on GitHub][github]
- Octopus Energy [Developer Dashboard][octo dashboard] (API tokens)
- Octopus Energy [API documentation][octo api]

[github]: https://github.com/markallanson/octopus-energy
[octo dashboard]: https://octopus.energy/dashboard/developer/
[octo api]: https://developer.octopus.energy/docs/api/
