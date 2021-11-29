# SLR
SLR is simple package designed to manipulate sea-level projections using the Python language.

## What SLR Does
SLR relies on a single configuration file, named `scenarios.json` to load pre-configured sea-level rise scenarios at specific locations, wrapped under a single `SLRScenarios` class instance. Custom scenarios can also be built using the `Scenario` class instance. SLR provides convenient class instances to perform the following routine tasks:

* Load sea-level rise projections for a specific location
* Display trajectories over time as plots or tables
* Evaluate sea-level rise offset by a certain horizon date
* Compare risk-based sea-level rise trajectories

More locations can be added by modifying and contributing to the `scenarios.json` file.

## Installation
The best way to install the package is to pip install from GitHub.com, or cloning the repo on your local machine.

## Quickstart (Jupyter)

SLR provides a very easy way to manipulate sea-level rise scenario datasets. The SLR package was built with convenience in mind and is designed to facilite operations commonly encountered when dealing with sea-level rise projections at specific locations. It is primarily designed to be used within Jupyter and is geared toward practitioners who need to publish their findings in reports.

### Importing SLR
The easiest way to use SLR is to locally amend PYTHONPATH, or after installation, select:

```python
import src as slr
```

### Available Locations
From that point on, wee locations available in the projection dataset:
```python
slr.SLRScenarios.show_all_available_locations()
```

### Manipulating SLR Scenarios
Let's load a set of projections by invoking a builtin classmethod:
```python
sf = slr.SLRScenarios.from_location(location="San Francisco")
```

We could do the same using indexing
```python
sf = slr.SLRScenarios.from_index(index=0)
```

SLR projections available at that location can be displayed and copy/pasted into a report
```python
sf.dataframe
```

### Visualization
We can plot those projections right away; let's convert to feet for easier interpretation and let's add a target date
```python
sf.convert(to_units='ft')
sf.plot(horizon_year=2075)
plt.tight_layout()
```

Here is what this should look like:

![projections](https://user-images.githubusercontent.com/46502166/143791203-32a194a6-169a-4bb7-81e0-087fb889ffcd.png)

### Calculating Projections
We can calculate the effective SLR projections by a certain date, e.g.:
```python
sf.by_horizon_year(2075, merge=False)
```

We can also choose to merge that projection into the dataframe, for presentation purposes. Note that the `SLRScenarios` class instance is not affected by the merging operation.
```python
sf.by_horizon_year(horizon_year=2075, merge=True)
```

### Drilling Into Specific Scenarios
Each `SLRScenarios` instance contains one or more `Scenario` instances which can be conveniently retrieved using index notation:
```python
sf_scenario = sf[1]
sf_scenario
```

Let's return to our prior example of visualization, and let's add this specific scenario:
```python
# Display a base figure using the builtin method
ax = sf.plot(horizon_year=2075)
# Add the specific Scenario instance
ax.plot(sf_scenario.data.x, sf_scenario.data.y, c='yellow', label='Selected for design', lw=10, alpha=.65)
# Use the builtin class method to estimate SLR by the horizon year
ax.axhline(y=sf_scenario.by_horizon_year(horizon_year=2075), c='k', ls='--', lw=1)
# Update the legend
plt.legend()
plt.tight_layout()
```

Here is what this should now look like:

![projections-plus](https://user-images.githubusercontent.com/46502166/143791670-ebfab835-3084-44e6-bcfb-a770f001c4ee.png)

## Customizing the `scenarios.json` File

SLR works by loading a JSON file located under `.\data\scenarios.json`. The format of the file mimics the structure of `SLRScenarios` and `Scenario` class instances. An example is shown for San Francisco, CA. The data was extracted from the 2018 State of California Sea-level Rise Guidance document published by the Ocean Council.

```json
{
    "San Francisco": {
        "description": "San Francisco, CA",
        "station ID (CO-OPS)": "9414290",
        "scenarios": [
            {
                "description": "High Emission, Low Risk (Likely Range)",
                "short name": "Low Risk",
                "units": "ft",
                "probability (CDF)": 0.83,
                "recommended by OPC": "yes",
                "baseline year": 2000,
                "data": {
                    "x": [
                        2030,
                        2040,
                        2050,
                        2060,
                        2070,
                        2080,
                        2090,
                        2100
                    ],
                    "y": [
                        0.5,
                        0.8,
                        1.1,
                        1.5,
                        1.9,
                        2.4,
                        2.9,
                        3.4
                    ]
                }
            },
            {
                "description": "High Emission, Medium-High Risk (1-in-200 Chance)",
                "short name": "Medium Risk",
                "units": "ft",
                "probability (CDF)": 0.995,
                "recommended by OPC": "yes",
                "baseline year": 2000,
                "data": {
                    "x": [
                        2030,
                        2040,
                        2050,
                        2060,
                        2070,
                        2080,
                        2090,
                        2100
                    ],
                    "y": [
                        0.8,
                        1.3,
                        1.9,
                        2.6,
                        3.5,
                        4.5,
                        5.6,
                        6.9
                    ]
                }
            },
            {
                "description": "High Emission, Extreme Risk (H++ Scenario)",
                "short name": "Extreme Risk",
                "units": "ft",
                "probability (CDF)": null,
                "recommended by OPC": "yes",
                "baseline year": 2000,
                "data": {
                    "x": [
                        2030,
                        2040,
                        2050,
                        2060,
                        2070,
                        2080,
                        2090,
                        2100
                    ],
                    "y": [
                        1.0,
                        1.8,
                        2.7,
                        3.9,
                        5.2,
                        6.6,
                        8.3,
                        10.2
                    ]
                }
            }
        ]
    }
}
```

New locations can be added using the same nomenclature. Currently, the following fields are implemented:

* "location": e.g. a string describing the `SLRScenarios` instance
  - "description": a description of the location for the SLR scenarios, e.g., "San Francisco, CA"
  - "station ID (CO-OPS)": the NOAA or CO-OPS identification string for the location, if available, e.g, "9414290"
  - "scenarios": an array of JSON objects containing specific scenarios
