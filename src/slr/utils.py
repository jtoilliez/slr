from pathlib import Path
import json
import typing
from pandas import DataFrame

M_TO_FT = 3.281

with open(Path(__file__).parent / "data/scenarios.json") as f:
    ALL_SCENARIOS = json.load(f)

# ALL_LOCATIONS = list(ALL_SCENARIOS.keys())
ALL_KEYS = [key_ for key_ in ALL_SCENARIOS.keys()]


def _show_available_locations(format: str = "list") -> typing.Union[list, DataFrame]:
    if format not in ["list", "dataframe"]:
        raise ValueError("The format arg must be either 'list' or 'dataframe'.")
    all_locations = [elem_["location name"] for _, elem_ in ALL_SCENARIOS.items()]
    if format == "list":
        return all_locations
    elif format == "dataframe":
        return DataFrame(data=all_locations, columns=["Location"])


# Provide list of all locations available in ALL_SCENARIOS
ALL_LOCATIONS = _show_available_locations(format="list")


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
            f"Units {units} are not supported; only use 'ft', 'in', 'm', and 'cm'."
        )


# Check that location is valid
def _validate_location(location: typing.Union[str, int]) -> str:
    """Validates key given as either a location name or an index

    Parameters
    ----------
    location : typing.Union[str, int]
        Either a str as a location name e.g., '"San Francisco, CA"', or a key
        e.g., '"San Francisco" or an int (e.g., '0') describing the location to be used
        to load a specific ScenarioPack

    Returns
    -------
    str
        Key of the requested ScenarioPack

    """
    if isinstance(location, int):
        if not (location in list(range(0, len(ALL_LOCATIONS)))):
            raise ValueError("Index notation exceeds length of locations")
        else:
            target_key = ALL_KEYS[location]
    elif isinstance(location, str):
        if not (location in ALL_LOCATIONS):
            if location in ALL_KEYS:
                target_key = location
            else:
                raise ValueError(
                    "Make sure location is present in the dataset either as an "
                    "index, key, or a location name."
                )
        else:
            # Find the corresponding key based on location name
            i = 0
            while not location == ALL_LOCATIONS[i]:
                i += 1
            target_key = ALL_KEYS[i]
    else:
        raise ValueError(
            "Make sure location is present in the dataset either as an "
            "index, key, or a location name."
        )

    return target_key
