# SLR
Sea Level Rise for Python

## Installation
The best way to install the package is to pip install from GitHub.com

## Quickstart

SLR provides a very easy way to manipulate sea-level rise scenario datasets. The SLR package was built with convenience in mind and is designed to facilite operations commonly encountered when dealing with sea-level rise projections.

### Importing SLR
The easiest way to use SLR is to locally amend PYTHONPATH, or after installation, select:

> `import src as slr`

### Available Locations
From that point on, wee locations available in the projection dataset:
> `scenario.SLRScenarios.show_all_available_locations()`

### Manipulating SLR Scenarios
Let's load a set of projections by invoking a builtin classmethod:
> `sf = scenario.SLRScenarios.from_location(location="San Francisco")`

We could do the same using indexing
> `sf = scenario.SLRScenarios.from_index(index=0)`

Plotting SLR projections is made easy, and adding a specific `horizon_year` is convenient to mark a certain date:
![projections](https://user-images.githubusercontent.com/46502166/143791203-32a194a6-169a-4bb7-81e0-087fb889ffcd.png)
