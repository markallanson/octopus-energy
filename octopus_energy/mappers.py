from datetime import datetime
from decimal import Decimal, ROUND_DOWN
from typing import List, Optional

import dateutil
from dateutil.parser import isoparse
from furl import furl

from .models import (
    IntervalConsumption,
    UnitType,
    Consumption,
    ElectricityMeter,
    MeterDirection,
    EnergyType,
    MeterGeneration,
    GasMeter,
    Tariff,
    Meter,
    Address,
    MeterPoint,
    PageReference,
    SortOrder,
    Aggregate,
    TariffRate,
)

_CUBIC_METERS_TO_KWH_MULTIPLIER = 11.1868
_KWH_TO_KWH_MULTIPLIER = 1
_UNIT_MULTIPLIERS = {
    (UnitType.KWH.value, UnitType.CUBIC_METERS.value): (1 / _CUBIC_METERS_TO_KWH_MULTIPLIER),
    (UnitType.CUBIC_METERS.value, UnitType.KWH.value): _CUBIC_METERS_TO_KWH_MULTIPLIER,
}
_QUANT_3DP = Decimal("0.001")


def to_timestamp_str(timestamp: datetime) -> str:
    """Convert a datetime to an iso timestamp string expected by the octopus energy APIs.

    Args:
        timestamp: The timestamp to convert.

    Returns:
        The timestamp in a iso format required by the octopus energy APIs
    """
    return timestamp.replace(microsecond=0).isoformat() if timestamp else None


def from_timestamp_str(timestamp: str) -> Optional[datetime]:
    """Convert am Octopus Energy timestamp string to an datetime.

    Args:
        timestamp: The timestamp to convert.

    Returns:
        The timestamp as a datetime object.
    """
    if timestamp is None:
        return None
    return dateutil.parser.isoparse(timestamp) if timestamp else None


def _map_tariffs(input_tariffs: List[dict]) -> List[Tariff]:
    return [
        Tariff(
            t["tariff_code"], from_timestamp_str(t["valid_from"]), from_timestamp_str(t["valid_to"])
        )
        for t in input_tariffs
    ]


def meters_from_response(response: dict) -> List[Meter]:
    meters = []
    for property_ in response["properties"]:
        address = Address(
            property_.get("address_line_1", None),
            property_.get("address_line_2", None),
            property_.get("address_line_3", None),
            property_.get("county", None),
            property_.get("town", None),
            property_.get("postcode", None),
            # the property is active if it has no moved out date
            property_.get("moved_out_at", None) is None,
        )
        for meter_point in property_.get("electricity_meter_points", []):
            for meter in meter_point["meters"]:
                meters.append(
                    ElectricityMeter(
                        meter_point=MeterPoint(meter_point["mpan"], address),
                        serial_number=meter["serial_number"],
                        tariffs=_map_tariffs(meter_point["agreements"]),
                        direction=MeterDirection.EXPORT
                        if meter_point["is_export"]
                        else MeterDirection.IMPORT,
                        energy_type=EnergyType.ELECTRICITY,
                        generation=MeterGeneration.SMETS1_ELECTRICITY,
                    )
                )
        for meter_point in property_.get("gas_meter_points", []):
            for meter in meter_point["meters"]:
                meters.append(
                    GasMeter(
                        meter_point=MeterPoint(meter_point["mprn"], address),
                        serial_number=meter["serial_number"],
                        tariffs=_map_tariffs(meter_point["agreements"]),
                        energy_type=EnergyType.GAS,
                        generation=MeterGeneration.SMETS1_GAS,
                    )
                )
        return meters


def consumption_from_response(
    response: dict, meter: Meter, desired_unit_type: UnitType = None
) -> Consumption:
    """Generates the Consumption model from an octopus energy API response.

    Args:
        response: The API response object.
        meter: The meter the consumption is related to.
        desired_unit_type: The desired unit for the consumption intervals. The mapping will
                           convert from the meters units to the desired units.

    Returns:
        The Consumption model for the period of time represented in the response.

    """
    if "results" not in response:
        return Consumption(unit_type=desired_unit_type, meter=meter)
    return Consumption(
        desired_unit_type,
        meter,
        [
            IntervalConsumption(
                consumed_units=_calculate_unit(
                    result["consumption"], meter.generation.unit_type, desired_unit_type
                ),
                interval_start=isoparse(result["interval_start"]),
                interval_end=isoparse(result["interval_end"]),
            )
            for result in response["results"]
        ],
        _get_page_reference(response, "previous"),
        _get_page_reference(response, "next"),
    )


def tariff_rates_from_response(response: dict) -> List[TariffRate]:
    """Generates the list of tariff rates from an octopus energy API response.

    Args:
        response: The API response object.

    Returns:
        The List containing the rates for a specific tariff

    """
    if "results" not in response:
        return []
    return [
        TariffRate(
            Decimal(result["value_inc_vat"]).quantize(_QUANT_3DP, rounding=ROUND_DOWN),
            Decimal(result["value_exc_vat"]).quantize(_QUANT_3DP, rounding=ROUND_DOWN),
            from_timestamp_str(result["valid_from"]),
            from_timestamp_str(result.get("valid_to", None)),
        )
        for result in response["results"]
    ]


def _get_page_reference(response: dict, page: str):
    if page not in response:
        return None
    page_url = furl(response[page])
    if not page_url.args:
        return None

    # Convert all args in the page reference to the types used by the APIs
    args = dict(page_url.args)
    if "period_from" in args:
        args["period_from"] = from_timestamp_str(args["period_from"])
    if "period_to" in args:
        args["period_to"] = from_timestamp_str(args["period_to"])
    if "order" in args:
        args["order"] = SortOrder(args["order"])
    if "group_by" in args:
        args["group_by"] = Aggregate(args["group_by"])

    return PageReference(args)


def _calculate_unit(consumption, actual_unit, desired_unit: UnitType = None):
    """Converts unit values from one unit to another unit.

    If no mapping is available the value is returned unchanged.

    :param consumption: The consumption to convert.
    :param actual_unit: The unit the supplied consumption is measured in.
    :param desired_unit: The unit the convert the consumption to.
    :return: The consumption converted to the desired unit.
    """
    return (
        consumption
        if not desired_unit
        else consumption * _UNIT_MULTIPLIERS.get((actual_unit.value, desired_unit.value), 1)
    )
