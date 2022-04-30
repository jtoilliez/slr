from pathlib import Path
import json
import typing
from pandas import DataFrame

M_TO_FT = 3.281

with open(Path(__file__).parent / "data/scenarios.json") as f:
    ALL_BUILTIN_SCENARIOS = json.load(f)

ALL_KEYS = [key_ for key_ in ALL_BUILTIN_SCENARIOS.keys()]
ALL_ISSUERS = [value_["issuer"] for _, value_ in ALL_BUILTIN_SCENARIOS.items()]


def _show_builtin_scenarios(format: str = "list") -> typing.Union[list, DataFrame]:
    if format not in ["list", "dataframe"]:
        raise ValueError("The format arg must be either 'list' or 'dataframe'.")
    all_locations = [
        elem_["location name"] for _, elem_ in ALL_BUILTIN_SCENARIOS.items()
    ]
    if format == "list":
        return ALL_KEYS
    elif format == "dataframe":
        return (
            # Build a clean dataframe showing what's available as custom scenarios
            DataFrame.from_dict(
                data={
                    "Key": ALL_KEYS,
                    "Location(s) covered": all_locations,
                    "Issuer": ALL_ISSUERS
                }
            )
        )


# Provide list of all locations available in ALL_BUILTIN_SCENARIOS
ALL_LOCATIONS = _show_builtin_scenarios(format="list")


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
def _validate_key(key: typing.Union[str, int]) -> str:
    """Validates location, station, or key given to locate a SLRProjections item

    Parameters
    ----------
    key : typing.Union[str, int]
        A unique identifier referencing one of the builtin scenarios. It can be given as
        either:

        * a location (e.g., 'New Jersey')
        * an int (e.g., '0')
        * a key from the scenarios.json file, e.g., 'cocat-2018-9414290'

        In case multiple matches are possible, the first match will be returned.

    Returns
    -------
    str
        Unique key of the requested scenario

    Examples
    -------
    Use a location:
    >>> utils._validate_key(key='New Jersey')
    'nj-dep-2021'
    Use a key:
    >>> utils._validate_key(key='nj-dep-2021')
    'nj-dep-2021'
    Use an index:
    >>> utils._validate_key(location=0)
    'nj-dep-2021'
    """
    if isinstance(key, int):
        if not (key in list(range(0, len(ALL_LOCATIONS)))):
            raise IndexError(
                "Index notation exceeds length of builtin items available."
            )
        else:
            target_key = ALL_KEYS[key]
    elif isinstance(key, str):
        # Try these:
        if key in ALL_LOCATIONS:
            target_key = ALL_KEYS[ALL_LOCATIONS.index(key)]
        elif key in ALL_KEYS:
            target_key = key
        else:
            raise KeyError(
                "Make sure location is specified either as an "
                "station ID, a key, or a location name."
            )

    return target_key
