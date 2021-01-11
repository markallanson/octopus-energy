from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List


class UnitType(Enum):
    """Units of energy measurement."""

    KWH = ("kWh", "Kilowatt Hours")
    CUBIC_METERS = ("m³", "Cubic Meters")

    @property
    def description(self) -> str:
        """A description, in english, of the unit type."""
        return self.value[1]

    def __eq__(self, other):
        return self.value == other.value


class MeterType(Enum):
    """Energy meter types, the units the measure in and description in english."""

    SMETS1_GAS = ("SMETS1_GAS", UnitType.KWH, "1st Generation Smart Gas Meter")
    SMETS2_GAS = ("SMETS2_GAS", UnitType.CUBIC_METERS, "2nd Generation Smart Gas Meter")
    SMETS1_ELECTRICITY = (
        "SMETS1_ELECTRICITY",
        UnitType.KWH,
        "1st Generation Smart Electricity Meter",
    )
    SMETS2_ELECTRICITY = (
        "SMETS2_ELECTRICITY",
        UnitType.KWH,
        "2nd Generation Smart Electricity Meter",
    )

    @property
    def unit_type(self) -> UnitType:
        """The type of unit the meter measures consumption in."""
        return self.value[1]

    @property
    def description(self) -> str:
        """A description, in english, of the meter."""
        return self.value[2]

    def __eq__(self, other):
        return self.value == other.value


@dataclass
class IntervalConsumption:
    """Represents the consumption of energy over a single interval of time."""

    interval_start: datetime
    interval_end: datetime
    consumed_units: Decimal


@dataclass
class Consumption:
    """Consumption of energy for a list of time intervals."""

    unit_type: UnitType
    meter_type: MeterType
    intervals: List[IntervalConsumption] = field(default_factory=lambda: [])


class _DocEnum(Enum):
    """Wrapper to create enumerations with useful docstrings."""

    def __new__(cls, value, doc):
        self = object.__new__(cls)
        self._value_ = value
        if doc is not None:
            self.__doc__ = doc
        return self


class EnergyTariffType(_DocEnum):
    """Represents a type of energy tariff."""

    ELECTRICITY = (
        "electricity-tariffs",
        "Represents a type of tariff related to electricity consumption.",
    )
    GAS = "gas-tariffs", "Represents a type of tariff relate to gas consumption."


class RateType(_DocEnum):
    """Represents a type of rate that can be charged for a product."""

    STANDING_CHARGES = (
        "standing-charges",
        "Represents the standing charge applied daily to an energy tariff.",
    )
    STANDARD_UNIT_RATES = (
        "standard-unit-rates",
        "Represents the standard unit rates for flat rate energy tariffs.",
    )
    DAY_UNIT_RATES = (
        "day-unit-rates",
        "Represents the rate charged during the day for dual rate tariffs.",
    )
    NIGHT_UNIT_RATES = (
        "night-unit-rates",
        "Represents the rate charged during the night for dual rate tariffs.",
    )


class SortOrder(_DocEnum):
    """The order to use when sorting results from search type API alls"""

    NEWEST_FIRST = (
        "-period",
        "Newest result first",
    )
    OLDEST_FIRST = (
        "period",
        "Oldest result first",
    )


class Aggregate(_DocEnum):
    """How to aggregate data returned from consumption based APIs"""

    HALF_HOURLY = None, "Aggregate consumption half hourly (the default)"
    HOUR = (
        "hour",
        "Aggregate consumption by hours",
    )
    DAY = (
        "day",
        "Aggregate consumption by days",
    )
    WEEK = (
        "week",
        "Aggregate consumption by weeks",
    )
    MONTH = (
        "month",
        "Aggregate consumption by months",
    )
    QUARTER = (
        "quarter",
        "Aggregate consumption quarterly",
    )
