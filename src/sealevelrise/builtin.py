from sealevelrise.scenario import Scenario
from sealevelrise.slrprojections import SLRProjections

from sealevelrise.utils import ALL_BUILTIN_SCENARIOS, _validate_key


class BuiltinProjections(SLRProjections):
    def __init__(self, key: str):
        """Generates a SLRProjections isinstance from one of the builtin scenarios.

        Parameters
        ----------
        key : str
        A unique key defining the builtin scenarios item, e.g., 'cocat-2018-9414290'

        Returns
        -------
        SLRProjections
            A SLRProjections instance corresponding to the key provided
        """

        target_key = _validate_key(key=key)
        data = ALL_BUILTIN_SCENARIOS[target_key]

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

        super().__init__(
            scenarios=scenarios_list,
            location_name=location_name,
            station_id=station_id,
            issuer=issuer,
            url=url,
        )
