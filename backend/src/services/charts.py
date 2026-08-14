from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# Our data follows this structure, we have three types of charts (can be expanded),
# We then have different series of data for each line or graph we make,
# And finally we have a more general class with the different series and some other options.
class chartType (str, Enum):
    LINE = "line"
    BAR = "bar"
    PIE = "pie"

class seriesInfo (BaseModel):
    name: str = Field(description="Name of the data series")
    type: chartType = Field(description="Chart type, either line, bar or pie")
    data: list[Any] = Field(description="Data values array for this series")

class eChartInfo (BaseModel):
    title: str|None = Field(default=None, description="Title of the chart")
    x_axis_categories: list[str]|None = Field(default=None, description="Labels for the x_axis")
    series: list[seriesInfo] = Field(description="One or more data series to plot.")

def get_echart_config(
        series: list[seriesInfo],
        title: str|None = None,
        x_axis_categories: list[str]|None = None
) -> dict[str, Any]:
    """Generates an Apache ECharts options dictionary.

    Args:
        series (list[seriesInfo]): A list of `seriesInfo` instances defining
            the plot data, series names, and chart types.
        title (str | None, optional): Main title for the chart. Defaults to None.
        categories (list[str] | None, optional): Category labels for the x-axis.
            When provided, sets the x-axis data and switches the tooltip trigger
            to 'axis' instead of 'item'. Defaults to None.

    Returns:
        dict[str, Any]: An ECharts option dictionary suitable for JSON serialization.
    """
    # Pie charts are very different from the rest so they need their own bool.
    is_pie = any(s.type == chartType.PIE for s in series)

    # We store the series with their config in this array.
    formatted_series = []

    for s in series:
        s_dict = s.model_dump(mode="json", exclude_none=True, by_alias=True)

        if s.type == chartType.LINE:
            s_dict.setdefault("areaStyle", {})
            s_dict.setdefault("smooth", True)

        formatted_series.append(s_dict)

    option: dict[str, Any] = {
        "tooltip": {"trigger": "axis" if x_axis_categories else "item"},
        "legend": {
            "bottom": 0,
            "left": "center",
            "type": "scroll"
        },
        "series": formatted_series,
        }

    if not is_pie:
        option["xAxis"] = {"type": "category", "data": x_axis_categories}
        option["yAxis"] = {"type": "value"}

    if title:
        option.update({"title": {"text": title}})

    return option