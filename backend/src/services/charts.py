from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


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
    is_pie = any(s.type == chartType.PIE for s in series)

    option: dict[str, Any] = {
        "tooltip": {"trigger": "axis" if x_axis_categories else "item"},
        "legend": {
            "bottom": "0px",
            "left": "center",
            "type": "scroll"
        },
        "series": [s.model_dump(mode="json") for s in series],
        }
  
    if not is_pie:
        option["xAxis"] = {"type": "category", "data": x_axis_categories}
        option["yAxis"] = {"type": "value"}

    if title:
        option.update({"title": {"text": title}})

    return option