from functools import cache
import json
import urllib.request
import warnings

from sealevelrise.scenario import Scenario
from sealevelrise.slrprojections import SLRProjections
from pandas import DataFrame


class NOAASLRProjections(SLRProjections):
    def __init__(self, station_id: str = None, **kwargs) -> None:

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
        link = (
            rf"{_base_URL}"
            rf"/?station={_station_ID}"
            rf"&units={_units}"
            rf"&report_year={_report_year}"
        )

        # Load and append
        with urllib.request.urlopen(link) as url:
            try:
                data = json.loads(url.read())["SlrProjections"]
            except ConnectionError:
                warnings.warn("Something came up while retrieving data from NOAA")

        _data = DataFrame.from_dict(data)

        # Organize the data in Scenario instance, NOAA provides 5 basic scenarios:
        # * Low
        # * Intermediate-Low
        # * Intermediate
        # * Intermediate-High
        # * High
        # There are confidence intervals but I'm going to skip for now

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

        super().__init__(
            scenarios=scenarios,
            location_name=location_name.replace("_", " ").title(),
            station_id=station_id,
            issuer=(
                "National Oceanographic and Atmospheric Administration, "
                "Sea Level Rise Projections, 2022"
            ),
            url=(
                "https://oceanservice.noaa.gov/hazards/"
                "sealevelrise/sealevelrise-tech-report.html"
            ),
        )

        self.noaa_properties = _data


if __name__ == "__main__":
    ns = NOAASLRProjections(station_id="9414290")
    print(ns.scenarios[0])
