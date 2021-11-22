import pytest
import numpy as np

from slr.slr import SeaLevelRise, data


def test_location():
    location = 1
    proj = SeaLevelRise(location=location)
    assert proj.location == list(data.keys())[location]


def test_horizon_date():
    location = 0
    proj = SeaLevelRise(location=location)
    assert proj.by_horizon_date(2050).values.all() == np.array([0.5, 0.8, 1.0]).all()


def test_health_json_data():
    # Test health of the master SLR dataset
    for _, pack in data.items():
        assert "description" in pack
        assert "station ID (CO-OPS)" in pack
        assert "datasets" in pack
        for elem in pack["datasets"]:
            assert "short name" in elem
            assert "units" in elem
            assert "probability (CDF)" in elem
            # Make sure probability checks out
            assert (
                isinstance(elem["probability (CDF)"], float)
                or elem["probability (CDF)"] is None
            )
            assert "baseline year" in elem
            assert "data" in elem
            # Now look at the data itself
            assert "x" in elem["data"]
            assert "y" in elem["data"]
            assert isinstance(elem["data"]["x"], list)
            assert isinstance(elem["data"]["y"], list)

