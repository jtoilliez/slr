import typing

import numpy as np
from matplotlib.pyplot import Axes, subplots
from pandas import DataFrame, Series, concat

from .scenario import Scenario
from .utils import (
    ALL_SCENARIOS,
    _check_units,
    _validate_location,
    _show_available_locations,
)


# ScenarioPack contains SLR Scenario objects for a given location
class ScenarioPack:
    def __init__(self, data: dict = None, coerce_units: bool = True) -> None:

        if data is not None:
            # Check that you have the right data in there
            for attr in ["location name", "station ID (CO-OPS)", "scenarios"]:
                if attr not in data:
                    raise KeyError(f"The {attr} key is missing or mispelled.")

        else:
            raise ValueError("data was passed as None")

        # Record properties
        self.location_name = data["location name"]
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
    def from_location_or_key(cls, location_or_key: str):
        """Generates a ScenarioPack isinstance from a location contained within the
        ALL_LOCATIONS or ALL_KEYS lists.

        Parameters
        ----------
        location_or_key : str
            String containing the location name of the ScenarioPack to load or
            the key of that ScenarioPack.

        Returns
        -------
        ScenarioPack
            ScenarioPack instance at the specified location
        """
        target_key = _validate_location(location=location_or_key)
        return cls(data=ALL_SCENARIOS[target_key])

    @classmethod
    def from_index(cls, index: int):
        """Generates a ScenarioPack instance from an index referring to any of the
            ALL_LOCATIONS or ALL_KEYS lists.

        Parameters
        ----------
        location : int, optional
            An integer containing the index of the ScenarioPack to load

        Returns
        -------
        ScenarioPack
            ScenarioPack instance at the specified index value
        """
        target_key = _validate_location(location=index)
        return cls(data=ALL_SCENARIOS[target_key])

    @staticmethod
    def show_all_available_locations(
        format: str = "list",
    ) -> typing.Union[str, DataFrame]:
        """Simple function that lists all functions available prior to loading a
        specific ScenarioPack instance

        Parameters
        ----------
        format : str
            Format for the list to be returned, either 'list' or 'dataframe',
            default is 'list'.

        Returns
        -------
        list
            List of locations available for manipulation
        """
        return _show_available_locations(format=format)

    def __repr__(self) -> str:
        s = (
            f"Sea level rise at {self.location_name}; "
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
        # If everything checks out, return the Scenario of interest within the Pack
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
            The difference is primarily cosmetic
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
            proj[scenario.short_name] = scenario.by_horizon_year(
                horizon_year=horizon_year
            )
        ds = Series(
            data=proj,
            name=f"SLR at {self.location_name} by {horizon_year} [{self.units}]",
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
        ax.set_title(f"SLR for {self.location_name}")
        ax.legend()

        return ax
