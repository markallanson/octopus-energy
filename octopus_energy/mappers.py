from dateutil.parser import isoparse
from requests import Response

from octopus_energy.models import IntervalConsumption, UnitType, Consumption, MeterType

_CUBIC_METERS_TO_KWH_MULTIPLIER = 11.1868
_KWH_TO_KWH_MULTIPLIER = 1
_UNIT_MULTIPLIERS = {
    (UnitType.KWH.value, UnitType.CUBIC_METERS.value): (1 / _CUBIC_METERS_TO_KWH_MULTIPLIER),
    (UnitType.CUBIC_METERS.value, UnitType.KWH.value): _CUBIC_METERS_TO_KWH_MULTIPLIER,
}


def consumption_from_response(
    response: Response, meter_type: MeterType, desired_unit_type: UnitType
) -> Consumption:
    """Generates the Consumption model from an octopus energy API response.

    Args:
        response: The API response object.
        meter_type: The type of meter the reading is from.
        desired_unit_type: The desired unit for the consumption intervals. The mapping will
                           convert from the meters units to the desired units.

    Returns:
        The Consumption model for the period of time represented in the response.

    """
    response_json = response.json()
    if "results" not in response_json:
        return Consumption(unit=desired_unit_type, meter_type=meter_type)
    return Consumption(
        desired_unit_type,
        meter_type,
        [
            IntervalConsumption(
                consumed_units=_calculate_unit(
                    result["consumption"], meter_type.unit_type, desired_unit_type
                ),
                interval_start=isoparse(result["interval_start"]),
                interval_end=isoparse(result["interval_end"]),
            )
            for result in response_json["results"]
        ],
    )


def _calculate_unit(consumption, actual_unit, desired_unit):
    """Converts unit values from one unit to another unit.

    If no mapping is available the value is returned unchanged.

    :param consumption: The consumption to convert.
    :param actual_unit: The unit the supplied consumption is measured in.
    :param desired_unit: The unit the convert the consumption to.
    :return: The consumption converted to the desired unit.
    """
    return consumption * _UNIT_MULTIPLIERS.get((actual_unit.value, desired_unit.value), 1)
