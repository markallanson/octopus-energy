"""Python client for the Octopus Energy RESTful API"""

from .rest_client import OctopusEnergyRestClient
from .models import (
    Consumption,
    IntervalConsumption,
    MeterType,
    UnitType,
    Aggregate,
    SortOrder,
    RateType,
)
from .exceptions import ApiAuthenticationError, ApiError, ApiNotFoundError, ApiBadRequestError

__all__ = [
    "OctopusEnergyRestClient",
    "ApiAuthenticationError",
    "ApiError",
    "ApiNotFoundError",
    "ApiBadRequestError",
    "Consumption",
    "IntervalConsumption",
    "MeterType",
    "UnitType",
    "Aggregate",
    "SortOrder",
    "RateType",
]
