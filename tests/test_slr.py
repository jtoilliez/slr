import pytest
import numpy as np

from slr.slr import SeaLevelRise, data

def test_location():
    location=1
    proj = SeaLevelRise(location=location)
    assert proj.location == list(data.keys())[location]

def test_horizon_date():
    location=0
    proj=SeaLevelRise(location=location)
    assert proj.by_horizon_date(2050).values.all()==np.array([0.5, 0.8, 1. ]).all()