import typing
from copy import deepcopy

import json
import urllib.request
import warnings

from matplotlib.pyplot import Axes, subplots
from pandas import DataFrame, Series, concat

from sealevelrise.scenario import Scenario
from sealevelrise.utils import (
    ALL_BUILTIN_SCENARIOS,
    _check_units,
    _show_builtin_scenarios,
    _validate_key,
)


# Scenarios contains multiple Scenario objects for a given location,
# as well as additional metadata
class Scenarios:
    def __init__(
        self,
        scenarios: typing.Union[Scenario, typing.List[Scenario]] = None,
        location_name: str = None,
        station_id: str = None,
        issuer: str = None,
        url: str = None,
        coerce_units: bool = True,
    ) -> None:
        """Scenarios contains SLR scenarios for a specific location defined
        by its name or NOAA ID (preferred).

        Parameters
        ----------
        data : dict, optional
            Data describing the scenarios, by default None
        coerce_units : bool, optional
            If true, will harmonize units in all scenarios provided, by default True

        """

        self.location_name = location_name
        self.station_id = station_id
        self.issuer = issuer
        self.url = url
        self.scenarios = scenarios
        self.shape = (len(self.scenarios),)

    @classmethod
    def from_dict(cls, data: dict):
        """Constructs a Scenarios instance from a dictionary

        Parameters
        ----------
        data : dict
            Dictionary that has the basic info required to build Scenarios

        Returns
        -------
        Scenarios
            A new Scenarios instance
        """

        # Check that you have the right data in there
        if not isinstance(data, dict):
            raise TypeError("data needs to be dictionary")
        if data is not None:
            for attr in ["location name", "station ID (CO-OPS)", "scenarios"]:
                if attr not in data:
                    raise KeyError(f"The {attr} key is missing or mispelled.")
        else:
            raise ValueError("data was passed as None")

        # Record properties; optional are popped
        location_name = data["location name"]
        station_id = data["station ID (CO-OPS)"]
        issuer = data["issuer"]
        # Optional properties
        url = data.pop("URL", None)

        # Build the scenarios from the dictionary
        scenarios_data = data["scenarios"]

        # Record all Scenario objects into a list of Scenario objects
        scenarios_list = list()

        # Iterate over each items in the dictionary
        for scenario_ in scenarios_data:
            scenarios_list.append(
                Scenario(
                    description=scenario_["description"],
                    short_name=scenario_["short name"],
                    units=scenario_["units"],
                    probability=scenario_["probability (CDF)"],
                    baseline_year=scenario_["baseline year"],
                    data=scenario_["data"],
                )
            )

        return cls(
            scenarios=scenarios_list,
            location_name=location_name,
            station_id=station_id,
            issuer=issuer,
            url=url,
        )

    @classmethod
    def from_builtin(cls, key: typing.Union[str, int]):
        """Generates a Scenarios isinstance from one of the builtin scenarios.

        Parameters
        ----------
        key : typing.Union[str, int]
        A unique key defining the builtin scenarios item. It can be given as
        either:

        * a location (e.g., 'New Jersey')
        * an int (e.g., '0')
        * a key from the scenarios.json file, e.g., 'cocat-2018-9414290'

        In case multiple matches are possible, the first match will be returned.

        Returns
        -------
        Scenarios
            Scenarios instance corresponding to the key provided
        """
        target_key = _validate_key(key=key)
        return cls.from_dict(data=ALL_BUILTIN_SCENARIOS[target_key])

    @classmethod
    def from_noaa(cls, station_id: str = None, **kwargs):
        # NOAA returns cm if metric is selected; in if english is selected
        _report_year = kwargs.pop("Report Year", 2022)
        _units = kwargs.pop("Data Units", "metric")
        if _units == "metric":
            units = "cm"
        else:
            units = "in"

        _station_ID = station_id
        _base_URL = (
            "https://api.tidesandcurrents.noaa.gov/dpapi/prod/webapi/product"
            "/slr_projections.json"
        )

        # Get the trend object from NOAA API
        _link = (
            rf"{_base_URL}"
            rf"/?station={_station_ID}"
            rf"&units={_units}"
            rf"&report_year={_report_year}"
        )

        # Load and append
        with urllib.request.urlopen(_link) as url:
            try:
                data = json.loads(url.read())["Scenarios"]
            except ConnectionError:
                warnings.warn("Something came up while retrieving data from NOAA")

        _data = DataFrame.from_dict(data)

        # NOAA has specific scenarios, and these are their properties
        noaa_scenario_props = {
            "Low": {
                "Description": "NOAA Low",
                "Short Name": "Low",
                "Probability": None,
            },
            "Intermediate-Low": {
                "Description": "NOAA Intermediate-Low",
                "Short Name": "Intermediate-Low",
                "Probability": None,
            },
            "Intermediate": {
                "Description": "NOAA Intermediate",
                "Short Name": "Intermediate",
                "Probability": None,
            },
            "Intermediate-High": {
                "Description": "NOAA Intermediate-High",
                "Short Name": "Intermediate-High",
                "Probability": None,
            },
            "High": {
                "Description": "NOAA High",
                "Short Name": "High",
                "Probability": None,
            },
        }

        # Launch the sequence and create the list of scenarios
        scenarios = list()
        for key_ in noaa_scenario_props.keys():
            scenario_ = _data[_data.loc[:, "scenario"] == key_]
            scenarios.append(
                Scenario(
                    description=noaa_scenario_props[key_]["Description"],
                    short_name=noaa_scenario_props[key_]["Short Name"],
                    units=units,
                    probability=noaa_scenario_props[key_]["Probability"],
                    baseline_year=2005,
                    data={
                        "x": scenario_.loc[:, "projectionYear"].values,
                        "y": scenario_.loc[:, "projectionRsl"].values,
                    },
                )
            )
        
        # The name of the location is retrieved from the last scenario_ chunk
        location_name = scenario_.loc[:, "stationName"].values[0]



    @staticmethod
    def show_all_builtin_scenarios(
        format: str = "list",
    ) -> typing.Union[str, DataFrame]:
        """Simple function that lists all builtin scenarios available

        Parameters
        ----------
        format : str
            Format for the list to be returned, either 'list' or 'dataframe',
            default is 'list'.

        Returns
        -------
        list or DataFrame
            List of locations available for manipulation
        """
        return _show_builtin_scenarios(format=format)

    def __repr__(self) -> str:
        s = (
            f"Sea level rise Projections for {self.location_name} "
            f"issued by {self.issuer}; there are "
            f"{self.shape[0]} Scenario(s) available."
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

    def convert(self, to_units: str, inplace: bool = False) -> DataFrame:
        """Provides on the fly or inplace units conversion for all Scenarios
        within a Scenarios instance.

        Parameters
        ----------
        to_units : str
            The value of the destination units, which can only be one of:
            * 'm'
            * 'cm'
            * 'in'
            * 'ft'
            * 'mm'
        inplace : bool, optional
            Wether the conversion is 'on the fly' (inplace=False),
            or if that conversion is burnt in the current Scenarios instance
            (inplace=Trie). By default set to False (on-the-fly behavior)

        Returns
        -------
        DataFrame
            Only returns the DataFrame of the resultant converted set of projections.
        """
        # Check the units
        _check_units(to_units)

        # Scan over Scenario objects and change the units
        if inplace:
            for scenario_ in self.scenarios:
                scenario_.data.convert(to_units=to_units, inplace=True)
            return self.dataframe
        else:
            # create a deep copy and output it
            temp = deepcopy(self)
            for scenario_ in temp.scenarios:
                scenario_.data.convert(to_units=to_units, inplace=True)
            return temp.dataframe

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


if __name__ == "__main__":
    sf = Scenarios.from_builtin(key="NPCC3-new-york-2019")
    print(sf)
    print(sf.scenarios[1].short_name)
    print(sf.url)
    print(sf.scenarios[1].by_horizon_year(horizon_year=2055))
    print(sf.scenarios[1].units)
    print(Scenarios.show_all_builtin_scenarios(format="dataframe"))
