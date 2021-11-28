# SLR
Sea Level Rise for Python

## Installation

## Tutorial

First load the various modules:
> `from src import data, scenario`

See locations available in the projection dataset:
> `scenario.SLRScenarios.show_all_available_locations()`

Let's load a set of projections
> `sf = scenario.SLRScenarios.from_location(location="San Francisco")`

We could do the same using indexing
> `sf = scenario.SLRScenarios.from_index(index=0)`