# AGENTS.md

Guidance for AI coding agents working in this repository. Read this before making changes.

## What this is

A Python client library (`octopus-energy` on PyPI) for the Octopus Energy RESTful API. It provides
two async clients: a low-level `OctopusEnergyRestClient` (returns dicts) and an opinionated
`OctopusEnergyConsumerClient` (returns typed dataclasses). Python 3.8+, MIT license, original work
by Mark Allanson (not a fork).

## Commands (verified — do not invent flags)

Dependency management is **Poetry** (not pip). Testing/linting is orchestrated by **tox**.

```shell
poetry install            # set up the virtualenv — run first
tox                       # full suite: py38 & py39 tests (coverage) + black check + flake8
tox -e black              # check formatting only (black --check octopus_energy tests)
tox -e flake8             # lint only (flake8 octopus_energy tests)
poetry run python -m unittest tests.test_client -v   # run a single unittest module
```

There is no `run` target — this is a library. To exercise a change locally, write a quick async
script and run it under `poetry run python`.

## Repo layout

```
octopus_energy/
├── __init__.py     # Public API: re-exports both clients, all models/enums, and exceptions. Flake8 ignores F401 here.
├── rest_client.py  # OctopusEnergyRestClient — async wrapper over every REST endpoint; returns dicts.
├── client.py       # OctopusEnergyConsumerClient — opinionated consumer layer; returns dataclasses. Wraps the REST client.
├── models.py       # Dataclass models + Enums (Meter, Consumption, TariffRate, SortOrder, Aggregate, RateType, EnergyTariffType, …).
├── mappers.py      # JSON dict ↔ dataclass mapping functions (meters_from_response, consumption_from_response, tariff_rates_from_response) + unit conversion (m³ ↔ kWh).
└── exceptions.py   # ApiError, ApiAuthenticationError, ApiNotFoundError, ApiBadRequestError.
tests/
├── __init__.py     # Helpers: load_fixture_json(), does_asyncio (decorator to run a coroutine in an event loop).
├── test_client.py      # Consumer client tests — uses unittest.mock.patch on the REST client + mappers.
├── test_rest_client.py # REST client tests.
├── test_e2e.py         # End-to-end style tests with aioresponses + freezegun; asserts exact request URLs.
├── test_mappers.py     # Mapper tests.
├── test_models.py      # Model tests.
├── test_exceptions.py  # Exception tests.
├── fixtures/           # JSON API response fixtures consumed by tests.
└── mapping_results/    # Expected mapping outputs.
```

CI: `.travis.yml` (matrix py38/py39 + black + flake8, deploys to PyPI on tags) and
`.github/workflows/python-publish.yml` (publishes to PyPI on release). Both run `tox`.

## Architecture & key concepts

- **Two-client design.** `OctopusEnergyConsumerClient` is a thin, consumer-focused layer that
  constructs an `OctopusEnergyRestClient` internally and maps its dict responses into models. When
  adding a consumer-facing method, (1) ensure the REST method exists, (2) add a mapper in
  `mappers.py` if needed, (3) add the model in `models.py` if needed.
- **Async is mandatory.** Both clients are built on `aiohttp`. Using a plain `with` raises
  `TypeError("Use async context manager (async with) instead")` by design — there is a test for it.
  Always demonstrate usage with `async with`.
- **Auth** is HTTP Basic with the API token as the username and empty password
  (`BasicAuth(api_token, "")`). A `None` token omits auth (public endpoints only).
- **URLs** are assembled with `furl` from a list of path segments in `_execute`; `None` query params
  are filtered out before the request is sent.
- **Error mapping** lives in `rest_client._execute`: status > 399 maps 401→`ApiAuthenticationError`,
  404→`ApiNotFoundError`, 400→`ApiBadRequestError`, else `ApiError`.
- **Unit conversion** (`mappers._calculate_unit`) converts between `m³` and `kWh` for gas using the
  multiplier `11.1868`, quantised to 3 decimal places.

## Conventions & gotchas

- **Line length is 100** (configured for both `black` and `flake8` in `tox.ini`/`pyproject.toml`).
  Black is the formatter; do not hand-format.
- **Flake8 ignores F401 in `__init__.py`** — the package root intentionally re-exports many names
  for the public API. When you add a new model/exception, export it from `__init__.py` AND add it to
  `__all__`.
- **`black` target version is py38** (`target-version = ['py38']` in `pyproject.toml`). Keep code
  3.8-compatible (no walrus-in-comprehension-only features that 3.8 lacks, etc.).
- **Tests are `unittest`, not pytest.** Async tests use the `@does_asyncio` decorator from
  `tests/__init__.py` (runs the coroutine via `get_event_loop().run_until_complete`). HTTP is mocked
  with `aioresponses`; time is frozen with `@freeze_time`; the e2e tests assert **exact** query
  strings, so changing how a parameter is serialized will break them.
- **Enums drive the API.** `SortOrder`, `Aggregate`, `EnergyTariffType`, and `RateType` use
  `_DocEnum`/`Enum`; their `.value` is what gets sent on the wire (e.g.
  `EnergyTariffType.ELECTRICITY.value == "electricity-tariffs"`). Don't pass raw strings to methods
  that take these enums.
- **Paging.** `Consumption` carries `previous_page` / `next_page` as `PageReference` objects; pass
  `page_reference=consumption.next_page` to `get_consumption` to walk pages.
- **`pyproject.toml` references `readme = "readme.md"`** — the README filename is lowercase. Keep it.
- **`integ_tests/` is gitignored** (real-account integration tests). Don't commit it.
- The API is pre-1.0 and declared unstable; prefer additive changes that don't break existing public
  shapes.

## Do / don't

- DO run `tox` (or `tox -e black && tox -e flake8` + unittest) before declaring a task done.
- DO export any new public symbol from `octopus_energy/__init__.py` and `__all__`.
- DO add a fixture under `tests/fixtures/` and an expected-mapping file when adding/altering a mapper.
- DON'T use a synchronous `with` with either client — it raises `TypeError`.
- DON'T hand-format; run black.
- DON'T invent CLI flags or a `run` command — this is an import-only library.
