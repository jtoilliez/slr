import urllib
import json
import warnings
import re
from typing import Union

from functools import cache
from slr.utils import _check_units
from slr.scenariopack import ScenarioPack
from pandas import Timestamp, DataFrame


class HistoricalSLR:
    @cache
    def __init__(self, station_ID: str = None, units: str = None) -> None:
        _check_units(units)
        self._station_ID = station_ID
        self._base_URL = (
            "https://api.tidesandcurrents.noaa.gov/dpapi/prod/webapi/product"
            "/sealvltrends.json"
        )

        # Get the trend object from NOAA API
        link = rf"{self._base_URL}" rf"/?station={self._station_ID}" rf"&affil=US"

        # Load and append
        with urllib.request.urlopen(link) as url:
            try:
                data = json.loads(url.read())["SeaLvlTrends"][0]
            except ConnectionError:
                warnings.warn("Something came up while retrieving data from NOAA")

        self._data = data

        # Parse data and write to object
        self.trend = data["trend"]
        self.trend_error = data["trendError"]
        self.trend_units = re.findall(r"([a-z]*)[/].", data["units"])[0]
        try:
            self.start_date = Timestamp(data["startDate"])
            self.end_date = Timestamp(data["endDate"])
        except ValueError:
            raise ValueError("Unable to parse start and end dates from response.")

    def noaa_properties(self, format: str = None) -> Union[DataFrame, str]:
        """Properties describing the HistoricalSLR object as provided by NOAA.

        Parameters
        ----------
        format : str, optional, by default None
            Options for format include:
                - 'dataframe' : will return a pandas DataFrame
                - 'narrative' : will return a formatted string with all properties
                - None : will return properties as dictionary (default)

        Returns
        -------
        Union[DataFrame, str]
            Depending on format option, either:
                - Narrative in plain text format for inclusion in a report, etc.
                - DataFrame with neatly formatted parameters describing the historical
                  trend at the location.

        """
        if format is None:
            return self._data
        elif format == "dataframe":
            df = DataFrame.from_dict(
                data=self._data, orient="index", columns=["Value"]
            ).rename_axis(index="Parameter")
            return df.rename(
                {
                    str_: re.sub(r"(\w)([A-Z])", r"\1 \2", str_).title()
                    for str_ in df.index
                },
                axis=0,
            )
        elif format == "narrative":
            out_str = (
                f"Historical sea-level rise information was retrieved at Station "
                f"{self._station_ID} operated by NOAA CO-OPS. "
                f"The relative sea level trend at that location reads "
                f"{self.trend} {self.trend_units} "
                f"per year with a 95% confidence interval of +/- {self.trend_error} "
                f"{self.trend_units} based on monthly mean sea level data from "
                f"{self.start_date.year} to {self.end_date.year} (approximately "
                f"{self.end_date.year - self.start_date.year} years in total). "
                f"This is equivalent to a change of "
                f"{self.trend * 100} {self.trend_units} in 100 years."
            )
            return out_str

    @classmethod
    def from_scenariopack(cls, scenariopack: ScenarioPack = None):
        # Read the station ID from the scenariopack
        location = scenariopack.station_ID
        units = scenariopack.units
        if not isinstance(units, str):
            raise TypeError(
                "There are mixed units in the ScenarioPack object. Cannot infer units."
            )
        return cls(station_ID=location, units=units)
