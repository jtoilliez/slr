import typing
from pathlib import Path
import json

from matplotlib.axes import Axes
from pandas import DataFrame, Series

scenarios = Path(__file__).parent / "data/scenarios.json"
with open(scenarios) as f:
    data = json.load(f)


class SeaLevelRise:
    def __init__(
        self, location: typing.Optional[typing.Union[str, int]] = None
    ) -> None:
        """Create a new SeaLevelRise based on location. Provides methods to
        plot and evaluate long-term sea-level rise projections.
        Parameters
        ----------
        location : Given as a str (e.g. "San Francisco") or int (e.g. 0), optional
            Location is matched to source data in the COCAT guidance, by default None
        """
        self.data = data
        self._locations = list(self.data.keys())
        if location is not None:
            # If a specific location was provided, then go ahead and make projections
            self._location = self._validate_location(location)
            self.table, self.narrative = self._get_data_frame_and_narrative(
                location=self._location, output_narrative=True
            )

    def __repr__(self) -> str:
        try:
            string_ = (
                f"SeaLevelRise for location {self._location}"   
            )
        except AttributeError:
            string_ = "SeaLevelRise object, location not defined"
        return string_

    @property
    def location(self) -> typing.Union[int, str]:
        return self._location

    @property
    def locations(self) -> list:
        return self._locations

    def _validate_location(self, location: typing.Union[str, int]) -> str:

        if isinstance(location, int):
            if not (location in list(range(0, len(self._locations)))):
                raise ValueError("Index notation exceeds length of locations")
            else:
                target_location = self._locations[location]
        else:
            if not (location in self._locations):
                raise ValueError("Make sure location is in the dataset")
            else:
                target_location = location

        return target_location

    def _handle_optional_location(
        self, location: typing.Optional[typing.Union[str, int]]
    ) -> typing.Tuple[str, DataFrame]:

        # Managing location
        if location is None:
            # We don't have a location passed: use the set one or make one up
            if not hasattr(self, "table"):
                temp_location = self._validate_location(location=0)
                temp_table = self._get_data_frame_and_narrative(
                    location=temp_location, output_narrative=False
                )
            # There is existing data, let's use what is already there
            else:
                temp_location = self._location
                temp_table = self.table
        else:
            # We have a location passed explicitly: let's use this one but
            # don't change the instance
            temp_location = self._validate_location(location=location)
            temp_table = self._get_data_frame_and_narrative(
                location=temp_location, output_narrative=False
            )

        return (temp_location, temp_table)

    def by_horizon_date(
        self,
        horizon_year: float,
        location: typing.Optional[typing.Union[str, int]] = None,
    ) -> Series:
        """Generate a Series with projected (estimated or looked up) values for SLR
        for the specified location.
        Parameters
        ----------
        horizon_year : float or int
            Value for the horizon year (e.g. what will be SLR by 2055?)
        location : either one of the several options for locations, optional
            Inherited from the object, by default None
        Returns
        -------
        Series
            List of projected values by the horizon year.
        Raises
        ------
        ValueError
            If the horizon year exceeds the range provided in the original data.
        """

        # Handle optional location
        temp_location, temp_table = self._handle_optional_location(location)

        # Check for horizon year
        if (horizon_year > temp_table.index.max()) or (
            horizon_year < temp_table.index.min()
        ):
            raise ValueError(
                "Target year is out of bounds for this location, "
                f"years range from {temp_table.index.min()} to "
                f"{temp_table.index.max()}."
            )

        # Easy case if horizon_year is already in index:
        if horizon_year in temp_table.index:
            ds = temp_table.loc[horizon_year]
        else:
            # Else you need to calculate
            ds = (
                temp_table.reindex(list(temp_table.index.values) + [horizon_year])
                .sort_index()
                .interpolate()
            ).loc[horizon_year]

        return ds

    def plot(
        self,
        ax: Axes,
        location: typing.Optional[typing.Union[str, int]] = None,
        horizon_year: float = None,
    ) -> Axes:

        # Handle optional location:
        temp_location, temp_table = self._handle_optional_location(location)

        # Graphics
        for index, series in temp_table.iteritems():
            ax.plot(series, label=series.name)

        # Handle horizon year
        if horizon_year is not None:
            temp_ds_horizon = self.by_horizon_date(
                horizon_year=horizon_year, location=temp_location
            )
            ax.axvline(x=horizon_year, **{"ls": "--", "lw": 1, "c": "lightgray"})
            for name, val in temp_ds_horizon.iteritems():
                ax.scatter(
                    x=horizon_year, y=val, label=f"{val} ft by {int(horizon_year)}"
                )

        ax.set_ylabel("SLR [ft]")
        ax.set_title(f"{data[temp_location]['description']}")
        ax.legend()

        return ax

    def _get_data_frame_and_narrative(
        self,
        location: typing.Union[str, int],
        output_narrative: typing.Optional[bool] = False,
    ) -> typing.Union[DataFrame, typing.Tuple[DataFrame, str]]:
        """Generate a table of projections for the specified location
        Parameters
        ----------
        location : typing.Union[str, int]
            Location to look up; either str or int
        output_narrative : bool, optional
            If True, then returns a lorem ipsum with text for copy/paste into a Word
            document, typically, by default False
        Returns
        -------
        Returns either a DataFrame or a tuple (DataFrame, str)
            DataFrame contains the projected SLR values and
            str contains the narrative.
        """

        target_location = self._validate_location(location)

        # Prepare dataset
        list_of_y = dict()
        for pack_ in data[target_location]["dataset"]:
            name_ = f'{pack_["short name"]} [{pack_["units"]}]'
            list_of_y[name_] = pack_["data"]["y"]

        df = DataFrame(data=list_of_y, index=pack_["data"]["x"]).rename_axis(
            "Year", axis=0
        )

        # Generate narrative from OPC document
        narrative = (
            "Probabilistic projections for the height of sea-level rise "
            "are shown below, "
            "along with the H++ scenario (Extreme Risk). "
            f"These projections are specific to "
            f"{data[target_location]['description']}, "
            "and follow the "
            "State of California Sea Level Rise Guidance, "
            "issued by the Ocean Protection "
            "Council (OPC). "
            "The 2018 update to the Guidance was developed "
            "by OPC, in coordination with the California Natural "
            "Resources Agency, the Governor’s Office of "
            "Planning and Research, and the California Energy "
            "Commission. "
            "The H++ projection is a "
            "single scenario and does not have an associated likelihood of occurrence "
            "as do the probabilistic projections. Probabilistic projections "
            "are with respect to a baseline of the year 2000, "
            "or more specifically the average relative sea level over 1991 - 2009. "
            "Recommended projections for use are those shown, specifically Low, "
            "Medium-high and Extreme Risk aversion. These recommended projections were "
            "generated using RCP 8.5. "
            "These projections were valid at the time of writing. "
            "Based on recommendations from OPC’s Scientific "
            "Working Group, OPC anticipates updating the "
            "Guidance periodically, and at a minimum of every five "
            "years, to reflect the latest scientific understanding "
            "of climate change driven sea-level rise in California. "
            "Rapid advances in science and subsequent "
            "release of relevant, peer-reviewed studies from "
            "the Intergovernmental Panel on Climate Change "
            "(IPCC), state and national climate assessments, and "
            "equivalently recognized sources may generate the "
            "need for more frequent updates."
        )

        # Return formatted data for this location as a Pandas.DataFrame
        if output_narrative:
            return (df, narrative)
        else:
            return df

    @classmethod
    def from_dict(cls, dic: dict):
        location = dic.pop("location", "San Francisco")
        return cls(location=location)

if __file__ == "main":
    proj = SeaLevelRise(location=1)
    print(proj.location)