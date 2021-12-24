import numpy as np
import typing
from .utils import _check_units
from .utils import M_TO_FT


# Data class contains the actual projection
class Data:
    def __init__(self, units: str, data: dict) -> None:
        """Data

        Parameters
        ----------
        units : str
            One of the allowable strings that define standard units for SLR
        data : dict
            A Data object that contains 'x' and 'y' keys with 'x' given as years and 'y'
            containing the SLR values for each year

        """
        # Check for length of data
        if len(data["x"]) != len(data["y"]):
            raise ValueError(
                "The two arrays passed in the data dictionary have discordant lengths!"
            )

        # Check the units using the helper function
        _check_units(units=units)

        # Check that the dictionary has the right keys
        if not (("x" in data.keys()) and ("y" in data.keys())):
            raise ValueError("Need 'x' and 'y' keys in the 'data' object")

        # Actually load the data
        self.x = np.array(data["x"])
        self.y = np.array(data["y"])
        self._units = units

    @property
    def units(self):
        return self._units

    def convert(
        self, to_units: str, inplace: bool = False
    ) -> typing.Union[None, np.ndarray]:
        """Convert units in data.y array

        Parameters
        ----------
        to_units : str
            Name of the units to convert toward, must be one of 'm', 'ft', 'in',
            and 'cm'
        inplace : bool, optional
            If true, the values in the data object are overwritten, by default False

        Returns
        -------
        typing.Union[None, np.ndarray]
            Returns either nothing (inplace=True) or an nd.ndarray with the converted
            values

        """
        # Check the units
        _check_units(to_units)

        # Change the units of the y value on the spot
        if self.units == "ft":
            if to_units == "in":
                fac = 12.0
            if to_units == "ft":
                fac = 1.0
            if to_units == "m":
                fac = 1 / M_TO_FT
            if to_units == "cm":
                fac = 1 / M_TO_FT * 100
        if self.units == "in":
            if to_units == "in":
                fac = 1.0
            if to_units == "ft":
                fac = 1 / 12.0
            if to_units == "m":
                fac = 1 / 12.0 * 1 / M_TO_FT
            if to_units == "cm":
                fac = 1 / 12.0 * 1 / M_TO_FT * 100
        if self.units == "m":
            if to_units == "in":
                fac = 12.0 * M_TO_FT
            if to_units == "ft":
                fac = M_TO_FT
            if to_units == "m":
                fac = 1.0
            if to_units == "cm":
                fac = 100.0
        if self.units == "cm":
            if to_units == "in":
                fac = 12.0 * M_TO_FT * 1 / 100.0
            if to_units == "ft":
                fac = M_TO_FT * 1 / 100
            if to_units == "m":
                fac = 1 / 100.0
            if to_units == "cm":
                fac = 1.0

        # Apply the transformation
        if inplace:
            self.y = self.y * fac
            self._units = to_units
        else:
            return self.y * fac

    def __repr__(self) -> str:
        s = f"Data in {self.units} ranging from {self.x[0]} to {self.x[-1]}"
        return s
