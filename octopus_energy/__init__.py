"""Python client for the Octopus Energy RESTful API"""

from .models import (
    get_tariff_at,
    Address,
    Aggregate,
    Consumption,
    EnergyType,
    EnergyTariffType,
    IntervalConsumption,
    Meter,
    MeterDirection,
    MeterGeneration,
    MeterPoint,
    RateType,
    SortOrder,
    Tariff,
    UnitType,
    ElectricityMeter,
    GasMeter,
    PageReference,
    TariffRate,
)
from .exceptions import ApiAuthenticationError, ApiError, ApiNotFoundError, ApiBadRequestError
from .rest_client import OctopusEnergyRestClient
from .client import OctopusEnergyConsumerClient

__all__ = [
    "OctopusEnergyRestClient",
    "ApiAuthenticationError",
    "ApiError",
    "ApiNotFoundError",
    "ApiBadRequestError",
    "Consumption",
    "IntervalConsumption",
    "MeterGeneration",
    "UnitType",
    "Aggregate",
    "SortOrder",
    "RateType",
    "Meter",
    "EnergyType",
    "EnergyTariffType",
    "OctopusEnergyConsumerClient",
    "Tariff",
    "MeterDirection",
    "MeterPoint",
    "Address",
    "ElectricityMeter",
    "GasMeter",
    "PageReference",
    "TariffRate",
    "get_tariff_at",
]
