# panel.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0302,R0912,R0913,R0914,R0915,W0105,W0212

# PyPI imports
import numpy
import matplotlib.pyplot as plt
# Putil imports
import putil.exh
import putil.pcontracts
from .series import Series
from .functions import _F, _intelligent_ticks, _uniquify_tick_labels
from .constants import AXIS_LABEL_FONT_SIZE, AXIS_TICKS_FONT_SIZE, LEGEND_SCALE


###
# Exception tracing initialization code
###
"""
[[[cog
import os, sys
if sys.hexversion < 0x03000000:
    import __builtin__
else:
    import builtins as __builtin__
sys.path.append(os.environ['TRACER_DIR'])
import trace_ex_plot_panel
exobj_plot = trace_ex_plot_panel.trace_module(no_print=True)
]]]
[[[end]]]
"""


###
# Functions
###
def _legend_position_validation(obj):
    """ Validate if a string is a valid legend position """
    options = [
        'BEST', 'UPPER RIGHT', 'UPPER LEFT', 'LOWER LEFT', 'LOWER RIGHT',
        'RIGHT', 'CENTER LEFT', 'CENTER RIGHT', 'LOWER CENTER',
        'UPPER CENTER', 'CENTER'
    ]
    if (obj is not None) and (not isinstance(obj, str)):
        return True
    if ((obj is None) or
       (obj and any([item.lower() == obj.lower() for item in options]))):
        return False
    return True


###
# Class
###
class Panel(object):
    r"""
    Defines a panel within a figure

    :param series: One or more data series
    :type  series: :py:class:`putil.plot.Series` *or list of*
                   :py:class:`putil.plot.Series` *or None*

    :param primary_axis_label: Primary dependent axis label
    :type  primary_axis_label: string

    :param primary_axis_units: Primary dependent axis units
    :type  primary_axis_units: string

    :param primary_axis_ticks: Primary dependent axis tick marks. If not None
                               overrides automatically generated tick
                               marks if the axis type is linear. If None
                               automatically generated tick marks are used for
                               the primary axis
    :type  primary_axis_ticks: list, Numpy vector or None

    :param secondary_axis_label: Secondary dependent axis label
    :type  secondary_axis_label: string

    :param secondary_axis_units: Secondary dependent axis units
    :type  secondary_axis_units: string

    :param secondary_axis_ticks: Secondary dependent axis tick marks. If not
                                 None overrides automatically generated tick
                                 marks if the axis type is linear. If None
                                 automatically generated tick marks are used
                                 for the secondary axis
    :type  secondary_axis_ticks: list, Numpy vector or None

    :param log_dep_axis: Flag that indicates whether the dependent (primary and
                         /or secondary) axis is linear (False) or logarithmic
                         (True)
    :type  log_dep_axis: boolean

    :param legend_props: Legend properties. See
                         :py:attr:`putil.plot.Panel.legend_props`. If None the
                         legend is placed in the best position in one column
    :type  legend_props: dictionary or None

    :param display_indep_axis: Flag that indicates whether the independent axis
                               is displayed (True) or not (False)
    :type  display_indep_axis: boolean

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.plot.panel.Panel.__init__

    :raises:
     * RuntimeError (Argument \`display_indep_axis\` is not valid)

     * RuntimeError (Argument \`legend_props\` is not valid)

     * RuntimeError (Argument \`log_dep_axis\` is not valid)

     * RuntimeError (Argument \`primary_axis_label\` is not valid)

     * RuntimeError (Argument \`primary_axis_ticks\` is not valid)

     * RuntimeError (Argument \`primary_axis_units\` is not valid)

     * RuntimeError (Argument \`secondary_axis_label\` is not valid)

     * RuntimeError (Argument \`secondary_axis_ticks\` is not valid)

     * RuntimeError (Argument \`secondary_axis_units\` is not valid)

     * RuntimeError (Argument \`series\` is not valid)

     * RuntimeError (Legend property \`cols\` is not valid)

     * RuntimeError (Series item *[number]* is not fully specified)

     * TypeError (Legend property \`pos\` is not one of ['BEST', 'UPPER
       RIGHT', 'UPPER LEFT', 'LOWER LEFT', 'LOWER RIGHT', 'RIGHT', 'CENTER
       LEFT', 'CENTER RIGHT', 'LOWER CENTER', 'UPPER CENTER', 'CENTER']
       (case insensitive))

     * ValueError (Illegal legend property \`*[prop_name]*\`)

     * ValueError (Series item *[number]* cannot be plotted in a
       logarithmic axis because it contains negative data points)

    .. [[[end]]]
    """
    # pylint: disable=R0902,R0903,W0102
    def __init__(self, series=None, primary_axis_label='',
                 primary_axis_units='', primary_axis_ticks=None,
                 secondary_axis_label='', secondary_axis_units='',
                 secondary_axis_ticks=None, log_dep_axis=False,
                 legend_props=None, display_indep_axis=False):
        # Private attributes
        self._series = None
        self._primary_axis_label = None
        self._secondary_axis_label = None
        self._primary_axis_units = None
        self._secondary_axis_units = None
        self._primary_axis_ticks = None
        self._secondary_axis_ticks = None
        self._log_dep_axis = None
        self._recalculate_series = False
        self._legend_props = {'pos':'BEST', 'cols':1}
        self._display_indep_axis = None
        # Private attributes
        self._legend_pos_list = [
            'best', 'upper right', 'upper left', 'lower left', 'lower right',
            'right', 'center left', 'center right', 'lower center',
            'upper center', 'center'
        ]
        self._panel_has_primary_axis = False
        self._panel_has_secondary_axis = False
        self._primary_dep_var_min = None
        self._primary_dep_var_max = None
        self._primary_dep_var_div = None
        self._primary_dep_var_unit_scale = None
        self._primary_dep_var_locs = None
        self._primary_dep_var_labels = None
        self._secondary_dep_var_min = None
        self._secondary_dep_var_max = None
        self._secondary_dep_var_div = None
        self._secondary_dep_var_unit_scale = None
        self._secondary_dep_var_locs = None
        self._secondary_dep_var_labels = None
        self._legend_props_list = ['pos', 'cols']
        self._legend_props_pos_list = [
            'BEST', 'UPPER RIGHT', 'UPPER LEFT', 'LOWER LEFT', 'LOWER RIGHT',
            'RIGHT', 'CENTER LEFT', 'CENTER RIGHT', 'LOWER CENTER',
            'UPPER CENTER', 'CENTER'
        ]
        # Exceptions definition
        invalid_prim_ex = putil.exh.addai('primary_axis_ticks')
        invalid_sec_ex = putil.exh.addai('secondary_axis_ticks')
        invalid_prim_ex(
            (primary_axis_ticks is not None) and (
            (not isinstance(primary_axis_ticks, list)) and
            (not isinstance(primary_axis_ticks, numpy.ndarray))
            )
        )
        invalid_sec_ex(
            (secondary_axis_ticks is not None) and (
            (not isinstance(secondary_axis_ticks, list)) and
            (not isinstance(secondary_axis_ticks, numpy.ndarray)))
        )
        # Assignment of arguments to attributes
        # Order here is important to avoid unnecessary re-calculating of
        # panel axes if log_dep_axis is True
        self._set_log_dep_axis(log_dep_axis)
        self._primary_axis_ticks = (
            primary_axis_ticks
            if not self.log_dep_axis else
            None
        )
        self._secondary_axis_ticks = (
            secondary_axis_ticks
            if not self.log_dep_axis else
            None
        )
        self._set_series(series)
        self._set_primary_axis_label(primary_axis_label)
        self._set_primary_axis_units(primary_axis_units)
        self._set_secondary_axis_label(secondary_axis_label)
        self._set_secondary_axis_units(secondary_axis_units)
        self._set_legend_props(legend_props)
        self._set_display_indep_axis(display_indep_axis)

    def __bool__(self): # pragma: no cover
        """
        Returns :code:`True` if the panel has at least a series associated
        with it, :code:`False` otherwise

        .. note:: This method applies to Python 3.x
        """
        return self._series is not None

    def __iter__(self):
        """
        Returns an iterator over the series object(s) in the panel. For
        example:

        .. =[=cog
        .. import docs.support.incfile
        .. docs.support.incfile.incfile('plot_example_6.py', cog.out)
        .. =]=
        .. code-block:: python

            # plot_example_6.py
            from __future__ import print_function
            import numpy, putil.plot

            def panel_iterator_example(no_print):
                source1 = putil.plot.BasicSource(
                    indep_var=numpy.array([1, 2, 3, 4]),
                    dep_var=numpy.array([1, -10, 10, 5])
                )
                source2 = putil.plot.BasicSource(
                    indep_var=numpy.array([100, 200, 300, 400]),
                    dep_var=numpy.array([50, 75, 100, 125])
                )
                series1 = putil.plot.Series(
                    data_source=source1,
                    label='Goals'
                )
                series2 = putil.plot.Series(
                    data_source=source2,
                    label='Saves',
                    color='b',
                    marker=None,
                    interp='STRAIGHT',
                    line_style='--'
                )
                panel = putil.plot.Panel(
                    series=[series1, series2],
                    primary_axis_label='Time',
                    primary_axis_units='sec',
                    display_indep_axis=True
                )
                if not no_print:
                    for num, series in enumerate(panel):
                        print('Series {0}:'.format(num+1))
                        print(series)
                        print('')
                else:
                    return panel

        .. =[=end=]=

        .. code-block:: python

            >>> import docs.support.plot_example_6 as mod
            >>> mod.panel_iterator_example(False)
            Series 1:
            Independent variable: [ 1.0, 2.0, 3.0, 4.0 ]
            Dependent variable: [ 1.0, -10.0, 10.0, 5.0 ]
            Label: Goals
            Color: k
            Marker: o
            Interpolation: CUBIC
            Line style: -
            Secondary axis: False
            <BLANKLINE>
            Series 2:
            Independent variable: [ 100.0, 200.0, 300.0, 400.0 ]
            Dependent variable: [ 50.0, 75.0, 100.0, 125.0 ]
            Label: Saves
            Color: b
            Marker: None
            Interpolation: STRAIGHT
            Line style: --
            Secondary axis: False
            <BLANKLINE>
        """
        return iter(self._series)

    def __nonzero__(self):  # pragma: no cover
        """
        Returns :code:`True` if the panel has at least a series associated
        with it, :code:`False` otherwise

        .. note:: This method applies to Python 2.x
        """
        return self._series is not None

    def _get_series(self):
        return self._series

    def _set_series(self, series):
        # pylint: disable=C0103
        self._series = (
            (series if isinstance(series, list) else [series])
            if series is not None else
            series
        )
        self._recalculate_series = False
        if self.series is not None:
            self._validate_series()
            self._panel_has_primary_axis = any(
                [not series_obj.secondary_axis for series_obj in self.series]
            )
            self._panel_has_secondary_axis = any(
                [series_obj.secondary_axis for series_obj in self.series]
            )
            comp_prim_dep_var = (
                (not self.log_dep_axis) and self._panel_has_primary_axis
            )
            comp_sec_dep_var = (
                (not self.log_dep_axis) and self._panel_has_secondary_axis
            )
            panel_has_primary_interp_series = any(
                [
                    (not series_obj.secondary_axis) and
                    (series_obj.interp_dep_var is not None)
                    for series_obj in self.series
                ]
            )
            panel_has_secondary_interp_series = any(
                [
                    series_obj.secondary_axis and
                    (series_obj.interp_dep_var is not None)
                    for series_obj in self.series
                ]
            )
            # Compute panel scaling factor
            primary_min = None
            prim_interp_min = None
            secondary_min = None
            sec_interp_min = None
            primary_max = None
            prim_interp_max = None
            secondary_max = None
            sec_interp_max = None
            panel_min = None
            panel_max = None
            # Find union of all data points and panel minimum and maximum.
            # If panel has logarithmic dependent axis, limits are common and
            # the union of the limits of both axis
            # Primary axis
            glob_prim_dep_var = (
                numpy.unique(
                    numpy.concatenate(
                        [
                            series_obj.dep_var
                            for series_obj in self.series
                            if not series_obj.secondary_axis
                        ]
                    )
                )
                if comp_prim_dep_var else
                None
            )
            prim_interp_min = (
                min(
                    [
                        min(series_obj.dep_var)
                        for series_obj in self.series
                        if ((not series_obj.secondary_axis) and
                           (series_obj.interp_dep_var is not None))
                    ]
                )
                if panel_has_primary_interp_series else
                None
            )
            prim_interp_max = (
                max(
                    [
                        max(series_obj.dep_var)
                        for series_obj in self.series
                        if ((not series_obj.secondary_axis) and
                           (series_obj.interp_dep_var is not None))
                    ]
                )
                if panel_has_primary_interp_series else
                None
            )
            primary_min = (
                min(min(glob_prim_dep_var), prim_interp_min)
                if comp_prim_dep_var and (prim_interp_min is not None) else
                (min(glob_prim_dep_var) if comp_prim_dep_var else None)
            )
            primary_max = (
                max(max(glob_prim_dep_var), prim_interp_max)
                if comp_prim_dep_var and (prim_interp_min is not None) else
                (max(glob_prim_dep_var) if comp_prim_dep_var else None)
            )
            # Secondary axis
            glob_sec_dep_var = (
                numpy.unique(
                    numpy.concatenate(
                        [
                            series_obj.dep_var
                            for series_obj in self.series
                            if series_obj.secondary_axis
                        ]
                    )
                )
                if comp_sec_dep_var else
                None
            )
            sec_interp_min = (
                min(
                    [
                        min(series_obj.dep_var)
                        for series_obj in self.series
                        if (series_obj.secondary_axis and
                           (series_obj.interp_dep_var is not None))
                    ]
                ).tolist()
                if panel_has_secondary_interp_series else
                None
            )
            sec_interp_max = (
                max(
                    [
                        max(series_obj.dep_var)
                        for series_obj in self.series
                        if (series_obj.secondary_axis and
                           (series_obj.interp_dep_var is not None))
                    ]
                ).tolist()
                if panel_has_secondary_interp_series else
                None
            )
            secondary_min = (
                min(min(glob_sec_dep_var), sec_interp_min)
                if comp_sec_dep_var and (sec_interp_min is not None) else
                (min(glob_sec_dep_var) if comp_sec_dep_var else None)
            )
            secondary_max = (
                max(max(glob_sec_dep_var), sec_interp_max)
                if comp_sec_dep_var and (sec_interp_max is not None) else
                (max(glob_sec_dep_var) if comp_sec_dep_var else None)
            )
            # Global (for logarithmic dependent axis)
            glob_panel_dep_var = (
                None
                if not self.log_dep_axis else
                numpy.unique(
                    numpy.concatenate(
                        [series_obj.dep_var for series_obj in self.series]
                    )
                )
            )
            panel_min = (
                min(min(glob_panel_dep_var), prim_interp_min)
                if self.log_dep_axis and panel_has_primary_interp_series else
                (min(glob_panel_dep_var) if self.log_dep_axis else None)
            )
            panel_max = (
                max(max(glob_panel_dep_var), prim_interp_max)
                if self.log_dep_axis and panel_has_primary_interp_series else
                (max(glob_panel_dep_var) if self.log_dep_axis else None)
            )
            panel_min = (
                min(min(glob_panel_dep_var), sec_interp_min)
                if self.log_dep_axis and panel_has_secondary_interp_series else
                (min(glob_panel_dep_var) if self.log_dep_axis else None)
            )
            panel_max = (
                max(max(glob_panel_dep_var), sec_interp_max)
                if self.log_dep_axis and panel_has_secondary_interp_series else
                (max(glob_panel_dep_var) if self.log_dep_axis else None)
            )
            # Get axis tick marks locations
            if comp_prim_dep_var:
                (
                    self._primary_dep_var_locs,
                    self._primary_dep_var_labels,
                    self._primary_dep_var_min,
                    self._primary_dep_var_max,
                    self._primary_dep_var_div,
                    self._primary_dep_var_unit_scale
                ) = _intelligent_ticks(
                        glob_prim_dep_var,
                        primary_min,
                        primary_max,
                        tight=False,
                        log_axis=self.log_dep_axis,
                        tick_list=self._primary_axis_ticks,
                    )
            if comp_sec_dep_var:
                (
                    self._secondary_dep_var_locs,
                    self._secondary_dep_var_labels,
                    self._secondary_dep_var_min,
                    self._secondary_dep_var_max,
                    self._secondary_dep_var_div,
                    self._secondary_dep_var_unit_scale
                ) = _intelligent_ticks(
                        glob_sec_dep_var,
                        secondary_min,
                        secondary_max,
                        tight=False,
                        log_axis=self.log_dep_axis,
                        tick_list=self._secondary_axis_ticks,
                    )
            if self.log_dep_axis and self._panel_has_primary_axis:
                (
                    self._primary_dep_var_locs,
                    self._primary_dep_var_labels,
                    self._primary_dep_var_min,
                    self._primary_dep_var_max,
                    self._primary_dep_var_div,
                    self._primary_dep_var_unit_scale
                ) = _intelligent_ticks(
                        glob_panel_dep_var,
                        panel_min,
                        panel_max,
                        tight=False,
                        log_axis=self.log_dep_axis
                    )
            if self.log_dep_axis and self._panel_has_secondary_axis:
                (
                    self._secondary_dep_var_locs,
                    self._secondary_dep_var_labels,
                    self._secondary_dep_var_min,
                    self._secondary_dep_var_max,
                    self._secondary_dep_var_div,
                    self._secondary_dep_var_unit_scale
                ) = _intelligent_ticks(
                        glob_panel_dep_var,
                        panel_min,
                        panel_max,
                        tight=False,
                        log_axis=self.log_dep_axis
                    )
            # Equalize number of ticks on primary and secondary axis so that
            # ticks are in the same percentage place within the dependent
            # variable plotting interval (for non-logarithmic panels)
            # If there is any tick override (primary and/or secondary) this
            # is not done, the user assumes responsibility for aesthetics of
            # final result
            if ((not self.log_dep_axis) and
               self._panel_has_primary_axis and
               self._panel_has_secondary_axis and
               (self._primary_axis_ticks is None) and
               (self._secondary_axis_ticks is None)):
                max_ticks = max(
                    len(self._primary_dep_var_locs),
                    len(self._secondary_dep_var_locs)
                )-1
                primary_delta = (
                    (
                        self._primary_dep_var_locs[-1]-
                        self._primary_dep_var_locs[0]
                    )
                    /
                    float(max_ticks)
                )
                secondary_delta = (
                    (
                        self._secondary_dep_var_locs[-1]-
                        self._secondary_dep_var_locs[0]
                    )
                    /
                    float(max_ticks)
                )
                self._primary_dep_var_locs = [
                    self._primary_dep_var_locs[0]+(num*primary_delta)
                    for num in range(max_ticks+1)
                ]
                self._secondary_dep_var_locs = [
                    self._secondary_dep_var_locs[0]+(num*secondary_delta)
                    for num in range(max_ticks+1)
                ]
                (
                    self._primary_dep_var_locs,
                    self._primary_dep_var_labels
                ) = _uniquify_tick_labels(
                        self._primary_dep_var_locs,
                        self._primary_dep_var_locs[0],
                        self._primary_dep_var_locs[-1]
                    )
                (
                    self._secondary_dep_var_locs,
                    self._secondary_dep_var_labels
                ) = _uniquify_tick_labels(
                        self._secondary_dep_var_locs,
                        self._secondary_dep_var_locs[0],
                        self._secondary_dep_var_locs[-1]
                    )
            self._primary_axis_ticks = self._primary_dep_var_locs
            self._secondary_axis_ticks = self._secondary_dep_var_locs
            # Scale panel
            self._scale_dep_var(
                self._primary_dep_var_div,
                self._secondary_dep_var_div
            )

    def _get_primary_axis_scale(self):
        return self._primary_dep_var_div

    def _get_primary_axis_ticks(self):
        return self._primary_axis_ticks

    def _get_secondary_axis_scale(self):
        return self._secondary_dep_var_div

    def _get_secondary_axis_ticks(self):
        return self._secondary_axis_ticks

    def _get_primary_axis_label(self):
        return self._primary_axis_label

    @putil.pcontracts.contract(primary_axis_label='None|str')
    def _set_primary_axis_label(self, primary_axis_label):
        self._primary_axis_label = primary_axis_label

    def _get_primary_axis_units(self):
        return self._primary_axis_units

    @putil.pcontracts.contract(primary_axis_units='None|str')
    def _set_primary_axis_units(self, primary_axis_units):
        self._primary_axis_units = primary_axis_units

    def _get_secondary_axis_label(self):
        return self._secondary_axis_label

    @putil.pcontracts.contract(secondary_axis_label='None|str')
    def _set_secondary_axis_label(self, secondary_axis_label):
        self._secondary_axis_label = secondary_axis_label

    def _get_secondary_axis_units(self):
        return self._secondary_axis_units

    @putil.pcontracts.contract(secondary_axis_units='None|str')
    def _set_secondary_axis_units(self, secondary_axis_units):
        self._secondary_axis_units = secondary_axis_units

    def _get_log_dep_axis(self):
        return self._log_dep_axis

    @putil.pcontracts.contract(log_dep_axis='None|bool')
    def _set_log_dep_axis(self, log_dep_axis):
        self._recalculate_series = self.log_dep_axis != log_dep_axis
        self._log_dep_axis = log_dep_axis
        if self._recalculate_series:
            self._set_series(self._series)

    def _get_display_indep_axis(self):
        return self._display_indep_axis

    @putil.pcontracts.contract(display_indep_axis='None|bool')
    def _set_display_indep_axis(self, display_indep_axis):
        self._display_indep_axis = display_indep_axis

    def _get_legend_props(self):
        return self._legend_props

    @putil.pcontracts.contract(legend_props='None|dict')
    def _set_legend_props(self, legend_props):
        invalid_ex = putil.exh.addex(
            ValueError, 'Illegal legend property `*[prop_name]*`'
        )
        illegal_ex = putil.exh.addex(
            TypeError,
            "Legend property `pos` is not one of ['BEST', 'UPPER RIGHT', "
            "'UPPER LEFT', 'LOWER LEFT', 'LOWER RIGHT', 'RIGHT', "
            "'CENTER LEFT', 'CENTER RIGHT', 'LOWER CENTER', "
            "'UPPER CENTER', 'CENTER'] (case insensitive)"
        )
        cols_ex = putil.exh.addex(
            RuntimeError, 'Legend property `cols` is not valid'
        )
        self._legend_props = (
            legend_props
            if legend_props is not None else
            {'pos':'BEST', 'cols':1}
        )
        self._legend_props.setdefault('pos', 'BEST')
        self._legend_props.setdefault('cols', 1)
        for key, value in self.legend_props.items():
            invalid_ex(
                key not in self._legend_props_list, _F('prop_name', key)
            )
            illegal_ex(
                (key == 'pos') and
                _legend_position_validation(self.legend_props['pos'])
            )
            cols_ex(
                ((key == 'cols') and (not isinstance(value, int))) or
                ((key == 'cols') and
                (isinstance(value, int) is True) and (value < 0))
            )
        self._legend_props['pos'] = self._legend_props['pos'].upper()

    def __str__(self):
        """
        Prints panel information. For example:

        .. code-block:: python

            >>> from __future__ import print_function
            >>> import docs.support.plot_example_6 as mod
            >>> print(mod.panel_iterator_example(True))
            Series 0:
               Independent variable: [ 1.0, 2.0, 3.0, 4.0 ]
               Dependent variable: [ 1.0, -10.0, 10.0, 5.0 ]
               Label: Goals
               Color: k
               Marker: o
               Interpolation: CUBIC
               Line style: -
               Secondary axis: False
            Series 1:
               Independent variable: [ 100.0, 200.0, 300.0, 400.0 ]
               Dependent variable: [ 50.0, 75.0, 100.0, 125.0 ]
               Label: Saves
               Color: b
               Marker: None
               Interpolation: STRAIGHT
               Line style: --
               Secondary axis: False
            Primary axis label: Time
            Primary axis units: sec
            Secondary axis label: not specified
            Secondary axis units: not specified
            Logarithmic dependent axis: False
            Display independent axis: True
            Legend properties:
               cols: 1
               pos: BEST
        """
        ret = ''
        if (self.series is None) or (len(self.series) == 0):
            ret += 'Series: None\n'
        else:
            for num, element in enumerate(self.series):
                ret += 'Series {0}:\n'.format(num)
                temp = str(element).split('\n')
                temp = [3*' '+line for line in temp]
                ret += '\n'.join(temp)
                ret += '\n'
        ret += 'Primary axis label: {0}\n'.format(
            self.primary_axis_label
            if self.primary_axis_label not in ['', None] else
            'not specified'
        )
        ret += 'Primary axis units: {0}\n'.format(
            self.primary_axis_units
            if self.primary_axis_units not in ['', None] else
            'not specified'
        )
        ret += 'Secondary axis label: {0}\n'.format(
            self.secondary_axis_label
            if self.secondary_axis_label not in ['', None] else
            'not specified'
        )
        ret += 'Secondary axis units: {0}\n'.format(
            self.secondary_axis_units
            if self.secondary_axis_units not in ['', None] else
            'not specified'
        )
        ret += 'Logarithmic dependent axis: {0}\n'.format(self.log_dep_axis)
        ret += (
            'Display independent '
            'axis: {0}\n'.format(self.display_indep_axis)
        )
        ret += 'Legend properties:\n'
        iobj = enumerate(sorted(list(self.legend_props.items())))
        for num, (key, value) in iobj:
            ret += '   {0}: {1}{2}'.format(
                key, value, '\n' if num+1 < len(self.legend_props) else ''
            )
        return ret

    def _validate_series(self):
        """
        Verifies that elements of series list are of the right type and
        fully specified
        """
        invalid_ex = putil.exh.addai('series')
        incomplete_ex = putil.exh.addex(
            RuntimeError, 'Series item *[number]* is not fully specified'
        )
        log_ex = putil.exh.addex(
            ValueError,
            'Series item *[number]* cannot be plotted in a logarithmic '
            'axis because it contains negative data points'
        )
        for num, obj in enumerate(self.series):
            invalid_ex(not isinstance(obj, Series))
            incomplete_ex(not obj._complete, _F('number', num))
            log_ex(
                bool((min(obj.dep_var) <= 0) and self.log_dep_axis),
                _F('number', num)
            )

    def _get_complete(self):
        """
        Returns True if panel is fully specified, otherwise returns False
        """
        return (self.series is not None) and (len(self.series) > 0)

    def _scale_indep_var(self, scaling_factor):
        """ Scale independent variable of panel series """
        for series_obj in self.series:
            series_obj._scale_indep_var(scaling_factor)

    def _scale_dep_var(self, primary_scaling_factor, secondary_scaling_factor):
        """ Scale dependent variable of panel series """
        for series_obj in self.series:
            if not series_obj.secondary_axis:
                series_obj._scale_dep_var(primary_scaling_factor)
            else:
                series_obj._scale_dep_var(secondary_scaling_factor)

    def _setup_axis(self, axis_type, axis_obj, dep_min, dep_max, tick_locs,
                    tick_labels, axis_label, axis_units, axis_scale):

        """ Configure dependent axis """
        # pylint: disable=R0201
        # Set function pointers
        xflist = [
            axis_obj.xaxis.grid, axis_obj.set_xlim, axis_obj.xaxis.set_ticks,
            axis_obj.xaxis.set_ticklabels, axis_obj.xaxis.set_label_text
        ]
        yflist = [
            axis_obj.yaxis.grid, axis_obj.set_ylim, axis_obj.yaxis.set_ticks,
            axis_obj.yaxis.set_ticklabels, axis_obj.yaxis.set_label_text
        ]
        (fgrid, flim, fticks, fticklabels, fset_label_text) = (
            xflist
            if axis_type.upper() == 'INDEP' else
            yflist
        )
        # Process
        fgrid(True, 'both')
        flim((dep_min, dep_max), emit=True, auto=False)
        fticks(tick_locs)
        axis_obj.tick_params(
            axis='x' if axis_type.upper() == 'INDEP' else 'y',
            which='major',
            labelsize=AXIS_TICKS_FONT_SIZE
        )
        fticklabels(tick_labels)
        if (axis_label not in [None, '']) or (axis_units not in [None, '']):
            axis_label = '' if axis_label is None else axis_label.strip()
            unit_scale = '' if axis_scale is None else axis_scale.strip()
            fset_label_text(
                axis_label +
                (
                    ''
                    if (unit_scale == '') and (axis_units == '') else
                    (
                        ' [{unit_scale}{units}]'.format(
                            unit_scale=unit_scale,
                            units='-' if axis_units == '' else axis_units
                        )
                    )
                ),
                fontdict={'fontsize':AXIS_LABEL_FONT_SIZE}
            )

    def _draw_panel(self, axarr_prim, indep_axis_dict, print_indep_axis):
        """ Draw panel series """
        # pylint: disable=W0612
        axarr_sec = (
            axarr_prim.twinx()
            if self._panel_has_secondary_axis else
            None
        )
        # Place data series in their appropriate axis (primary or secondary)
        for series_obj in self.series:
            series_obj._draw_series(
                axarr_prim if not series_obj.secondary_axis else axarr_sec,
                indep_axis_dict['log_indep'],
                self.log_dep_axis
            )
        # Set up tick labels and axis labels
        if self._panel_has_primary_axis:
            self._setup_axis(
                'DEP',
                axarr_prim,
                self._primary_dep_var_min,
                self._primary_dep_var_max,
                self._primary_dep_var_locs,
                self._primary_dep_var_labels,
                self.primary_axis_label,
                self.primary_axis_units,
                self._primary_dep_var_unit_scale
            )
        if self._panel_has_secondary_axis:
            self._setup_axis(
                'DEP',
                axarr_sec,
                self._secondary_dep_var_min,
                self._secondary_dep_var_max,
                self._secondary_dep_var_locs,
                self._secondary_dep_var_labels,
                self.secondary_axis_label,
                self.secondary_axis_units,
                self._secondary_dep_var_unit_scale
            )
        if ((not self._panel_has_primary_axis) and
           self._panel_has_secondary_axis):
            axarr_prim.yaxis.set_visible(False)
        # Print legend
        if (len(self.series) > 1) and (len(self.legend_props) > 0):
            _, primary_labels = (
                axarr_prim.get_legend_handles_labels()
                if self._panel_has_primary_axis else
                (None, [])
            )
            _, secondary_labels = (
                axarr_sec.get_legend_handles_labels()
                if self._panel_has_secondary_axis else
                (None, [])
            )
            lprim = len(primary_labels)
            lsec = len(secondary_labels)
            labels = (
                (
                    [r'$\Leftarrow$'+label for label in primary_labels]+
                    [label+r'$\Rightarrow$' for label in secondary_labels]
                )
                if (lprim > 0) and (lsec > 0) else
                primary_labels+secondary_labels
            )
            if any([bool(label) for label in labels]):
                leg_artist = [
                    series_obj._legend_artist(LEGEND_SCALE)
                    for series_obj in self.series
                    if series_obj._check_series_is_plottable()
                ]
                legend_axis = (
                    axarr_prim
                    if self._panel_has_primary_axis else
                    axarr_sec
                )
                loc_key = self._legend_pos_list.index(
                            self.legend_props['pos'].lower()
                            if 'pos' in self.legend_props else 'lower left'
                )

                legend_axis.legend(
                    leg_artist,
                    labels,
                    ncol=self.legend_props['cols']
                         if 'cols' in self.legend_props else
                         len(labels),
                    loc=self._legend_pos_list[loc_key],
                    numpoints=1,
                    fontsize=AXIS_LABEL_FONT_SIZE/LEGEND_SCALE
                )
                # Fix Matplotlib issue where when there is primary and
                # secondary axis the legend box of one axis is transparent for
                # the axis/series of the other
                # From: http://stackoverflow.com/questions/17158469/
                #       legend-transparency-when-using-secondary-axis
                if (self._panel_has_primary_axis and
                    self._panel_has_secondary_axis):
                    axarr_prim.set_zorder(1)
                    axarr_prim.set_frame_on(False)
                    axarr_sec.set_frame_on(True)
        #  Print independent axis tick marks and label
        (indep_var_min, indep_var_max, indep_var_locs) = (
            indep_axis_dict['indep_var_min'],
            indep_axis_dict['indep_var_max'],
            indep_axis_dict['indep_var_locs']
        )
        indep_var_labels = (
            indep_axis_dict['indep_var_labels']
            if ('indep_var_labels' in indep_axis_dict) and
               (indep_axis_dict['indep_var_labels'] is not None) else
            None
        )
        indep_axis_label = (
            ''
            if indep_axis_dict['indep_axis_label'] is None or
               not print_indep_axis else
            indep_axis_dict['indep_axis_label'].strip()
        )
        indep_axis_units = (
            ''
            if indep_axis_dict['indep_axis_units'] is None or
               not print_indep_axis else
            indep_axis_dict['indep_axis_units'].strip()
        )
        indep_axis_unit_scale = (
            ''
            if indep_axis_dict['indep_axis_unit_scale'] is None or
               not print_indep_axis else
            indep_axis_dict['indep_axis_unit_scale'].strip()
        )
        self._setup_axis(
            'INDEP',
            axarr_prim,
            indep_var_min,
            indep_var_max,
            indep_var_locs,
            indep_var_labels,
            indep_axis_label,
            indep_axis_units,
            indep_axis_unit_scale
        )
        plt.setp(axarr_prim.get_xticklabels(), visible=print_indep_axis)
        return {
            'primary':(
                None
                if not self._panel_has_primary_axis else
                axarr_prim
            ),
            'secondary':(
                None
                if not self._panel_has_secondary_axis else
                axarr_sec
            )
        }

    _complete = property(_get_complete)

    display_indep_axis = property(
        _get_display_indep_axis,
        _set_display_indep_axis,
        doc='Show independent axis flag'
    )
    r"""
    Gets or sets the independent axis display flag; indicates whether the
    independent axis is displayed (True) or not (False)

    :type: boolean

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.plot.panel.Panel.display_indep_axis

    :raises: (when assigned) RuntimeError (Argument \`display_indep_axis\`
     is not valid)

    .. [[[end]]]
    """

    legend_props = property(
        _get_legend_props, _set_legend_props, doc='Panel legend box properties'
    )
    r"""
    Gets or sets the panel legend box properties; this is a dictionary that
    has properties (dictionary key) and their associated values (dictionary
    values). Currently supported properties are:

    * **pos** (*string*) -- legend box position, one of :code:`'BEST'`,
      :code:`'UPPER RIGHT'`, :code:`'UPPER LEFT'`, :code:`'LOWER LEFT'`,
      :code:`'LOWER RIGHT'`, :code:`'RIGHT'`, :code:`'CENTER LEFT'`,
      :code:`'CENTER RIGHT'`, :code:`'LOWER CENTER'`, :code:`'UPPER CENTER'`
      or :code:`'CENTER'` (case insensitive)

    * **cols** (integer) -- number of columns of the legend box

    If :code:`None` the default used is :code:`{'pos':'BEST', 'cols':1}`

    .. note:: No legend is shown if a panel has only one series in it or if no
              series has a label

    :type: dictionary

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.plot.panel.Panel.legend_props

    :raises: (when assigned)

     * RuntimeError (Argument \`legend_props\` is not valid)

     * RuntimeError (Legend property \`cols\` is not valid)

     * TypeError (Legend property \`pos\` is not one of ['BEST', 'UPPER
       RIGHT', 'UPPER LEFT', 'LOWER LEFT', 'LOWER RIGHT', 'RIGHT', 'CENTER
       LEFT', 'CENTER RIGHT', 'LOWER CENTER', 'UPPER CENTER', 'CENTER']
       (case insensitive))

     * ValueError (Illegal legend property \`*[prop_name]*\`)

    .. [[[end]]]
    """

    log_dep_axis = property(
        _get_log_dep_axis,
        _set_log_dep_axis,
        doc='Panel logarithmic dependent axis flag'
    )
    r"""
    Gets or sets the panel logarithmic dependent (primary and/or secondary)
    axis flag; indicates whether the dependent (primary and/or secondary) axis
    is linear (False) or logarithmic (True)

    :type: boolean

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.plot.panel.Panel.log_dep_axis

    :raises: (when assigned)

     * RuntimeError (Argument \`log_dep_axis\` is not valid)

     * RuntimeError (Argument \`series\` is not valid)

     * RuntimeError (Series item *[number]* is not fully specified)

     * ValueError (Series item *[number]* cannot be plotted in a
       logarithmic axis because it contains negative data points)

    .. [[[end]]]
    """

    primary_axis_label = property(
        _get_primary_axis_label,
        _set_primary_axis_label,
        doc='Panel primary axis label'
    )
    r"""
    Gets or sets the panel primary dependent axis label

    :type: string

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.plot.panel.Panel.primary_axis_label

    :raises: (when assigned) RuntimeError (Argument \`primary_axis_label\`
     is not valid)

    .. [[[end]]]
    """

    primary_axis_scale = property(
        _get_primary_axis_scale, doc='Primary axis scale'
    )
    """
    Gets the scale of the panel primary axis, :code:`None` if axis has no
    series associated with it

    :type: float or None
    """

    primary_axis_ticks = property(
        _get_primary_axis_ticks, doc='Primary axis tick locations'
    )
    """
    Gets the primary axis (scaled) tick locations, :code:`None` if axis has no
    series associated with it

    :type: list or None
    """

    primary_axis_units = property(
        _get_primary_axis_units,
        _set_primary_axis_units,
        doc='Panel primary axis units'
    )
    r"""
    Gets or sets the panel primary dependent axis units

    :type: string

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.plot.panel.Panel.primary_axis_units

    :raises: (when assigned) RuntimeError (Argument \`primary_axis_units\`
     is not valid)

    .. [[[end]]]
    """

    secondary_axis_label = property(
        _get_secondary_axis_label,
        _set_secondary_axis_label,
        doc='Panel secondary axis label'
    )
    r"""
    Gets or sets the panel secondary dependent axis label

    :type: string

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.plot.panel.Panel.secondary_axis_label

    :raises: (when assigned) RuntimeError (Argument
     \`secondary_axis_label\` is not valid)

    .. [[[end]]]
    """

    secondary_axis_scale = property(
        _get_secondary_axis_scale,
        doc='Secondary axis scale'
    )
    """
    Gets the scale of the panel secondary axis, :code:`None` if axis has no
    series associated with it

    :type: float or None
    """

    secondary_axis_ticks = property(
        _get_secondary_axis_ticks, doc='secondary axis tick locations'
    )
    """
    Gets the secondary axis (scaled) tick locations, :code:`None` if axis has
    no series associated with it


    :type:  list or None
     with it
    """

    secondary_axis_units = property(
        _get_secondary_axis_units,
        _set_secondary_axis_units,
        doc='Panel secondary axis units'
    )
    r"""
    Gets or sets the panel secondary dependent axis units

    :type: string

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.plot.panel.Panel.secondary_axis_units

    :raises: (when assigned) RuntimeError (Argument
     \`secondary_axis_units\` is not valid)

    .. [[[end]]]
    """

    series = property(_get_series, _set_series, doc='Panel series')
    r"""
    Gets or sets the panel series, :code:`None` if there are no series
    associated with the panel

    :type: :py:class:`putil.plot.Series`, list of
           :py:class:`putil.plot.Series` or None

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.plot.panel.Panel.series

    :raises: (when assigned)

     * RuntimeError (Argument \`series\` is not valid)

     * RuntimeError (Series item *[number]* is not fully specified)

     * ValueError (Series item *[number]* cannot be plotted in a
       logarithmic axis because it contains negative data points)

    .. [[[end]]]
    """
