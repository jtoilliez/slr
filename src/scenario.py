import typing

import numpy as np
from pandas import DataFrame, Series

from .data import Data
from .utils import _check_units


# Scenario contains the entire information related to a single trajectory
class Scenario:
    def __init__(
        self,
        description: str,
        short_name: str,
        units: str,
        probability: float,
        baseline_year: int,
        data: dict,
    ) -> None:
        """Scenario represent a specific sea-level rise trajectory, described by the below
        paramaters

        Parameters
        ----------
        description : str
            Long name for the trajectory, e.g., 'High Emission, Low Risk'
        short_name : str
            Short name used for captions, legends, etc. e.g., 'Low Risk'
        units : str
            One of 'm', 'cm', 'in', and 'ft' which describes the units of the 'y' data
        probability : float
            Probability given as the value of the Cumulative Distribution Function (CDF)
            if available, must be between 0 and 1
        baseline_year : int
            The baseline year upon which the sea-level rise trajectory is based.
            Must be an integer
        data : dict
            Dictionary containing the actual sea-level rise data. The dictionary
            must have 'x' and 'y' keys, with values paired as follows:
            * 'x' : [list of years]
            * 'y' : [list of SLR values]
            Both lists must have the same dimension.

        """
        # Units need to be valid
        _check_units(units)

        # Probability is a float or None
        if not (isinstance(probability, float) or (probability is None)):
            raise ValueError(
                "'probability' must be a float or None (null); "
                "check entry in JSON file."
            )

        if isinstance(probability, float):
            if probability >= 0.0 and probability <= 1.0:
                self.probability = probability
            else:
                raise ValueError(
                    f"Probability {self.probability} is not within [0; 1]."
                )

        if probability is None:
            self.probability = np.nan

        # If all checks out, record values
        self.description = description
        self.short_name = short_name
        self.baseline_year = baseline_year
        self.data = Data(units=units, data=data)

    def __repr__(self) -> str:
        s = (
            f"Scenario '{self.short_name}', values are given in {self.units} "
            f"and years range from {self.data.x[0]} to {self.data.x[-1]}"
        )
        return s

    @property
    def units(self):
        return self.data.units

    @property
    def dataframe(self) -> Series:
        """Returns a DataFrame built from x and y in the Scenario

        Returns
        -------
        DataFrame
            DataFrame containing x values as index and y values as values.
        """
        df = DataFrame(
            data={
                f"{self.short_name}, {100. * self.probability:.2f}%"
                f" [{self.units}]": self.data.y
            },
            index=self.data.x,
        )
        df.index.name = f"Year (baseline: {self.baseline_year})"
        return df

    def by_horizon_year(self, horizon_year: typing.Union[int, float]) -> float:
        """Calculates the value of SLR projections by a given horizon_year

        Parameters
        ----------
        horizon_year : int or float
            The value of the year to interpolate the projections

        Returns
        -------
        float
            The interpolated SLR projection at that year, e.g., 2.5.
            Units are implicit and available using Scenario.units

        """
        # Check for horizon year
        if (horizon_year > self.data.x.max()) or (horizon_year < self.data.x.min()):
            raise ValueError(
                "Target year is out of bounds for this location, "
                f"years range from {self.data.x.min()} to "
                f"{self.data.x.max()}."
            )
        # Linearly interpolate value at the horizon_year
        proj = np.interp(horizon_year, self.data.x, self.data.y)
        return proj
