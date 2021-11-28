from pathlib import Path
import json
import typing

M_TO_FT = 3.281

with open(Path(__file__).parent / "data/scenarios.json") as f:
    ALL_SCENARIOS = json.load(f)

ALL_LOCATIONS = list(ALL_SCENARIOS.keys())


# Check that units are valid
def _check_units(units: str) -> None:
    """Validates units and verifies that unit string descriptor is in the standard set

    Parameters
    ----------
    units : str
        String representing units, can only be one of 'ft', 'in', 'm', and 'cm'

    """
    if not (units in ["ft", "in", "m", "cm"]):
        raise ValueError(
            f"Units {units} are not supported; only use 'ft', " f"'in', 'm', and 'cm'."
        )


# Check that location is valid
def _validate_location(location: typing.Union[str, int]) -> str:
    """Validates location by checking against ALL_LOCATIONS global constant

    Parameters
    ----------
    location : typing.Union[str, int]
        Either a str (e.g., '"San Francisco"') or an int (e.g., '1') describing the location
        to be used to load SLRScenarios

    Returns
    -------
    str
        Standard location string as recorded in ALL_LOCATIONS

    """
    if isinstance(location, int):
        if not (location in list(range(0, len(ALL_LOCATIONS)))):
            raise ValueError("Index notation exceeds length of locations")
        else:
            target_location = ALL_LOCATIONS[location]
    else:
        if not (location in ALL_LOCATIONS):
            raise ValueError("Make sure location is in the dataset")
        else:
            target_location = location

    return target_location
