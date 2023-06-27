# basic_source.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0302,E1101,E1103,W0105,W0212

# PyPI imports
import numpy
# Putil imports
import putil.exh
import putil.pcontracts
from .constants import PRECISION
from .functions import _C, _SEL, DataSource


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
import trace_ex_plot_basic_source
exobj_plot = trace_ex_plot_basic_source.trace_module(no_print=True)
]]]
[[[end]]]
"""


###
# Class
###
class BasicSource(DataSource):
    r"""
    Objects of this class hold a given data set intended for plotting. It is a
    convenient way to plot manually-entered data or data coming from
    a source that does not export to a comma-separated values (CSV) file.

    :param indep_var: Independent variable vector
    :type  indep_var: :ref:`IncreasingRealNumpyVector`

    :param dep_var: Dependent variable vector
    :type  dep_var: :ref:`RealNumpyVector`

    :param indep_min: Minimum independent variable value. If None no minimum
                      thresholding is applied to the data
    :type  indep_min: :ref:`RealNum` *or None*

    :param indep_max: Maximum independent variable value. If None no maximum
                      thresholding is applied to the data
    :type  indep_max: :ref:`RealNum` *or None*

    :rtype: :py:class:`putil.plot.BasicSource`

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc())]]]
    .. Auto-generated exceptions documentation for
    .. putil.plot.basic_source.BasicSource.__init__

    :raises:
     * RuntimeError (Argument \`dep_var\` is not valid)

     * RuntimeError (Argument \`indep_max\` is not valid)

     * RuntimeError (Argument \`indep_min\` is not valid)

     * RuntimeError (Argument \`indep_var\` is not valid)

     * ValueError (Argument \`indep_min\` is greater than argument
       \`indep_max\`)

     * ValueError (Argument \`indep_var\` is empty after
       \`indep_min\`/\`indep_max\` range bounding)

     * ValueError (Arguments \`indep_var\` and \`dep_var\` must have the
       same number of elements)

    .. [[[end]]]
    """
    # pylint: disable=R0902,R0903
    def __init__(self, indep_var, dep_var, indep_min=None, indep_max=None):
        # Private attributes
        super(BasicSource, self).__init__()
        self._exh = putil.exh.get_or_create_exh_obj()
        self._raw_indep_var = None
        self._raw_dep_var = None
        self._indep_var_indexes = None
        self._min_indep_var_index = None
        self._max_indep_var_index = None
        # Public attributes
        self._indep_min = None
        self._indep_max = None
        # Assignment of arguments to attributes
        # Assign minimum and maximum first so as not to trigger unnecessary
        # thresholding if the dependent and independent variables are
        # already assigned
        self._set_indep_min(indep_min)
        self._set_indep_max(indep_max)
        self._set_indep_var(indep_var)
        self._set_dep_var(dep_var)

    def __str__(self):
        """
        Prints source information. For example:

        .. =[=cog
        .. import docs.support.incfile
        .. docs.support.incfile.incfile('plot_example_4.py', cog.out)
        .. =]=
        .. code-block:: python

            # plot_example_4.py
            import numpy, putil.plot

            def create_basic_source():
                obj = putil.plot.BasicSource(
                    indep_var=numpy.array([1, 2, 3, 4]),
                    dep_var=numpy.array([1, -10, 10, 5]),
                    indep_min=2, indep_max=3
                )
                return obj

        .. =[=end=]=

        .. code-block:: python

            >>> from __future__ import print_function
            >>> import docs.support.plot_example_4
            >>> obj = docs.support.plot_example_4.create_basic_source()
            >>> print(obj)
            Independent variable minimum: 2
            Independent variable maximum: 3
            Independent variable: [ 2.0, 3.0 ]
            Dependent variable: [ -10.0, 10.0 ]
        """
        ret = ''
        ret += 'Independent variable minimum: {0}\n'.format(
            '-inf' if self.indep_min is None else self.indep_min
        )
        ret += 'Independent variable maximum: {0}\n'.format(
            '+inf' if self.indep_max is None else self.indep_max
        )
        ret += super(BasicSource, self).__str__()
        return ret

    def _get_indep_max(self):
        return self._indep_max

    def _get_indep_min(self):
        return self._indep_min

    @putil.pcontracts.contract(dep_var='real_numpy_vector')
    def _set_dep_var(self, dep_var):
        putil.exh.addex(
            ValueError,
            'Arguments `indep_var` and `dep_var` must have'
            ' the same number of elements',
            _C(dep_var, self._raw_indep_var) and
            (self._raw_indep_var.size != dep_var.size)
        )
        self._raw_dep_var = putil.eng.round_mantissa(dep_var, PRECISION)
        self._update_dep_var()

    @putil.pcontracts.contract(indep_max='real_num')
    def _set_indep_max(self, indep_max):
        putil.exh.addex(
            ValueError,
            'Argument `indep_min` is greater than argument `indep_max`',
            _C(self.indep_min, indep_max) and (indep_max < self.indep_min)
        )
        self._indep_max = (
            putil.eng.round_mantissa(indep_max, PRECISION)
            if not isinstance(indep_max, int) else
            indep_max
        )
        # Apply minimum and maximum range bounding and assign it
        # to self._indep_var and thus this is what self.indep_var returns
        self._update_indep_var()
        self._update_dep_var()

    @putil.pcontracts.contract(indep_min='real_num')
    def _set_indep_min(self, indep_min):
        putil.exh.addex(
            ValueError,
            'Argument `indep_min` is greater than argument `indep_max`',
            _C(self.indep_max, indep_min) and (self.indep_max < indep_min)
        )
        self._indep_min = (
            putil.eng.round_mantissa(indep_min, PRECISION)
            if not isinstance(indep_min, int) else
            indep_min
        )
        # Apply minimum and maximum range bounding and assign it to
        # self._indep_var and thus this is what self.indep_var returns
        self._update_indep_var()
        self._update_dep_var()

    @putil.pcontracts.contract(indep_var='increasing_real_numpy_vector')
    def _set_indep_var(self, indep_var):
        putil.exh.addex(
            ValueError,
            'Arguments `indep_var` and `dep_var` must have the '
            'same number of elements',
            _C(indep_var, self._raw_dep_var) and
            (self._raw_dep_var.size != indep_var.size)
        )
        self._raw_indep_var = putil.eng.round_mantissa(indep_var, PRECISION)
        # Apply minimum and maximum range bounding and assign it to
        # self._indep_var and thus this is what self.indep_var returns
        self._update_indep_var()
        self._update_dep_var()

    def _update_dep_var(self):
        """
        Update dependent variable (if assigned) to match the independent
        variable range bounding
        """
        self._dep_var = self._raw_dep_var
        if _C(self._indep_var_indexes, self._raw_dep_var):
            super(BasicSource, self)._set_dep_var(
                self._raw_dep_var[self._indep_var_indexes]
            )

    def _update_indep_var(self):
        """
        Update independent variable according to its minimum and maximum limits
        """
        empty_ex = putil.exh.addex(
            ValueError,
            'Argument `indep_var` is empty after `indep_min`/`indep_max`'
            ' range bounding'
        )
        if self._raw_indep_var is not None:
            indep_min = _SEL(self.indep_min, self._raw_indep_var[0])
            indep_max = _SEL(self.indep_max, self._raw_indep_var[-1])
            min_indexes = self._raw_indep_var >= indep_min
            max_indexes = self._raw_indep_var <= indep_max
            self._indep_var_indexes = numpy.where(min_indexes & max_indexes)
            super(BasicSource, self)._set_indep_var(
                self._raw_indep_var[self._indep_var_indexes]
            )
            empty_ex(not self.indep_var.size)

    # Managed attributes
    dep_var = property(
        DataSource._get_dep_var,
        _set_dep_var,
        doc='Dependent variable Numpy vector'
    )
    r"""
    Gets or sets the dependent variable data

    :type: :ref:`RealNumpyVector`

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc())]]]
    .. Auto-generated exceptions documentation for
    .. putil.plot.basic_source.BasicSource.dep_var

    :raises: (when assigned)

     * RuntimeError (Argument \`dep_var\` is not valid)

     * ValueError (Arguments \`indep_var\` and \`dep_var\` must have the
       same number of elements)

    .. [[[end]]]
    """

    indep_max = property(
        _get_indep_max, _set_indep_max, doc='Maximum of independent variable'
    )
    r"""
    Gets or sets the maximum independent variable limit. If :code:`None` no
    maximum thresholding is applied to the data

    :type: :ref:`RealNum` or None

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc())]]]
    .. Auto-generated exceptions documentation for
    .. putil.plot.basic_source.BasicSource.indep_max

    :raises: (when assigned)

     * RuntimeError (Argument \`indep_max\` is not valid)

     * ValueError (Argument \`indep_min\` is greater than argument
       \`indep_max\`)

     * ValueError (Argument \`indep_var\` is empty after
       \`indep_min\`/\`indep_max\` range bounding)

    .. [[[end]]]
    """

    indep_min = property(
        _get_indep_min, _set_indep_min, doc='Minimum of independent variable'
    )
    r"""
    Gets or sets the minimum independent variable limit. If :code:`None` no
    minimum thresholding is applied to the data

    :type: :ref:`RealNum` or None

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc())]]]
    .. Auto-generated exceptions documentation for
    .. putil.plot.basic_source.BasicSource.indep_min

    :raises: (when assigned)

     * RuntimeError (Argument \`indep_min\` is not valid)

     * ValueError (Argument \`indep_min\` is greater than argument
       \`indep_max\`)

     * ValueError (Argument \`indep_var\` is empty after
       \`indep_min\`/\`indep_max\` range bounding)

    .. [[[end]]]
    """

    indep_var = property(
        DataSource._get_indep_var,
        _set_indep_var,
        doc='Independent variable Numpy vector'
    )
    r"""
    Gets or sets the independent variable data

    :type: :ref:`IncreasingRealNumpyVector`

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc())]]]
    .. Auto-generated exceptions documentation for
    .. putil.plot.basic_source.BasicSource.indep_var

    :raises: (when assigned)

     * RuntimeError (Argument \`indep_var\` is not valid)

     * ValueError (Argument \`indep_var\` is empty after
       \`indep_min\`/\`indep_max\` range bounding)

     * ValueError (Arguments \`indep_var\` and \`dep_var\` must have the
       same number of elements)

    .. [[[end]]]
    """
