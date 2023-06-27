# series.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0302,E0102,E0611,W0105

# PyPI imports
import numpy
import matplotlib.path
import matplotlib.pyplot as plt
from scipy.stats import linregress
from scipy.interpolate import InterpolatedUnivariateSpline
# Putil imports
import putil.misc
import putil.pcontracts
from .functions import _C
from .constants import LEGEND_SCALE, LINE_WIDTH, MARKER_SIZE


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
import trace_ex_plot_series
exobj_plot = trace_ex_plot_series.trace_module(no_print=True)
]]]
[[[end]]]
"""


###
# Class
###
class Series(object):
    r"""
    Specifies a series within a panel

    :param data_source: Data source object
    :type  data_source: :py:class:`putil.plot.BasicSource`,
                        :py:class:`putil.plot.CsvSource` *or others
                        conforming to the data source specification*

    :param label: Series label, to be used in the panel legend
    :type  label: string

    :param color: Series color. All `Matplotlib colors
                  <http://matplotlib.org/api/colors_api.html>`_
                  are supported
    :type  color: polymorphic

    :param marker: Marker type. All `Matplotlib marker types
                   <http://matplotlib.org/api/markers_api.html>`_
                   are supported. None indicates no marker
    :type  marker: string or None

    :param interp: Interpolation option (case insensitive), one of None (no
                   interpolation) 'STRAIGHT' (straight line connects data
                   points), 'STEP' (horizontal segments between data points),
                   'CUBIC' (cubic interpolation between data points) or
                   'LINREG' (linear regression based on data points). The
                   interpolation option is case insensitive
    :type  interp: :ref:`InterpolationOption` *or None*

    :param line_style: Line style. All `Matplotlib line styles
                       <http://matplotlib.org/api/artist_api.html#
                       matplotlib.lines.Line2D.set_linestyle>`_ are supported.
                       None indicates no line
    :type  line_style: :ref:`LineStyleOption` *or None*

    :param secondary_axis: Flag that indicates whether the series belongs to
                           the panel primary axis (False) or secondary axis
                           (True)
    :type  secondary_axis: boolean

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.plot.series.Series.__init__

    :raises:
     * RuntimeError (Argument \`color\` is not valid)

     * RuntimeError (Argument \`data_source\` does not have an \`dep_var\`
       attribute)

     * RuntimeError (Argument \`data_source\` does not have an
       \`indep_var\` attribute)

     * RuntimeError (Argument \`data_source\` is not fully specified)

     * RuntimeError (Argument \`interp\` is not valid)

     * RuntimeError (Argument \`label\` is not valid)

     * RuntimeError (Argument \`line_style\` is not valid)

     * RuntimeError (Argument \`marker\` is not valid)

     * RuntimeError (Argument \`secondary_axis\` is not valid)

     * TypeError (Invalid color specification)

     * ValueError (Argument \`interp\` is not one of ['STRAIGHT', 'STEP',
       'CUBIC', 'LINREG'] (case insensitive))

     * ValueError (Argument \`line_style\` is not one of ['-', '--', '-.',
       ':'])

     * ValueError (Arguments \`indep_var\` and \`dep_var\` must have the
       same number of elements)

     * ValueError (At least 4 data points are needed for CUBIC
       interpolation)

    .. [[[end]]]
    """
    # pylint: disable=R0902,R0903,R0913
    def __init__(self, data_source, label, color='k', marker='o',
                 interp='CUBIC', line_style='-', secondary_axis=False):
        # Series plotting attributes
        self._ref_linewidth = LINE_WIDTH
        self._ref_markersize = MARKER_SIZE
        self._ref_markeredgewidth = self._ref_markersize*(5.0/14.0)
        self._ref_markerfacecolor = 'w'
        # Private attributes
        self._scaling_factor_indep_var = 1
        self._scaling_factor_dep_var = 1
        self._marker_spec = None
        self._linestyle_spec = None
        self._linewidth_spec = None
        # Public attributes
        self.scaled_indep_var = None
        self.scaled_dep_var = None
        self.interp_indep_var = None
        self.interp_dep_var = None
        self.indep_var = None
        self.dep_var = None
        self.scaled_interp_indep_var = None
        self.scaled_interp_dep_var = None
        self._data_source = None
        self._label = None
        self._color = 'k'
        self._marker = 'o'
        self._interp = 'CUBIC'
        self._line_style = '-'
        self._secondary_axis = False
        # Assignment of arguments to attributes
        self._set_label(label)
        self._set_color(color)
        self._set_marker(marker)
        self._set_interp(interp)
        self._set_line_style(line_style)
        self._set_secondary_axis(secondary_axis)
        self._set_data_source(data_source)

    def _get_data_source(self):
        return self._data_source

    def _set_data_source(self, data_source):
        # pylint: disable=W0212
        indep_ex = putil.exh.addex(
            RuntimeError,
            'Argument `data_source` does not have an `indep_var` attribute'
        )
        dep_ex = putil.exh.addex(
            RuntimeError,
            'Argument `data_source` does not have an `dep_var` attribute'
        )
        specified_ex = putil.exh.addex(
            RuntimeError, 'Argument `data_source` is not fully specified'
        )
        if data_source is not None:
            indep_ex('indep_var' not in dir(data_source))
            dep_ex('dep_var' not in dir(data_source))
            specified_ex(
                ('_complete' in dir(data_source)) and
                (not data_source._complete)
            )
            self._data_source = data_source
            self.indep_var = self.data_source.indep_var
            self.dep_var = self.data_source.dep_var
            self._validate_source_length_cubic_interp()
            self._calculate_curve()

    def _get_label(self):
        return self._label

    @putil.pcontracts.contract(label='None|str')
    def _set_label(self, label):
        self._label = label

    def _get_color(self):
        return self._color

    @putil.pcontracts.contract(color='real_num|str|list|tuple')
    def _set_color(self, color):
        invalid_ex = putil.exh.addex(
            TypeError, 'Invalid color specification'
        )
        valid_html_colors = [
            'aliceblue', 'antiquewhite', 'aqua', 'aquamarine', 'azure',
            'beige', 'bisque', 'black', 'blanchedalmond', 'blue', 'blueviolet',
            'brown', 'burlywood', 'cadetblue', 'chartreuse', 'chocolate',
            'coral', 'cornflowerblue', 'cornsilk', 'crimson', 'cyan',
            'darkblue', 'darkcyan', 'darkgoldenrod', 'darkgray', 'darkgreen',
            'darkkhaki', 'darkmagenta', 'darkolivegreen', 'darkorange',
            'darkorchid', 'darkred', 'darksalmon', 'darkseagreen',
            'darkslateblue', 'darkslategray', 'darkturquoise', 'darkviolet',
            'deeppink', 'deepskyblue', 'dimgray', 'dodgerblue', 'firebrick',
            'floralwhite', 'forestgreen', 'fuchsia', 'gainsboro', 'ghostwhite',
            'gold', 'goldenrod', 'gray', 'green', 'greenyellow', 'honeydew',
            'hotpink', 'indianred', 'indigo', 'ivory', 'khaki', 'lavender',
            'lavenderblush', 'lawngreen', 'lemonchiffon', 'lightblue',
            'lightcoral', 'lightcyan', 'lightgoldenrodyellow', 'lightgreen',
            'lightgrey', 'lightpink', 'lightsalmon', 'lightseagreen',
            'lightskyblue', 'lightslategray', 'lightsteelblue', 'lightyellow',
            'lime', 'limegreen', 'linen', 'magenta', 'maroon',
            'mediumaquamarine', 'mediumblue', 'mediumorchid', 'mediumpurple',
            'mediumseagreen', 'mediumslateblue', 'mediumspringgreen',
            'mediumturquoise', 'mediumvioletred', 'midnightblue', 'mintcream',
            'mistyrose', 'moccasin', 'navajowhite', 'navy', 'oldlace', 'olive',
            'olivedrab', 'orange', 'orangered', 'orchid', 'palegoldenrod',
            'palegreen', 'paleturquoise', 'palevioletred', 'papayawhip',
            'peachpuff', 'peru', 'pink', 'plum', 'powderblue', 'purple', 'red',
            'rosybrown', 'royalblue', 'saddlebrown', 'salmon', 'sandybrown',
            'seagreen', 'seashell', 'sienna', 'silver', 'skyblue', 'slateblue',
            'slategray', 'snow', 'springgreen', 'steelblue', 'tan', 'teal',
            'thistle', 'tomato', 'turquois', 'violet', 'wheat', 'white',
            'whitesmoke', 'yellow', 'yellowgreen'
        ]
        self._color = (
            color.lower().strip()
            if isinstance(color, str) else
            (float(color) if putil.misc.isreal(color) else color)
        )
        check_list = list()
        # No color specification
        check_list.append(self.color is None)
        # Gray scale color specification, checked by decorator
        check_list.append(
            putil.misc.isreal(self.color) and (0.0 <= color <= 1.0)
        )
        # Basic built-in Matplotlib specification
        check_list.append(
            isinstance(self.color, str) and
            (len(self.color) == 1) and
            (self.color in 'bgrcmykw')
        )
        # HTML color name specification
        check_list.append(
            isinstance(self.color, str) and (self.color in valid_html_colors)
        )
        # HTML hex color specification
        check_list.append(
            isinstance(self.color, str) and
            (self.color[0] == '#') and
            (len(self.color) == 7) and
            ((numpy.array([putil.misc.ishex(char)
                  for char in self.color[1:]]
                 ) == numpy.array([True]*6)).all())
        )
        # RGB or RGBA tuple
        check_list.append(
            (isinstance(self.color, list) or isinstance(self.color, tuple)) and
            (len(self.color) in [3, 4]) and
            ((numpy.array([
                putil.misc.isreal(comp) and (0.0 <= comp <= 1.0)
                for comp in self.color
            ]) == numpy.array([True]*len(self.color))).all())
        )
        invalid_ex(True not in check_list)

    def _get_marker(self):
        return self._marker

    def _set_marker(self, marker):
        putil.exh.addai('marker', not self._validate_marker(marker))
        self._marker = marker
        self._marker_spec = (
            self.marker if self.marker not in ["None", None, ' ', ''] else ''
        )

    def _get_interp(self):
        return self._interp

    @putil.pcontracts.contract(interp='interpolation_option')
    def _set_interp(self, interp):
        self._interp = (
            interp.upper().strip() if isinstance(interp, str) else interp
        )
        self._validate_source_length_cubic_interp()
        self._update_linestyle_spec()
        self._update_linewidth_spec()
        self._calculate_curve()

    def _get_line_style(self):
        return self._line_style

    @putil.pcontracts.contract(line_style='line_style_option')
    def _set_line_style(self, line_style):
        self._line_style = line_style
        self._update_linestyle_spec()
        self._update_linewidth_spec()

    def _get_secondary_axis(self):
        return self._secondary_axis

    @putil.pcontracts.contract(secondary_axis='None|bool')
    def _set_secondary_axis(self, secondary_axis):
        self._secondary_axis = secondary_axis

    def __str__(self):
        """ Print series object information """
        ret = ''
        ret += 'Independent variable: {0}\n'.format(
            putil.eng.pprint_vector(self.indep_var, width=50)
        )
        ret += 'Dependent variable: {0}\n'.format(
            putil.eng.pprint_vector(self.dep_var, width=50)
        )
        ret += 'Label: {0}\n'.format(self.label)
        ret += 'Color: {0}\n'.format(self.color)
        ret += 'Marker: {0}\n'.format(self._print_marker())
        ret += 'Interpolation: {0}\n'.format(self.interp)
        ret += 'Line style: {0}\n'.format(self.line_style)
        ret += 'Secondary axis: {0}'.format(self.secondary_axis)
        return ret

    def _check_series_is_plottable(self):
        """
        Check that the combination of marker, line style and line width width
        will produce a printable series
        """
        return (
            not (((self._marker_spec == '') and
            ((not self.interp) or
            (not self.line_style))) or
            (self.color in [None, '']))
        )

    def _validate_source_length_cubic_interp(self):
        """
        Test if data source has minimum length to calculate cubic interpolation
        """
        # pylint: disable=C0103
        putil.exh.addex(
            ValueError,
            'At least 4 data points are needed for CUBIC interpolation',
            (self.interp == 'CUBIC') and (self.indep_var is not None) and
            (self.dep_var is not None) and (self.indep_var.shape[0] < 4)
        )

    def _validate_marker(self, marker):
        """ Validate if marker specification is valid """
        # pylint: disable=R0201
        try:
            plt.plot(range(10), marker=marker)
        except ValueError:
            return False
        except: # pragma: no cover
            raise
        return True

    def _print_marker(self):
        """ Returns marker description """
        marker_consts = [
            {
                'value':matplotlib.markers.TICKLEFT,
                'repr':'matplotlib.markers.TICKLEFT'
            },
            {
                'value':matplotlib.markers.TICKRIGHT,
                'repr':'matplotlib.markers.TICKRIGHT'
            },
            {
                'value':matplotlib.markers.TICKUP,
                'repr':'matplotlib.markers.TICKUP'
            },
            {
                'value':matplotlib.markers.TICKDOWN,
                'repr':'matplotlib.markers.TICKDOWN'
            },
            {
                'value':matplotlib.markers.CARETLEFT,
                'repr':'matplotlib.markers.CARETLEFT'
            },
            {
                'value':matplotlib.markers.CARETRIGHT,
                'repr':'matplotlib.markers.CARETRIGHT'
            },
            {
                'value':matplotlib.markers.CARETUP,
                'repr':'matplotlib.markers.CARETUP'
            },
            {
                'value':matplotlib.markers.CARETDOWN,
                'repr':'matplotlib.markers.CARETDOWN'
            }
        ]
        marker_none = ["None", None, ' ', '']
        if self.marker in marker_none:
            return 'None'
        for const_dict in marker_consts:
            if self.marker == const_dict['value']:
                return const_dict['repr']
        if isinstance(self.marker, str):
            return self.marker
        if isinstance(self.marker, matplotlib.path.Path):
            return 'matplotlib.path.Path object'
        return str(self.marker)

    def _get_complete(self):
        """
        Returns True if series is fully specified, otherwise returns False
        """
        return self.data_source is not None

    def _calculate_curve(self):
        """ Compute curve to interpolate between data points """
        # pylint: disable=E1101,W0612
        if _C(self.interp, self.indep_var, self.dep_var):
            if self.interp == 'CUBIC':
                # Add 20 points between existing points
                self.interp_indep_var = numpy.array([])
                iobj = zip(self.indep_var[:-1], self.indep_var[1:])
                for start, stop in iobj:
                    self.interp_indep_var = numpy.concatenate(
                        (
                            self.interp_indep_var,
                            numpy.linspace(start, stop, 20, endpoint=False)
                        )
                    )
                self.interp_indep_var = numpy.concatenate(
                    (self.interp_indep_var, [self.indep_var[-1]])
                )
                spl = InterpolatedUnivariateSpline(
                    self.indep_var, self.dep_var
                )
                self.interp_dep_var = spl(self.interp_indep_var)
            elif self.interp == 'LINREG':
                slope, intercept, _, _, _ = linregress(
                    self.indep_var, self.dep_var
                )
                self.interp_indep_var = self.indep_var
                self.interp_dep_var = intercept+(slope*self.indep_var)
        self._scale_indep_var(self._scaling_factor_indep_var)
        self._scale_dep_var(self._scaling_factor_dep_var)

    def _scale_indep_var(self, scaling_factor):
        """ Scale independent variable """
        self._scaling_factor_indep_var = float(scaling_factor)
        self.scaled_indep_var = (
            self.indep_var/self._scaling_factor_indep_var
            if self.indep_var is not None else
            self.scaled_indep_var
        )
        self.scaled_interp_indep_var = (
            self.interp_indep_var/self._scaling_factor_indep_var
            if self.interp_indep_var is not None else
            self.scaled_interp_indep_var
        )

    def _scale_dep_var(self, scaling_factor):
        """ Scale dependent variable """
        self._scaling_factor_dep_var = float(scaling_factor)
        self.scaled_dep_var = (
            self.dep_var/self._scaling_factor_dep_var
            if self.dep_var is not None else
            self.scaled_dep_var
        )
        self.scaled_interp_dep_var = (
            self.interp_dep_var/self._scaling_factor_dep_var
            if self.interp_dep_var is not None else
            self.scaled_interp_dep_var
        )

    def _update_linestyle_spec(self):
        """ Update line style specification to be used in series drawing """
        self._linestyle_spec = (
            self.line_style if _C(self.line_style, self.interp) else ''
        )

    def _update_linewidth_spec(self):
        """ Update line width specification to be used in series drawing """
        self._linewidth_spec = (
            self._ref_linewidth if _C(self.line_style, self.interp) else 0.0
        )

    def _legend_artist(self, legend_scale=None):
        """ Creates artist (marker -if used- and line style -if used-) """
        legend_scale = LEGEND_SCALE if legend_scale is None else legend_scale
        return plt.Line2D(
            (0, 1),
            (0, 0),
            color=self.color,
            marker=self._marker_spec,
            linestyle=self._linestyle_spec,
            linewidth=self._linewidth_spec/legend_scale,
            markeredgecolor=self.color,
            markersize=self._ref_markersize/legend_scale,
            markeredgewidth=self._ref_markeredgewidth/legend_scale,
            markerfacecolor=self._ref_markerfacecolor
        )

    def _draw_series(self, axarr, log_indep, log_dep):
        """ Draw series """
        if self._check_series_is_plottable():
            flist = [axarr.plot, axarr.semilogx, axarr.semilogy, axarr.loglog]
            fplot = flist[2*log_dep+log_indep]
            # Plot line
            if self._linestyle_spec != '':
                fplot(
                    self.scaled_indep_var
                    if self.interp in ['STRAIGHT', 'STEP'] else
                    self.scaled_interp_indep_var,
                    self.scaled_dep_var
                    if self.interp in ['STRAIGHT', 'STEP'] else
                    self.scaled_interp_dep_var,
                    color=self.color,
                    linestyle=self.line_style,
                    linewidth=self._ref_linewidth,
                    drawstyle=(
                        'steps-post' if self.interp == 'STEP' else 'default'
                    ),
                    label=self.label
                )
            # Plot markers
            if self._marker_spec != '':
                fplot(
                    self.scaled_indep_var,
                    self.scaled_dep_var,
                    color=self.color,
                    linestyle='',
                    linewidth=0,
                    drawstyle=(
                        'steps-post' if self.interp == 'STEP' else 'default'
                    ),
                    marker=self._marker_spec,
                    markeredgecolor=self.color,
                    markersize=self._ref_markersize,
                    markeredgewidth=self._ref_markeredgewidth,
                    markerfacecolor=self._ref_markerfacecolor,
                    label=self.label if self.line_style is None else None
                )

    # Managed attributes
    _complete = property(_get_complete)

    color = property(
        _get_color, _set_color, doc='Series line and marker color'
    )
    r"""
    Gets or sets the series line and marker color. All `Matplotlib colors
    <http://matplotlib.org/api/colors_api.html>`_ are supported

    :type: polymorphic

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.plot.series.Series.color

    :raises: (when assigned)

     * RuntimeError (Argument \`color\` is not valid)

     * TypeError (Invalid color specification)

    .. [[[end]]]
    """

    data_source = property(
        _get_data_source, _set_data_source, doc='Data source'
    )
    r"""
    Gets or sets the data source object. The independent and dependent data
    sets are obtained once this attribute is set. To be valid, a data source
    object must have an ``indep_var`` attribute that contains a Numpy vector of
    increasing real numbers and a ``dep_var`` attribute that contains a Numpy
    vector of real numbers

    :type:  :py:class:`putil.plot.BasicSource`,
     :py:class:`putil.plot.CsvSource` or others conforming to the
     data source specification

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.plot.series.Series.data_source

    :raises: (when assigned)

     * RuntimeError (Argument \`data_source\` does not have an \`dep_var\`
       attribute)

     * RuntimeError (Argument \`data_source\` does not have an
       \`indep_var\` attribute)

     * RuntimeError (Argument \`data_source\` is not fully specified)

     * ValueError (Arguments \`indep_var\` and \`dep_var\` must have the
       same number of elements)

     * ValueError (At least 4 data points are needed for CUBIC
       interpolation)

    .. [[[end]]]
    """
    interp = property(
        _get_interp,
        _set_interp,
        doc='Series interpolation option, one of `STRAIGHT`, '
            '`CUBIC` or `LINREG` (case insensitive)'
    )
    r"""
    Gets or sets the interpolation option, one of :code:`None`
    (no interpolation) :code:`'STRAIGHT'` (straight line connects data points),
    :code:`'STEP'` (horizontal segments between data points), :code:`'CUBIC'`
    (cubic interpolation between data points) or :code:`'LINREG'` (linear
    regression based on data points). The interpolation option is case
    insensitive

    :type:  :ref:`InterpolationOption` or None

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.plot.series.Series.interp

    :raises: (when assigned)

     * RuntimeError (Argument \`interp\` is not valid)

     * ValueError (Argument \`interp\` is not one of ['STRAIGHT', 'STEP',
       'CUBIC', 'LINREG'] (case insensitive))

     * ValueError (At least 4 data points are needed for CUBIC
       interpolation)

    .. [[[end]]]
    """

    label = property(_get_label, _set_label, doc='Series label')
    r"""
    Gets or sets the series label, to be used in the panel legend if the panel
    has more than one series

    :type:  string

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.plot.series.Series.label

    :raises: (when assigned) RuntimeError (Argument \`label\` is not
     valid)

    .. [[[end]]]
    """

    line_style = property(
        _get_line_style,
        _set_line_style,
        doc='Series line style, one of `-`, `--`, `-.` or `:`'
    )
    r"""
    Sets or gets the line style. All `Matplotlib line styles
    <http://matplotlib.org/api/artist_api.html#matplotlib.lines.
    Line2D.set_linestyle>`_ are supported. :code:`None` indicates no line

    :type:  :ref:`LineStyleOption`

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.plot.series.Series.line_style

    :raises: (when assigned)

     * RuntimeError (Argument \`line_style\` is not valid)

     * ValueError (Argument \`line_style\` is not one of ['-', '--', '-.',
       ':'])

    .. [[[end]]]
    """

    marker = property(
        _get_marker, _set_marker, doc='Plot data point markers flag'
    )
    r"""
    Gets or sets the series marker type. All `Matplotlib marker types
    <http://matplotlib.org/api/markers_api.html>`_ are supported.
    :code:`None` indicates no marker

    :type: string or None

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.plot.series.Series.marker

    :raises: (when assigned) RuntimeError (Argument \`marker\` is not
     valid)

    .. [[[end]]]
    """

    secondary_axis = property(
        _get_secondary_axis,
        _set_secondary_axis,
        doc='Series secondary axis flag'
    )
    r"""
    Sets or gets the secondary axis flag; indicates whether the series belongs
    to the panel primary axis (False) or secondary axis (True)

    :type:  boolean

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.plot.series.Series.secondary_axis

    :raises: (when assigned) RuntimeError (Argument \`secondary_axis\` is
     not valid)

    .. [[[end]]]
    """
