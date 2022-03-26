import urllib.request
import json
import warnings
import re
from typing import Union

import numpy as np

from functools import cache
from slr.utils import _check_units
from slr.slrprojections import SLRProjections
from pandas import Timestamp, DataFrame, date_range, DateOffset, Series


class HistoricalSLR:
    """HistoricalSLR will attempt to download and retrieve historical Sea Level
    Rise data for a particular location. Station ID and units must be provided.

    Attributes
    ----------
    station_ID : str, optional
        String describing the NOAA ID, e.g. "9410660", by default None
    units : str, optional
        One of the allowable units to be used for storing the historical trend
        can be either one of 'm', 'mm', 'in', 'cm', or 'ft', by default None

    Methods
    --------
    noaa_properties(format):
        Properties describing the HistoricalSLR object as provided by NOAA.
    from_slrprojections(cls, slrprojections):
        Will attempt to retrieve historical SLR information from NOAA servers using
        a SLRProjections item as seed.s
    """

    @cache
    def __init__(self, station_ID: str = None, units: str = None) -> None:

        """[summary]

        Raises
        ------
        ValueError
            [description]
        """
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
        self._zero_year = 2000
        self.trend = data["trend"]
        self.trend_error = data["trendError"]
        self.trend_units = re.findall(r"([a-z]*)[/].", data["units"])[0]
        try:
            self.start_date = Timestamp(data["startDate"])
            self.end_date = Timestamp(data["endDate"])
        except ValueError:
            raise ValueError("Unable to parse start and end dates from response.")

        # Build the historical trend
        self.timeseries = self._build_timeseries()

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

    def _build_timeseries(self) -> Series:

        index = date_range(
            start=Timestamp(self.start_date.year, 6, 15),
            end=Timestamp(self.end_date.year, 6, 15),
            freq=DateOffset(years=1),
        )
        values = np.full_like(index, fill_value=np.nan, dtype=float)
        values[0] = self.trend * (self.start_date.year - self._zero_year)
        values[-1] = self.trend * (self.end_date.year - self._zero_year)

        # Stitch it together
        ts = (
            DataFrame(
                data=values,
                index=index,
                columns=[f"Historical SLR [{self.trend_units}]"],
            )
            .interpolate(method="time")
            .squeeze()
        )
        return ts

    @classmethod
    def from_slrprojections(cls, slrprojections: SLRProjections = None):
        # Read the station ID from the slrprojections
        location = slrprojections.station_ID
        units = slrprojections.units
        if not isinstance(units, str):
            raise TypeError(
                "There are mixed units in the SLRProjections object."
                "Cannot infer units."
            )
        return cls(station_ID=location, units=units)
