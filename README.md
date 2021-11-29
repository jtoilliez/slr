# SLR
Sea Level Rise for Python

## Installation
The best way to install the package is to pip install from GitHub.com

## Quickstart (Jupyter)

SLR provides a very easy way to manipulate sea-level rise scenario datasets. The SLR package was built with convenience in mind and is designed to facilite operations commonly encountered when dealing with sea-level rise projections. It is primarily designed to be used within Jupyter.

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
# We can manipulate that make a custom plot
ax = sf.plot(horizon_year=2075)
ax.plot(sf_scenario.data.x, sf_scenario.data.y, c='yellow', label='Selected for design', lw=10, alpha=.65)
ax.axhline(y=sf_scenario.by_horizon_year(horizon_year=2075), c='k', ls='--', lw=1)
plt.legend()
plt.tight_layout()
```

Here is what this should now look like:

![projections-plus](https://user-images.githubusercontent.com/46502166/143791670-ebfab835-3084-44e6-bcfb-a770f001c4ee.png)
