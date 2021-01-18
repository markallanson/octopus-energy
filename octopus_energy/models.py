from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional


class _DocEnum(Enum):
    """Wrapper to create enumerations with useful docstrings."""

    def __new__(cls, value, doc):
        self = object.__new__(cls)
        self._value_ = value
        if doc is not None:
            self.__doc__ = doc
        return self


@dataclass
class Tariff:
    code: str
    valid_from: datetime
    valid_to: Optional[datetime]


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


class MeterGeneration(Enum):
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


class EnergyType(Enum):
    """Represents a type of energy."""

    GAS = "gas"
    ELECTRICITY = "electricity"


class MeterDirection(_DocEnum):
    """Represents the direction that energy flows through the meter."""

    IMPORT = ("import", "Electricity that is consumed from the electricity grid")
    EXPORT = ("export", "Electricity that is sent to the electricity grid")


@dataclass
class Address:
    line_1: str
    line_2: str
    line_3: str
    county: str
    town: str
    postcode: str
    active: bool

    def __str__(self):
        """Gets a single line string representation of the address"""
        return (
            f"{self.line_1} "
            f"{self.line_2 + ', ' if self.line_2 is not None else ''} "
            f"{self.line_3 + ', ' if self.line_3 is not None else ''}"
            f"{self.county + ', ' if self.county is not None else ''}"
            f"{self.town + ', ' if self.town is not None else ''}"
        )


@dataclass
class MeterPoint:
    """Represents an energy meter point which has an identifier and is located at an address.

    Many meter points can share the same address.
    """

    id: str
    address: Address


@dataclass
class Meter:
    """Represents an energy meter, either gas or electric."""

    meter_point: MeterPoint
    serial_number: str
    energy_type: EnergyType
    generation: MeterGeneration
    tariffs: List[Tariff]

    def get_tariff_at(self, timestamp: datetime):
        """Gets the tariff in effect on a meter at a specific date/time.

        This automatically takes into account open ended tariffs that have no end."""
        return next(
            (
                tariff
                for tariff in self.tariffs
                if timestamp >= tariff.valid_from
                and (not tariff.valid_to or timestamp < tariff.valid_to)
            ),
            None,
        )


@dataclass
class ElectricityMeter(Meter):
    direction: MeterDirection


@dataclass
class GasMeter(Meter):
    pass


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
    meter: Meter
    intervals: List[IntervalConsumption] = field(default_factory=lambda: [])


class EnergyTariffType(_DocEnum):
    """Represents a type of energy tariff."""

    ELECTRICITY = (
        "electricity-tariffs",
        "Represents a type of tariff related to electricity consumption.",
    )
    GAS = ("gas-tariffs", "Represents a type of tariff related to gas consumption.")


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
