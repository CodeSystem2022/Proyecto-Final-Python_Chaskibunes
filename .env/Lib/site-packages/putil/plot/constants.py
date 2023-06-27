# constants.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0302,W0105


###
# Global variables
###
AXIS_TICKS_FONT_SIZE = 14
"""
Axis tick labels font size in points

:type: integer
"""


AXIS_LABEL_FONT_SIZE = 18
"""
Axis labels font size in points

:type: integer
"""


LEGEND_SCALE = 1.5
"""
Scale factor for panel legend. The legend font size in points is equal to the
axis font size divided by the legend scale

:type: number
"""


LINE_WIDTH = 2.5
"""
Series line width in points

:type: float
"""


MARKER_SIZE = 14
"""
Series marker size in points

:type: integer
"""


MIN_TICKS = 6
"""
Minimum number of ticks desired for the independent and dependent axis of
a panel

:type: integer
"""


PRECISION = 10
"""
Number of mantissa significant digits used in all computations

:type: integer
"""


SUGGESTED_MAX_TICKS = 10
"""
Maximum number of ticks desired for the independent and dependent axis of a
panel. It is possible for a panel to have more than SUGGESTED_MAX_TICKS in the
dependent axis if one or more series are plotted with an interpolation function
and at least one interpolated curve goes above or below the maximum and minimum
data points of the panel. In this case the panel will have
SUGGESTED_MAX_TICKS+1 ticks if some interpolation curve is above the maximum
data point of the panel or below the minimum data point of the panel; or the
panel will have SUGGESTED_MAX_TICKS+2 ticks if some interpolation curve(s)
is(are) above the maximum data point of the panel and below the minimum data
point of the panel

:type: integer
"""


TITLE_FONT_SIZE = 24
"""
Figure title font size in points

:type: integer
"""
