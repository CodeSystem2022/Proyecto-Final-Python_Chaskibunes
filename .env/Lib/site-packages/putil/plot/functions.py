# functions.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0302,F0401,R0914,W0105,W0212,W0611

# Standard library imports
import abc
import collections
import itertools
import math
import sys
# PyPI imports
import six
import numpy
import matplotlib.pyplot as plt
# Putil imports
import putil.exh
import putil.eng
import putil.misc
import putil.pcontracts
from .constants import PRECISION, MIN_TICKS, SUGGESTED_MAX_TICKS


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
import trace_ex_plot_functions
exobj_plot = trace_ex_plot_functions.trace_module(no_print=True)
]]]
[[[end]]]
"""


###
# Global variables
###
TickProps = collections.namedtuple(
    'TickProps', ['locs', 'labels', 'min', 'max', 'div', 'unit_scale']
)


###
# Functions
###
# all() is not an adequate replacement because if element is zero
# or empty it returns False; also not adequate with Numpy arrays
_C = lambda *x: all([item is not None for item in x])
_F = lambda x, y: dict(field=x, value=y)
_MF = lambda *x: [_F(item1, item2) for item1, item2 in zip(x[::2], x[1::2])]
_SEL = lambda x, y: x if x is not None else y


def _intelligent_ticks(series, series_min, series_max,
    tight=True, log_axis=False, tick_list=None):
    """
    Calculates ticks 'intelligently', trying to calculate sane tick spacing
    """
    # pylint: disable=E1103,R0204,R0912,R0913,R0915
    if tick_list is not None:
        tick_list = numpy.sort(numpy.asarray(tick_list))
    elif len(series) == 1:
        # Handle 1-point series
        series_min = series_max = series[0]
        tick_spacing = putil.eng.round_mantissa(0.1*series[0], PRECISION)
        tick_list = numpy.array(
            [series[0]-tick_spacing, series[0], series[0]+tick_spacing]
        )
        tick_spacing = putil.eng.round_mantissa(0.1*series[0], PRECISION)
        tight = tight_left = tight_right = log_axis = False
    else:
        min_series = min(series)
        max_series = max(series)
        rounded_min_series = putil.eng.round_mantissa(min_series, PRECISION)
        rounded_max_series = putil.eng.round_mantissa(max_series, PRECISION)
        if log_axis:
            dec_start = int(math.log10(min_series))
            dec_stop = int(math.ceil(math.log10(max_series)))
            tick_list = [10**num for num in range(dec_start, dec_stop+1)]
            tight_left = not ((not tight) and (tick_list[0] >= min_series))
            tight_right = not ((not tight) and (tick_list[-1] <= max_series))
            tick_list = numpy.array(tick_list)
        else:
            # Try to find the tick spacing that will have the most number of
            # data points on grid. Otherwise, place max_ticks uniformly
            # distributed across the data rage
            series_delta = putil.eng.round_mantissa(
                max_series-min_series, PRECISION
            )
            working_series = numpy.array(series[:])
            tick_list = list()
            num_ticks = SUGGESTED_MAX_TICKS
            while (num_ticks >= MIN_TICKS) and (len(working_series) > 1):
                # Round mantissa of spacings so as to not confuse greatest
                # common denominator algorithm
                sdiff = numpy.diff(working_series)
                nzero_indexes = numpy.nonzero(sdiff)
                nzero = sdiff[nzero_indexes]
                exp = numpy.power(10, numpy.floor(numpy.log10(nzero)))
                nzero = numpy.round(nzero/exp, PRECISION)*exp
                sdiff[nzero_indexes] = nzero
                # numpy.unique return list is sorted in ascending order
                data_spacing = numpy.unique(nzero)
                # Calculation of greatest common denominator (GCD) is
                # computationally (and time) expensive, only do it when the
                # minimum spacing would generate a number of ticks less than
                # the suggested maximum number of ticks, since the GCD of
                # all the data point spacings is at most as big as the minimum
                # data spacing
                if (series_delta/data_spacing[0])+1 < SUGGESTED_MAX_TICKS:
                    tick_spacing = putil.misc.gcd(data_spacing)
                    num_ticks = (
                        (series_delta/tick_spacing)+1
                        if tick_spacing else
                        MIN_TICKS
                    )
                    if MIN_TICKS <= num_ticks <= SUGGESTED_MAX_TICKS:
                        tick_list = numpy.linspace(
                            rounded_min_series, rounded_max_series, num_ticks
                        ).tolist()
                        break
                # Remove elements that cause minimum spacing, to see if with
                # those elements removed the number of tick marks can be
                # withing the acceptable range
                min_data_spacing = data_spacing[0]
                indexes = numpy.concatenate(
                    ([True], (sdiff != min_data_spacing))
                )
                # Account for fact that if minimum spacing is between last two
                # elements, the last element cannot be removed (it is the end
                # of the range), but rather the next-to-last has to be removed
                if (not indexes[-1]) and (len(working_series) > 2):
                    indexes[-2], indexes[-1] = False, True
                working_series = working_series[indexes]
            tick_list = (
                tick_list
                if len(tick_list) > 0 else
                numpy.linspace(
                    min_series, max_series, SUGGESTED_MAX_TICKS
                ).tolist()
            )
            tick_spacing = putil.eng.round_mantissa(
                tick_list[1]-tick_list[0], PRECISION
            )
            # Account for interpolations, whose curves might have values above
            # or below the data points. Only add an extra tick, otherwise let
            # curve go above/below panel
            tight_left = (
                False
                if (not tight) and (tick_list[0] >= series_min) else
                tight
            )
            tight_right = (
                False
                if (not tight) and (tick_list[-1] <= series_max) else
                tight
            )
            tick_list = numpy.array(
                tick_list
                if tight else
                ([tick_list[0]-tick_spacing] if not tight_left else [])+
                tick_list+
                ([tick_list[-1]+tick_spacing] if not tight_right else [])
            )
    # Scale series with minimum, maximum and delta as reference, pick
    # scaling option that has the most compact representation
    opt_min = _scale_ticks(tick_list, 'MIN')
    opt_max = _scale_ticks(tick_list, 'MAX')
    opt_delta = _scale_ticks(tick_list, 'DELTA')
    opt = (
        opt_min
        if (opt_min['count'] <= opt_max['count']) and
           (opt_min['count'] <= opt_delta['count']) else
        (
            opt_max
            if (opt_max['count'] <= opt_min['count']) and
               (opt_max['count'] <= opt_delta['count']) else
            opt_delta
        )
    )
    # Add extra room in logarithmic axis if Tight is True, but do not
    # label marks (aesthetic decision)
    if log_axis and not tight:
        if not tight_left:
            opt['min'] = putil.eng.round_mantissa(
                0.9*opt['loc'][0], PRECISION
            )
            opt['loc'].insert(0, opt['min'])
            opt['labels'].insert(0, '')
        if not tight_right:
            opt['max'] = putil.eng.round_mantissa(
                1.1*opt['loc'][-1], PRECISION
            )
            opt['loc'].append(opt['max'])
            opt['labels'].append('')
    return TickProps(
        opt['loc'],
        opt['labels'],
        opt['min'],
        opt['max'],
        opt['scale'],
        opt['unit'].replace('u', '$\\mu$')
    )


def _process_ticks(locs, min_lim, max_lim, mant):
    """
    Returns pretty-printed tick locations that are within the given bound
    """
    locs = [float(loc) for loc in locs]
    bounded_locs = [
        loc
        for loc in locs
        if ((loc >= min_lim) or (abs(loc-min_lim) <= 1e-14)) and
           ((loc <= max_lim) or (abs(loc-max_lim) <= 1e-14))
    ]
    raw_labels = [
        putil.eng.peng(float(loc), mant, rjust=False)
        if ((abs(loc) >= 1) or (loc == 0)) else
        str(putil.eng.round_mantissa(loc, mant))
        for loc in bounded_locs
    ]
    return (
        bounded_locs,
        [label.replace('u', '$\\mu$') for label in raw_labels]
    )


def _scale_ticks(tick_list, mode):
    """
    Scale series taking the reference to be the series start, stop or delta
    """
    mode = mode.strip().upper()
    tick_min = tick_list[0]
    tick_max = tick_list[-1]
    tick_delta = tick_max-tick_min
    tick_ref = (
        tick_min
        if mode == 'MIN' else
        (tick_max if mode == 'MAX' else tick_delta)
    )
    (unit, scale) = putil.eng.peng_power(putil.eng.peng(tick_ref, 3))
    # Move one engineering unit back if there are more ticks
    # below 1.0 than above it
    above_1k_sum = sum((tick_list/scale) >= 1000)
    below_1k_sum = sum((tick_list/scale) < 1000)
    last_tick_below_10k = tick_list[-1]/scale < 10000
    rollback = (above_1k_sum > below_1k_sum) and last_tick_below_10k
    scale = 1 if rollback else scale
    unit = putil.eng.peng_suffix_math(unit, +1) if rollback else unit
    tick_list = numpy.array(
        [
            putil.eng.round_mantissa(element/scale, PRECISION)
            for element in tick_list
        ]
    )
    tick_min = putil.eng.round_mantissa(tick_min/scale, PRECISION)
    tick_max = putil.eng.round_mantissa(tick_max/scale, PRECISION)
    loc, labels = _uniquify_tick_labels(tick_list, tick_min, tick_max)
    count = len(''.join(labels))
    return {
        'loc':loc,
        'labels':labels,
        'unit':unit,
        'scale':scale,
        'min':tick_min,
        'max':tick_max,
        'count':count
    }


def _uniquify_tick_labels(tick_list, tmin, tmax):
    """ Calculate minimum tick mantissa given tick spacing """
    # If minimum or maximum has a mantissa, at least preserve one digit
    mant_min = (
        1
        if any([float(item) != float(int(item)) for item in tick_list]) else
        0
    )
    # Step 1: Look at two contiguous ticks and lower mantissa digits till
    # they are no more right zeros
    mant = 10
    for mant in range(10, mant_min-1, -1):
        ldig = str(
            putil.eng.peng_frac(putil.eng.peng(tick_list[-1], mant))
        )[-1]
        nldig = str(
            putil.eng.peng_frac(putil.eng.peng(tick_list[-2], mant))
        )[-1]
        if (ldig != '0') or (nldig != '0'):
            break
    # Step 2: Confirm labels are unique
    #unique_mant_found = False
    while mant >= mant_min:
        loc, labels = _process_ticks(tick_list, tmin, tmax, mant)
        sum1 = sum(
            [
                1 if labels[index] != labels[index+1] else 0
                for index in range(0, len(labels[:-1]))
            ]
        )
        sum2 = sum(
            [
                1 if (putil.eng.peng_float(label) != 0) or
                     ((putil.eng.peng_float(label) == 0) and (num == 0)) else
                0
                for num, label in zip(tick_list, labels)
            ]
        )
        if (sum1 == len(labels)-1) and (sum2 == len(labels)):
            mant -= 1
        else:
            mant += 1
            loc, labels = _process_ticks(tick_list, tmin, tmax, mant)
            break
    return (
        [putil.eng.round_mantissa(element, PRECISION) for element in loc],
        labels
    )


@putil.pcontracts.contract(
    param_list='list(int|float)',
    offset='offset_range',
    color_space='color_space_option'
)
def parameterized_color_space(param_list, offset=0, color_space='binary'):
    r"""
    Computes a color space where lighter colors correspond to lower
    parameter values

    :param param_list: Parameter values
    :type  param_list: list

    :param offset: Offset of the first (lightest) color
    :type  offset: :ref:`OffsetRange`

    :param color_space: Color palette (case sensitive)
    :type  color_space: :ref:`ColorSpaceOption`

    :rtype: `Matplotlib color map <http://matplotlib.org/api/colors_api.html#
            matplotlib.colors.LinearSegmentedColormap>`_

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.plot.functions.parameterized_color_space

    :raises:
     * RuntimeError (Argument \`color_space\` is not valid)

     * RuntimeError (Argument \`offset\` is not valid)

     * RuntimeError (Argument \`param_list\` is not valid)

     * TypeError (Argument \`param_list\` is empty)

     * ValueError (Argument \`color_space\` is not one of 'binary',
       'Blues', 'BuGn', 'BuPu', 'GnBu', 'Greens', 'Greys', 'Oranges',
       'OrRd', 'PuBu', 'PuBuGn', 'PuRd', 'Purples', 'RdPu', 'Reds', 'YlGn',
       'YlGnBu', 'YlOrBr' or 'YlOrRd' (case insensitive))

    .. [[[end]]]
    """
    # pylint: disable=E1101
    color_space_name_list = [
        'binary', 'Blues', 'BuGn', 'BuPu', 'GnBu', 'Greens', 'Greys',
        'Oranges', 'OrRd', 'PuBu', 'PuBuGn', 'PuRd', 'Purples', 'RdPu',
        'Reds', 'YlGn', 'YlGnBu', 'YlOrBr', 'YlOrRd'
    ]
    putil.exh.addex(
        TypeError, 'Argument `param_list` is empty', len(param_list) == 0
    )
    color_palette_list = [
        plt.cm.binary, plt.cm.Blues, plt.cm.BuGn, plt.cm.BuPu, plt.cm.GnBu,
        plt.cm.Greens, plt.cm.Greys, plt.cm.Oranges, plt.cm.OrRd, plt.cm.PuBu,
        plt.cm.PuBuGn, plt.cm.PuRd, plt.cm.Purples, plt.cm.RdPu, plt.cm.Reds,
        plt.cm.YlGn, plt.cm.YlGnBu, plt.cm.YlOrBr, plt.cm.YlOrRd
    ]
    color_dict = dict(zip(color_space_name_list, color_palette_list))
    return [
        color_dict[color_space](
            putil.misc.normalize(value, param_list, offset)
        )
        for value in param_list
    ]


def _check_real_numpy_vector(obj):
    if (isinstance(obj, numpy.ndarray) and
       (len(obj.shape) == 1) and (obj.shape[0] > 0) and
       ((obj.dtype.type == numpy.array([0]).dtype.type) or
       (obj.dtype.type == numpy.array([0.0]).dtype.type))):
        return False
    return True


def _check_increasing_real_numpy_vector(obj):
    # pylint: disable=C0103
    if ((not isinstance(obj, numpy.ndarray)) or (isinstance(obj, numpy.ndarray)
       and ((len(obj.shape) > 1) or ((len(obj.shape) == 1) and
       (obj.shape[0] == 0))))):
        return True
    if (((obj.dtype.type == numpy.array([0]).dtype.type) or
       (obj.dtype.type == numpy.array([0.0]).dtype.type)) and
       ((obj.shape[0] == 1) or ((obj.shape[0] > 1) and
       (min(numpy.diff(obj)) > 0)))):
        return False
    return True


###
# Classes
###
@six.add_metaclass(abc.ABCMeta)
class DataSource(object):
    """
    Abstract base class for data sources. The following example is a
    minimal implementation of a data source class:

    .. =[=cog
    .. import docs.support.incfile
    .. docs.support.incfile.incfile('plot_example_2.py', cog.out)
    .. =]=
    .. code-block:: python

        # plot_example_2.py
        import putil.plot

        class MySource(putil.plot.DataSource, object):
            def __init__(self):
                super(MySource, self).__init__()

            def __str__(self):
                return super(MySource, self).__str__()

            def _set_dep_var(self, dep_var):
                super(MySource, self)._set_dep_var(dep_var)

            def _set_indep_var(self, indep_var):
                super(MySource, self)._set_indep_var(indep_var)

            dep_var = property(
                putil.plot.DataSource._get_dep_var, _set_dep_var
            )

            indep_var = property(
                putil.plot.DataSource._get_indep_var, _set_indep_var
            )

    .. =[=end=]=

    .. warning:: The abstract methods listed below need to be defined
                 in a child class

    """
    # pylint: disable=E0012,R0903,R0921
    def __init__(self):
        self._dep_var, self._indep_var = None, None

    def _get_dep_var(self):
        return self._dep_var

    def _get_indep_var(self):
        return self._indep_var

    @abc.abstractmethod
    def __str__(self):
        """
        Pretty prints the stored independent and dependent variables.
        For example:

        .. code-block:: python

            >>> from __future__ import print_function
            >>> import numpy, docs.support.plot_example_2
            >>> obj = docs.support.plot_example_2.MySource()
            >>> obj.indep_var = numpy.array([1, 2, 3])
            >>> obj.dep_var = numpy.array([-1, 1, -1])
            >>> print(obj)
            Independent variable: [ 1.0, 2.0, 3.0 ]
            Dependent variable: [ -1.0, 1.0, -1.0 ]
        """
        ret = ''
        ret += 'Independent variable: {0}\n'.format(
            putil.eng.pprint_vector(
                self.indep_var,
                width=50,
                indent=len('Independent variable: ')
            )
        )
        ret += 'Dependent variable: {0}'.format(
            putil.eng.pprint_vector(
                self.dep_var,
                width=50,
                indent=len('Dependent variable: ')
            )
        )
        return ret

    @abc.abstractmethod
    def _set_dep_var(self, dep_var):
        """
        Sets the dependent variable (casting to float type). For example:

        .. code-block:: python

            >>> import numpy, docs.support.plot_example_2
            >>> obj = docs.support.plot_example_2.MySource()
            >>> obj.dep_var = numpy.array([-1, 1, -1])
            >>> obj.dep_var
            array([-1.,  1., -1.])
        """
        self._dep_var = dep_var.astype(float)

    @abc.abstractmethod
    def _set_indep_var(self, indep_var):
        """
        Sets the independent variable (casting to float type). For example:

        .. code-block:: python

            >>> import numpy, docs.support.plot_example_2
            >>> obj = docs.support.plot_example_2.MySource()
            >>> obj.indep_var = numpy.array([1, 2, 3])
            >>> obj.indep_var
            array([ 1.,  2.,  3.])
        """
        self._indep_var = indep_var.astype(float)

    def _get_complete(self):
        """
        Returns True if object is fully specified, otherwise returns False
        """
        putil.exh.addex(
            ValueError,
            'Arguments `indep_var` and `dep_var` must have '
            'the same number of elements',
            (self._dep_var is not None) and (self._indep_var is not None) and
            (len(self._dep_var) != len(self._indep_var))
        )
        return (self.indep_var is not None) and (self.dep_var is not None)

    indep_var = abc.abstractproperty(
        _get_indep_var,
        _set_indep_var,
        doc='Independent variable Numpy vector'
    )

    dep_var = abc.abstractproperty(
        _get_dep_var,
        _set_dep_var,
        doc='Dependent variable Numpy vector'
    )

    _complete = property(
        _get_complete,
        doc='Flag that indicates whether the series '
            'is plottable (True) or not (False)'
    )
