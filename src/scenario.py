import typing
import numpy as np
from pandas import Series
from pandas import DataFrame
from pandas import concat
from matplotlib.pyplot import Axes, subplots
from .utils import ALL_LOCATIONS

from .utils import ALL_SCENARIOS, _check_units, _validate_location
from .data import Data

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
            Probability given as the value of the Cumulative Distribution Function (CDF) if
            available, must be between 0 and 1
        baseline_year : int
            The baseline year upon which the sea-level rise trajectory is based. Must be an
            integer
        data : dict
            Dictionary containing the actual sea-level rise data. The dictionary must have
            'x' and 'y' keys, with values paired as follows:
            * 'x' : [list of years]
            * 'y' : [list of SLR values]
            Both lists must have the same dimension.    
    
        """
        # Units need to be valid
        _check_units(units)

        # Probability is a float or None
        if not (isinstance(probability, float) or (probability is None)):
            raise ValueError(
                "'probability' must be a float or None (null); check entry in JSON file."
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
                f"{self.short_name}, {100. * self.probability:.2f}% [{self.units}]": self.data.y
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


# SLRScenarios contains SLR Scenario objects for a given location
class SLRScenarios:
    def __init__(self, data: dict = None, coerce_units: bool = True) -> None:

        if data is not None:
            # Check that you have the right data in there
            for attr in ["description", "station ID (CO-OPS)", "scenarios"]:
                if not attr in data:
                    raise KeyError(f"The {attr} key is missing or mispelled.")

        else:
            raise ValueError("data was passed as None")

        # Record properties
        self.description = data["description"]
        self.station_ID = data["station ID (CO-OPS)"]

        # Record Scenarios
        scenarios = data["scenarios"]
        try:
            len(scenarios)
            self.scenarios = []
        except TypeError:
            raise TypeError("The Scenarios passed are not a list of Scenario objects")

        # Record all Scenario objects
        for scenario_ in scenarios:
            self.scenarios.append(
                Scenario(
                    description=scenario_["description"],
                    short_name=scenario_["short name"],
                    units=scenario_["units"],
                    probability=scenario_["probability (CDF)"],
                    baseline_year=scenario_["baseline year"],
                    data=scenario_["data"],
                )
            )

        # Additional attributes
        self.shape = (len(self.scenarios),)

    @classmethod
    def from_location(cls, location: str = ""):
        """Generates a SLRScenarios isinstance from a location contained within the
        ALL_LOCATIONS list

        Parameters
        ----------
        location : str, optional
            String containing the location to load, by default ""

        Returns
        -------
        SLRScenarios
            SLRScenarios instance at the specified location
        """
        target_location = _validate_location(location=location)
        return cls(data=ALL_SCENARIOS[target_location])

    @classmethod
    def from_index(cls, index: int = None):
        """Generates a SLRScenarios isinstance from a location contained within the
        ALL_LOCATIONS list

        Parameters
        ----------
        location : int, optional
            Int containing the index of the location to load, by default None

        Returns
        -------
        SLRScenarios
            SLRScenarios instance at the specified location
        """
        target_location = _validate_location(location=index)
        return cls(data=ALL_SCENARIOS[target_location])

    @staticmethod
    def show_all_available_locations():
        """Simple function that lists all functions available prior to loading a
        specific SLRScenarios instance

        Returns
        -------
        list
            List of locations available for manipulation
        """
        return ALL_LOCATIONS

    def __repr__(self) -> str:
        s = (
            f"Sea level rise at {self.description}; "
            f"{self.shape[0]} Scenario(s) available"
        )
        return s

    def __getitem__(self, key: int) -> Scenario:
        if not isinstance(key, int):
            raise TypeError("Wrong type passed; only int is supported")
        if not (key >= 0 and key <= self.shape[0]):
            raise IndexError(
                f"Index is out of range; shape of the instance is {self.shape}"
            )
        # If everything checks out, provides the Scenario
        return self.scenarios[key]

    @property
    def dataframe(self) -> DataFrame:
        """Builds a pd.DataFrame from all Scenario objects in this instance

        Returns
        -------
        DataFrame
            A single pd.DataFrame containing all Scenario.data.x and 
            Scenario.data.y instances
        """
        df = concat([scenario_.dataframe for scenario_ in self.scenarios], axis=1)
        return df

    @property
    def units(self) -> str:
        """Returns the units used in the Scenario.data instances. If more than one
         units are used, returns a list; otherwise, if the same units are used for 
         all Scenario.data instances, a single value is returned.

        Returns
        -------
        str
            The name of the units used in the Scenario.data instances,
            either a list or a single value out of 'm', 'ft', 'in', or 'cm'.
        """
        # Returns the units of each Scenario
        units = []
        for scenario in self.scenarios:
            units.append(scenario.units)

        if all(x == units[0] for x in units):
            return units[0]
        else:
            return units

    def by_horizon_year(
        self, horizon_year: float, merge: bool = True, coerce_errors: bool = False
    ) -> typing.Union[Series, DataFrame]:
        """Generate a Series with projected values for SLR
        for a given horizon year for each Scenario. It is a wrapper of the method
        from the Scenario class

        Parameters
        ----------
        horizon_year : float or int
            Value for the horizon year (e.g. 2055)
        merge: bool, optional
            If set to True (default), will returns a the projected value merged with
            the built-in projections as a pandas.DataFrame instance.
            If set to False, will return a pandas.Series instance with the projected
            values for each Scenario
        coerce_errors: bool, optional
            If set to True (default), will coerce linear interpolation errors by
            replacing with np.nan; if set to False, will raise errors

        Returns
        -------
        Series
            List of projected values by the horizon year OR
        DataFrame
            Merged DataFrame with built-in projections and the newly calculated
            projections
        
        Raises
        ------
        ValueError
            If the horizon year exceeds the range provided in the original data.
        """

        proj = dict()
        for scenario in self.scenarios:
            # Check for horizon year
            # if (horizon_year > scenario.data.x.max()) or (
            #     horizon_year < scenario.data.x.min()
            # ):
            #     raise ValueError(
            #         "Target year is out of bounds for this location, "
            #         f"years range from {scenario.data.x.min()} to "
            #         f"{scenario.data.x.max()}."
            #     )
            # Linearly interpolate value at the horizon_year
            # proj[scenario.short_name] = np.interp(
            #     horizon_year, scenario.data.x, scenario.data.y
            # )
            proj[scenario.short_name] = scenario.by_horizon_year(
                horizon_year=horizon_year
            )
        ds = Series(
            data=proj,
            name=f"SLR at {self.description} by {horizon_year} [{self.units}]",
        )

        if not merge:
            # Simply return calculated values
            return ds
        else:
            # Deep copy of existing (built-in) projections
            df = self.dataframe.copy(deep=True)
            # Include new values
            df.loc[horizon_year, :] = ds.values
            df.sort_index(inplace=True)
            return df

    def convert(
        self, to_units: str, inplace: bool = True
    ) -> typing.Union[None, np.ndarray]:

        # Check the units
        _check_units(to_units)

        # Scan over Scenario objects and change the units
        if inplace:
            for scenario_ in self.scenarios:
                scenario_.data.convert(to_units=to_units, inplace=inplace)
            return self.dataframe
        else:
            raise NotImplementedError("On the fly conversion not supported")

    def plot(self, ax: Axes = None, horizon_year: float = None) -> Axes:

        # Handle ax
        if ax is None:
            _, ax = subplots(1, 1, figsize=(5.35, 3.5))

        # Graphics
        for index, series in self.dataframe.iteritems():
            ax.plot(series, label=series.name)

        # Handle horizon year
        if horizon_year is not None:
            ds = self.by_horizon_year(horizon_year=horizon_year, merge=False)
            ax.axvline(x=horizon_year, **{"ls": "--", "lw": 1, "c": "lightgray"})
            for name, val in ds.iteritems():
                ax.scatter(x=horizon_year, y=val)

        # Plot all values
        ax.set_ylabel(f"SLR [{self.units}]")
        ax.set_title(f"SLR for {self.description}")
        ax.legend()

        return ax
