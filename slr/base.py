import numpy as np
M_TO_FT = 3.281



class Dataset:
    def __init__(self,
        description: str,
        short_name: str,
        units: str,
        probability: float,
        data: dict = None
    ) -> None:

        # Dataset has certain attributes
        self.units = units
        self.description = description

        if probability >=0. and probability <= 1.:
            self.probability = probability
        else:
            raise ValueError(
                f"Probability {self.probability} is not within [0; 1].")

        # Save the data as Data
        self.data = Data(units=units, data=data)

class Data:
    def __init__(self, units: str, data: dict) -> None:
        
        # Check for length of data
        if len(data["x"]) != len(data["y"]):
            raise ValueError(
                "The two arrays passed in the data dictionary have discordant lengths!"
            )

        # Check the units using the helper function
        self._check_units(units=units)

        # Actually load the data
        self.x = np.array(data["x"])
        self.y = np.array(data["y"])
        self.units = units

    def _check_units(self, units: str) -> None:
        if not (units in ['ft', 'in', 'm', 'cm']):
            raise ValueError(
                f"Units {units} are not supported; only use 'ft', " 
                f"'in', 'm', and 'cm'.")

    def _convert(self, to_units: str) -> None:
        # Check the units
        self._check_units(to_units)

        # Change the units of the y value on the spot
        if self.units == 'ft':
            if to_units == 'in':
                fac = 12.
            if to_units == 'ft':
                fac = 1.
            if to_units == 'm' :
                fac = 1 / M_TO_FT
            if to_units == 'cm' :
                fac = 1 / M_TO_FT * 100
        if self.units == 'in':
            if to_units == 'in':
                fac = 1.
            if to_units == 'ft':
                fac = 1/12.
            if to_units == 'm' :
                fac = 1/12. * 1 / M_TO_FT
            if to_units == 'cm' :
                fac = 1/12. * 1 / M_TO_FT * 100
        if self.units == 'm':
            if to_units == 'in':
                fac = 12. * M_TO_FT
            if to_units == 'ft':
                fac = M_TO_FT
            if to_units == 'm' :
                fac = 1.
            if to_units == 'cm' :
                fac = 100.
        if self.units == 'cm':
            if to_units == 'in':
                fac = 12. * M_TO_FT * 1/100.
            if to_units == 'ft':
                fac = M_TO_FT * 1/100
            if to_units == 'm' :
                fac = 1/100.
            if to_units == 'cm' :
                fac = 1.
        
        # Apply the transformation
        self.y = self.y * fac
        self.units = to_units