from pathlib import Path
import json
import typing
from pandas import DataFrame

M_TO_FT = 3.281

with open(Path(__file__).parent / "data/scenarios.json") as f:
    ALL_SCENARIOS = json.load(f)

ALL_KEYS = [key_ for key_ in ALL_SCENARIOS.keys()]
ALL_STATIONS = [value_["station ID (CO-OPS)"] for _, value_ in ALL_SCENARIOS.items()]


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
    if not (units in ["ft", "in", "m", "mm", "cm"]):
        raise ValueError(
            f"Units {units} are not supported; only use 'ft', 'in', 'm',"
            f" 'mm', and 'cm'."
        )


# Check that location is valid
def _validate_location(location: typing.Union[str, int]) -> str:
    """Validates location, station, or key given to locate a SLRProjections item

    Parameters
    ----------
    location : typing.Union[str, int]
        A unique identifier defining the SLRProjections item. It can be given as
        either:

        * a str as a location name e.g., '"San Francisco, CA"',
        * or a Station ID e.g., '"9414290"'
        * or an int (e.g., '0')
        * a key from the scenarios.json file, e.g., 'cocat-2018-9414290'

        All describe the location to be used to load a specific
        SLRProjections item.

        In case multiple matches are possible, the first match will be returned.

    Returns
    -------
    str
        Key of the requested SLRProjections item

    Examples
    -------
    Use the NOAA Station ID:
    >>> utils._validate_location(location="9410660")
    '9410660'

    Use the location:
    >>> utils._validate_location(location="Los Angeles, CA")
    '9410660'

    Use an index:
    >>> utils._validate_location(location=0)
    '9414290'
    """
    if isinstance(location, int):
        if not (location in list(range(0, len(ALL_LOCATIONS)))):
            raise IndexError(
                "Index notation exceeds length of SLRProjections items available."
            )
        else:
            target_key = ALL_KEYS[location]
    elif isinstance(location, str):
        # Try these:
        if location in ALL_LOCATIONS:
            target_key = ALL_KEYS[ALL_LOCATIONS.index(location)]
        elif location in ALL_KEYS:
            target_key = location
        elif location in ALL_STATIONS:
            target_key = ALL_KEYS[ALL_STATIONS.index(location)]
        else:
            raise KeyError(
                "Make sure location is specified either as an "
                "station ID, a key, or a location name."
            )

    return target_key
