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
