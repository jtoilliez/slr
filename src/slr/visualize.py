from .historical import HistoricalSLR
from .slrprojections import SLRProjections
import matplotlib.pyplot as plt
from typing import Union


def HistoricalVsProjections(
        location: Union[str, int],
        ax: plt.Axes = None
) -> plt.Axes:
    """Will match two objects, HistoricalSLR and SLRProjections
    given a location and make a combined plot. Useful when looking
    for a quick figure.

    Parameters
    ----------
    location : Union[str, int]
        Use the same int, str nomenclature as that used for creating
        a new SLRProjections object, i.e.:
        * an integer, e.g., '0'
        * a station ID, e.g. '9419750'
        * a city e.g., 'Los Angeles, CA'
    ax : plt.Axes, optional
        _description_, by default None

    Returns
    -------
    plt.Axes
        _description_
    """

    # Create the SLRProjections instance:
    ps = SLRProjections.from_location(location=location)
    # Convert to 'mm'
    ps.convert(to_units='mm', inplace=True)

    # Create the Historical instance:
    hs = HistoricalSLR.from_slrprojections(slrprojections=ps)

    # Create an ax figure if none provided
    if ax is None:
        _, ax = plt.subplots(1, 1)

    ax.plot(
        hs.timeseries.index.year,
        hs.timeseries.values,
        label='Historical trend',
        ls='--', c='k', lw=2
    )
    for scenario_ in ps.scenarios:
        ax.plot(
            scenario_.data.x,
            scenario_.data.y,
            label=scenario_.short_name
        )
    ax.set_xlabel('Year')
    ax.set_ylabel(f'SLR from 2000 in [{ps.units}]')
    ax.set_xlim(
        ax.get_xlim()[0],
        2100
    )
    plt.legend(loc='best')

    return ax
