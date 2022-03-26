from functools import cache
import json
import urllib.request
import warnings

from numpy import nan
from slr.scenario import Scenario
from pandas import DataFrame


class NOAASLR:

    @cache
    def __init__(self, station_id: str = None, **kwargs) -> None:

        # NOAA returns cm if metric is selected; in if english is selected
        _report_year = kwargs.pop("Report Year", 2022)
        _units = kwargs.pop("Data Units", "metric")
        if _units == "metric":
            self.units = "cm"
        else:
            self.units = "in"

        self._station_ID = station_id
        self._base_URL = (
            "https://api.tidesandcurrents.noaa.gov/dpapi/prod/webapi/product"
            "/slr_projections.json"
        )

        # Get the trend object from NOAA API
        link = (
            rf"{self._base_URL}"
            rf"/?station={self._station_ID}"
            rf"&units={_units}"
            rf"&report_year={_report_year}"
        )

        # Load and append
        with urllib.request.urlopen(link) as url:
            try:
                data = json.loads(url.read())["SlrProjections"]
            except ConnectionError:
                warnings.warn("Something came up while retrieving data from NOAA")

        self._data = DataFrame.from_dict(
            data
        )



        # Organize the data in Scenario instance, NOAA provides 4 basic scenarios:
        # * Low
        # * Intermediate-Low
        # * Intermediate
        # * Intermediate-High
        # * High
        # There are confidence intervals but I'm going to skip for now

        noaa_scenarios = {
            "Low" : {
                "Description": "NOAA Low",
                "Short Name": "NOAA Low",
                "Probability" : nan,
            }
        }

        scenario_ = (
            self._data[self._data.loc[:, "scenario"] == "Low"]
        )

        self.sc = Scenario(
            description="NOAA Low",
            short_name="NOAA Low",
            units=self.units,
            probability=.17,
            baseline_year=2005,
            data={
                'x': scenario_.loc[:, "projectionYear"].values,
                'y': scenario_.loc[:, "projectionRsl"].values
            },
        )

    def __repr__(self) -> str:
        return "That's a NOAA SLR object"

if __name__ == "__main__":
    ns = NOAASLR(station_id="9414290")
    print(ns.sc)
