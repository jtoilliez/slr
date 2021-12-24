from slr.utils import ALL_SCENARIOS


def test_health_json_data():
    # Test health of the master SLR dataset
    for _, pack in ALL_SCENARIOS.items():
        assert "location name" in pack
        assert "station ID (CO-OPS)" in pack
        assert "scenarios" in pack
        for elem in pack["scenarios"]:
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
