import os
import string
from grafanalib.core import *


datasource = os.environ['DASHBOARD_DATASOURCE']
refIds = list(string.ascii_uppercase)

BROWN_RGBA = RGBA(189, 118, 31, 0.18)
BROWN_RGB = RGB(193, 120, 31)
RED_RGBA = RGBA(245, 54, 54, 0.18)
RED_RGB = RGB(245, 54, 54)
GREEN_RGBA = RGBA(50, 172, 45, 0.18)
GREEN_RGB = RGB(50, 172, 45)
GREY_RGBA = RGBA(216, 216, 216, 0.18)
GREY_RGB = RGB(216, 216, 216)


def percentage_gauge(title, exprs, show_sparkline=True, span=3, height=150):
    return SingleStat(
        title=title,
        dataSource=datasource,
        targets=[
            Target(expr=exprs[ii], refId=refIds[ii]) for ii in range(len(exprs))],
        format = PERCENT_UNIT_FORMAT,
        sparkline = SparkLine(show=show_sparkline),
        thresholds = '80,90',
        valueName = 'current',
        gauge = Gauge(show=True, thresholdMarkers=True),
        span = span,
        height = height
    )

def number(title, exprs, show_sparkline=True, span=2, height=100, format=NO_FORMAT, thresholds="",
           colors=None, colors_reverse=False, colorValue=False, valueMaps=[], sparkline=None):

    if not colors:
        if colors_reverse:
            _colors = [RED, ORANGE, GREEN]
        else:
            _colors = [GREEN, ORANGE, RED]
    if not sparkline and show_sparkline:
        _sparkline = SparkLine(show=show_sparkline, fillColor=BLUE_RGBA, lineColor=BLUE_RGB)
    else:
        _sparkline = sparkline
    return SingleStat(
        title=title,
        dataSource=datasource,
        targets=[
            Target(expr=exprs[ii], refId=refIds[ii]) for ii in range(len(exprs))],
        format = format,
        colors = _colors,
        colorValue = colorValue,
        height = height,
        valueMaps = valueMaps,
        sparkline = _sparkline,
        span = span,
        thresholds = thresholds,
        valueName = 'current'
    )

def capacity_graph(title, exprs, span=3, format=SHORT_FORMAT, decimals=None):
    return Graph(
        title=title,
        dataSource=datasource,
        targets=[
            Target(expr=exprs[ii][0], legendFormat=exprs[ii][1], refId=refIds[ii]) for ii in range(len(exprs))],
        yAxes=single_y_axis(format=format, decimals=decimals),
        # alert = Alert(
        #     name='POD Usage Alert',
        #     message="High POD usage",
        #     alertConditions=[
        #         AlertCondition(
        #             Target(
        #                 refId='D',
        #             ),
        #             timeRange=TimeRange("5m", "now"),
        #             evaluator=GreaterThan(0.80),
        #             operator=OP_AND,
        #             reducerType=RTYPE_AVG,
        #         ),
        #     ],
        # ),
        span = span
    )
