import typing
import numpy as np
from pandas import Series

M_TO_FT = 3.281

# Check that units are valid
def _check_units(units: str) -> None:
    if not (units in ["ft", "in", "m", "cm"]):
        raise ValueError(
            f"Units {units} are not supported; only use 'ft', " f"'in', 'm', and 'cm'."
        )


# Data class contains the actual projection
class Data:
    def __init__(self, units: str, data: dict) -> None:
        """Data

        Parameters
        ----------
        units : str
            One of the allowable strings that define standard units for SLR
        data : dict
            A Data object that contains 'x' and 'y' keys with 'x' given as years and 'y'
            containing the SLR values for each year

        """
        # Check for length of data
        if len(data["x"]) != len(data["y"]):
            raise ValueError(
                "The two arrays passed in the data dictionary have discordant lengths!"
            )

        # Check the units using the helper function
        _check_units(units=units)

        # Check that the dictionary has the right keys
        if not (("x" in data.keys()) and ("y" in data.keys())):
            raise ValueError("Need 'x' and 'y' keys in the 'data' object")

        # Actually load the data
        self.x = np.array(data["x"])
        self.y = np.array(data["y"])
        self._units = units

    @property
    def units(self):
        return self._units

    def convert(
        self, to_units: str, inplace: bool = False
    ) -> typing.Union[None, np.ndarray]:
        """Convert units in data.y array

        Parameters
        ----------
        to_units : str
            Name of the units to convert toward, must be one of 'm', 'ft', 'in', and 'cm'
        inplace : bool, optional
            If true, the values in the data object are overwritten, by default False

        Returns
        -------
        typing.Union[None, np.ndarray]
            Returns either nothing (inplace=True) or an nd.ndarray with the converted values
        """
        # Check the units
        _check_units(to_units)

        # Change the units of the y value on the spot
        if self.units == "ft":
            if to_units == "in":
                fac = 12.0
            if to_units == "ft":
                fac = 1.0
            if to_units == "m":
                fac = 1 / M_TO_FT
            if to_units == "cm":
                fac = 1 / M_TO_FT * 100
        if self.units == "in":
            if to_units == "in":
                fac = 1.0
            if to_units == "ft":
                fac = 1 / 12.0
            if to_units == "m":
                fac = 1 / 12.0 * 1 / M_TO_FT
            if to_units == "cm":
                fac = 1 / 12.0 * 1 / M_TO_FT * 100
        if self.units == "m":
            if to_units == "in":
                fac = 12.0 * M_TO_FT
            if to_units == "ft":
                fac = M_TO_FT
            if to_units == "m":
                fac = 1.0
            if to_units == "cm":
                fac = 100.0
        if self.units == "cm":
            if to_units == "in":
                fac = 12.0 * M_TO_FT * 1 / 100.0
            if to_units == "ft":
                fac = M_TO_FT * 1 / 100
            if to_units == "m":
                fac = 1 / 100.0
            if to_units == "cm":
                fac = 1.0

        # Apply the transformation
        if inplace:
            self.y = self.y * fac
            self._units = to_units
        else:
            return self.y * fac

    def __repr__(self) -> str:
        s = f"Data in {self.units} ranging from {self.x[0]} to {self.x[-1]}"
        return s


# Dataset contains the entire information related to a single trajectory
class Dataset:
    def __init__(
        self,
        description: str,
        short_name: str,
        units: str,
        probability: float,
        baseline_year: int,
        data: dict,
    ) -> None:
        """Dataset represent a given sea-level rise trajectory, described by the below
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

    @property
    def units(self):
        return self.data.units

    def __repr__(self) -> str:
        s = (
            f"Dataset '{self.short_name}', values are given in {self.units} "
            f"and years range from {self.data.x[0]} to {self.data.x[-1]}"
        )
        return s


# SeaLevelRise contains SLR Dataset objects for a given location
class SeaLevelRise:
    def __init__(self, data=dict, coerce_units: bool = True) -> None:

        # Check that you have the right data in there
        for attr in ["description", "station ID (CO-OPS)", "datasets"]:
            if not attr in data:
                raise KeyError(f"The {attr} key is missing or mispelled.")

        # Record properties
        self.description = data["description"]
        self.station_ID = data["station ID (CO-OPS)"]

        # Record datasets
        datasets = data["datasets"]
        try:
            len(datasets)
            self.datasets = []
        except TypeError:
            raise TypeError("The datasets passed are not a list of dataset objects")

        # Record all dataset objects
        for dataset_ in datasets:
            self.datasets.append(
                Dataset(
                    description=dataset_["description"],
                    short_name=dataset_["short name"],
                    units=dataset_["units"],
                    probability=dataset_["probability (CDF)"],
                    baseline_year=dataset_["baseline year"],
                    data=dataset_["data"],
                )
            )

        # Additional attributes
        self.shape = (len(self.datasets),)

    @property
    def units(self):
        # Returns the units of each Dataset
        units = []
        for dataset in self.datasets:
            units.append(dataset.units)

        if all(x == units[0] for x in units):
            return units[0]
        else:
            return units

    def __repr__(self) -> str:
        s = f"Sea level rise at {self.description}; {self.shape[0]} Dataset(s) available"
        return s

    def by_horizon_date(self, horizon_year: float, coerce_errors: bool = False) -> None:
        """Generate a Series with projected values for SLR
        for a given horizon year for each Dataset.

        Parameters
        ----------
        horizon_year : float or int
            Value for the horizon year (e.g. 2055)
        coerce_errors: bool, optional
            If set to True (default), will coerce linear interpolation errors by replacing
            with np.nan; if set to False, will raise errors

        Returns
        -------
        Series
            List of projected values by the horizon year.
        
        Raises
        ------
        ValueError
            If the horizon year exceeds the range provided in the original data.
        """

        proj = dict()
        for dataset in self.datasets:
            # Check for horizon year
            if (horizon_year > dataset.data.x.max()) or (
                horizon_year < dataset.data.x.min()
            ):
                raise ValueError(
                    "Target year is out of bounds for this location, "
                    f"years range from {dataset.data.x.min()} to "
                    f"{dataset.data.x.max()}."
                )
            # Linearly interpolate value at the horizon_year
            proj[dataset.short_name] = np.interp(
                horizon_year, dataset.data.x, dataset.data.y
            )
        ds = Series(
            data=proj,
            name=f"SLR at {self.description} by {horizon_year} [{self.units}]",
        )
        return ds
