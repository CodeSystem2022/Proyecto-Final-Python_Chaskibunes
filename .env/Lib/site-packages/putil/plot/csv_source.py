# csv_source.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0302,E0602,E1101,E1103,W0105,W0212,W0611

# PyPI imports
import numpy
# Putil imports
import putil.exh
from putil.eng import pprint_vector as pprint
from putil.eng import round_mantissa
import putil.pcsv
from putil.ptypes import csv_row_filter
from .constants import PRECISION
from .functions import (
    _C,
    _MF,
    _SEL,
    DataSource,
    _check_increasing_real_numpy_vector,
    _check_real_numpy_vector
)


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
import trace_ex_plot_csv_source
exobj_plot = trace_ex_plot_csv_source.trace_module(no_print=True)
exclude_list = [
    'putil.pcsv.csv_file.CsvFile._set_cfilter',
    'putil.pcsv.csv_file.CsvFile._set_dfilter',
    'putil.pcsv.csv_file.CsvFile._set_has_header',
    'putil.pcsv.csv_file.CsvFile._validate_frow',
    'putil.pcsv.csv_file.CsvFile.data',
    'putil.pcsv.csv_file.CsvFile.header',
    'putil.pcsv.csv_file.CsvFile.cfilter',
    'putil.pcsv.csv_file.CsvFile.dfilter',
    'putil.pcsv.csv_file.CsvFile.reset_dfilter'
]
]]]
[[[end]]]
"""


###
# Class
###
class CsvSource(DataSource):
    r"""
    Objects of this class hold a data set from a CSV file intended for
    plotting. The raw data from the file can be filtered and a callback
    function can be used for more general data pre-processing

    :param fname: Comma-separated values file name
    :type  fname: :ref:`FileNameExists`

    :param indep_col_label: Independent variable column label
                            (case insensitive)
    :type  indep_col_label: string

    :param dep_col_label: Dependent variable column label
                          (case insensitive)
    :type  dep_col_label: string

    :param rfilter: Row filter specification. If None no row filtering is
                    performed
    :type  rfilter: :ref:`CsvRowFilter` *or None*

    :param indep_min: Minimum independent variable value. If None no minimum
                      thresholding is applied to the data
    :type  indep_min: :ref:`RealNum` *or None*

    :param indep_max: Maximum independent variable value. If None no maximum
                      thresholding is applied to the data
    :type  indep_max: :ref:`RealNum` *or None*

    :param fproc: Data processing function. If None no processing function is
                  used
    :type  fproc: :ref:`Function` *or None*

    :param fproc_eargs: Data processing function extra arguments. If None no
                        extra arguments are passed to the processing function
                        (if defined)
    :type  fproc_eargs: dictionary or None

    :rtype: :py:class:`putil.plot.CsvSource`

    .. note:: The row where data starts in the comma-separated file is
              auto-detected as the first row that has a number (integer or
              float) in at least one of its columns

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc(exclude=exclude_list)) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.plot.csv_source.CsvSource.__init__

    :raises:
     * OSError (File *[fname]* could not be found)

     * RuntimeError (Argument \`dep_col_label\` is not valid)

     * RuntimeError (Argument \`dep_var\` is not valid)

     * RuntimeError (Argument \`fname\` is not valid)

     * RuntimeError (Argument \`fproc_eargs\` is not valid)

     * RuntimeError (Argument \`fproc\` (function *[func_name]*) returned
       an illegal number of values)

     * RuntimeError (Argument \`fproc\` is not valid)

     * RuntimeError (Argument \`indep_col_label\` is not valid)

     * RuntimeError (Argument \`indep_max\` is not valid)

     * RuntimeError (Argument \`indep_min\` is not valid)

     * RuntimeError (Argument \`indep_var\` is not valid)

     * RuntimeError (Argument \`rfilter\` is not valid)

     * RuntimeError (Column headers are not unique in file *[fname]*)

     * RuntimeError (File *[fname]* has no valid data)

     * RuntimeError (File *[fname]* is empty)

     * RuntimeError (Processing function *[func_name]* raised an exception
       when called with the following arguments: ``\n`` indep_var:
       *[indep_var_value]* ``\n`` dep_var: *[dep_var_value]* ``\n``
       fproc_eargs: *[fproc_eargs_value]* ``\n`` Exception error:
       *[exception_error_message]*)

     * TypeError (Argument \`fproc\` (function *[func_name]*) return value
       is not valid)

     * TypeError (Processed dependent variable is not valid)

     * TypeError (Processed independent variable is not valid)

     * ValueError (Argument \`fproc\` (function *[func_name]*) does not
       have at least 2 arguments)

     * ValueError (Argument \`indep_min\` is greater than argument
       \`indep_max\`)

     * ValueError (Argument \`indep_var\` is empty after
       \`indep_min\`/\`indep_max\` range bounding)

     * ValueError (Argument \`rfilter\` is empty)

     * ValueError (Arguments \`indep_var\` and \`dep_var\` must have the
       same number of elements)

     * ValueError (Column *[col_name]* (dependent column label) could not
       be found in comma-separated file *[fname]* header)

     * ValueError (Column *[col_name]* (independent column label) could not
       be found in comma-separated file *[fname]* header)

     * ValueError (Column *[col_name]* in row filter not found in comma-
       separated file *[fname]* header)

     * ValueError (Column *[column_identifier]* not found)

     * ValueError (Extra argument \`*[arg_name]*\` not found in argument
       \`fproc\` (function *[func_name]*) definition)

     * ValueError (Filtered dependent variable is empty)

     * ValueError (Filtered independent variable is empty)

     * ValueError (Processed dependent variable is empty)

     * ValueError (Processed independent and dependent variables are of
       different length)

     * ValueError (Processed independent variable is empty)

    .. [[[end]]]
    """
    # pylint: disable=R0902,R0903,R0913
    def __init__(self, fname, indep_col_label, dep_col_label, rfilter=None,
                 indep_min=None, indep_max=None, fproc=None, fproc_eargs=None):
        # Private attributes
        super(CsvSource, self).__init__()
        self._raw_indep_var = None
        self._raw_dep_var = None
        self._min_indep_var_index = None
        self._max_indep_var_index = None
        self._indep_var_indexes = None
        self._csv_obj = None
        self._reverse_data = False
        # Public attributes
        self._indep_min = None
        self._indep_max = None
        self._fname = None
        self._rfilter = None
        self._indep_col_label = None
        self._dep_col_label = None
        self._fproc = None
        self._fproc_eargs = None
        # Assignment of arguments to attributes.
        self._set_fproc(fproc)
        self._set_fproc_eargs(fproc_eargs)
        self._set_rfilter(rfilter)
        self._set_indep_col_label(indep_col_label)
        self._set_dep_col_label(dep_col_label)
        self._set_indep_min(indep_min)
        self._set_indep_max(indep_max)
        self._set_fname(fname)

    def __str__(self):
        r"""
        Prints source information. For example:

        .. =[=cog
        .. import docs.support.incfile
        .. docs.support.incfile.incfile('plot_example_3.py', cog.out)
        .. =]=
        .. code-block:: python

            # plot_example_3.py
            import putil.misc, putil.pcsv

            def cwrite(fobj, data):
                fobj.write(data)

            def write_csv_file(file_handle):
                cwrite(file_handle, 'Col1,Col2\n')
                cwrite(file_handle, '0E-12,10\n')
                cwrite(file_handle, '1E-12,0\n')
                cwrite(file_handle, '2E-12,20\n')
                cwrite(file_handle, '3E-12,-10\n')
                cwrite(file_handle, '4E-12,30\n')

            # indep_var is a Numpy vector, in this example time,
            # in seconds. dep_var is a Numpy vector
            def proc_func1(indep_var, dep_var):
                # Scale time to pico-seconds
                indep_var = indep_var/1e-12
                # Remove offset
                dep_var = dep_var-dep_var[0]
                return indep_var, dep_var

            def create_csv_source():
                with putil.misc.TmpFile(write_csv_file) as fname:
                    obj = putil.plot.CsvSource(
                        fname=fname,
                        indep_col_label='Col1',
                        dep_col_label='Col2',
                        indep_min=2E-12,
                        fproc=proc_func1
                    )
                return obj

        .. =[=end=]=

        .. code-block:: python

            >>> from __future__ import print_function
            >>> import docs.support.plot_example_3
            >>> obj = docs.support.plot_example_3.create_csv_source()
            >>> print(obj)  #doctest: +ELLIPSIS
            File name: ...
            Row filter: None
            Independent column label: Col1
            Dependent column label: Col2
            Processing function: proc_func1
            Processing function extra arguments: None
            Independent variable minimum: 2e-12
            Independent variable maximum: +inf
            Independent variable: [ 2.0, 3.0, 4.0 ]
            Dependent variable: [ 0.0, -30.0, 10.0 ]
        """
        ret = ''
        ret += 'File name: {0}\n'.format(self.fname)
        ret += 'Row filter: {0}\n'.format(
            self.rfilter if self.rfilter is None else ''
        )
        if self.rfilter is not None:
            for key in sorted(self.rfilter):
                ret += '   {key}: {value}\n'.format(
                    key=key, value=self.rfilter[key]
                )
        ret += 'Independent column label: {0}\n'.format(self.indep_col_label)
        ret += 'Dependent column label: {0}\n'.format(self.dep_col_label)
        ret += 'Processing function: {0}\n'.format(
            getattr(self.fproc, '__name__', 'None')
        )
        ret += 'Processing function extra arguments: {0}\n'.format(
            self.fproc_eargs if self.fproc_eargs is None else ''
        )
        if self.fproc_eargs is not None:
            for key in sorted(self.fproc_eargs):
                ret += '   {key}: {value}\n'.format(
                    key=key, value=self.fproc_eargs[key]
                )
        ret += 'Independent variable minimum: {0}\n'.format(
            _SEL(self.indep_min, '-inf')
        )
        ret += 'Independent variable maximum: {0}\n'.format(
            _SEL(self.indep_max, '+inf')
        )
        ret += super(CsvSource, self).__str__()
        return ret

    def _apply_rfilter(self):
        """ Apply row filters to loaded data """
        self._check_rfilter()
        if _C(self.rfilter, self._csv_obj) and len(self.rfilter):
            self._csv_obj.rfilter = self.rfilter
        elif _C(self._csv_obj):
            self._csv_obj.reset_dfilter()
        self._get_indep_var_from_file()
        self._get_dep_var_from_file()

    def _check_dep_col_label(self):
        """
        Check that dependent column label can be found in
        comma-separated file header
        """
        putil.exh.addex(
            ValueError,
            'Column *[col_name]* (dependent column label) could not be'
            ' found in comma-separated file *[fname]* header',
            _C(self._csv_obj, self.dep_col_label) and
            (self.dep_col_label not in self._csv_obj.header()),
            _MF('col_name', self.dep_col_label, 'fname', self.fname)
        )

    def _check_rfilter(self):
        """
        Check that columns in filter specification can be found in
        comma-separated file header
        """
        rfilter_ex = putil.exh.addex(
            ValueError,
            'Column *[col_name]* in row filter not found '
            'in comma-separated file *[fname]* header'
        )
        if _C(self._csv_obj, self.rfilter):
            for key in self.rfilter:
                rfilter_ex(
                    key not in self._csv_obj.header(),
                    _MF('col_name', key, 'fname', self.fname)
                )

    def _check_indep_col_label(self):
        """
        Check that independent column label can be found in
        comma-separated file header
        """
        putil.exh.addex(
            ValueError,
            'Column *[col_name]* (independent column label) could not'
            ' be found in comma-separated file *[fname]* header',
            _C(self._csv_obj, self.indep_col_label) and
            (self.indep_col_label not in self._csv_obj.header()),
            _MF('col_name', self.indep_col_label, 'fname', self.fname)
        )

    def _check_fproc_eargs(self):
        """
        Checks that the extra arguments are in the processing
        function definition
        """
        eargs_ex = putil.exh.addex(
            ValueError,
            'Extra argument `*[arg_name]*` not found in argument '
            '`fproc` (function *[func_name]*) definition',
        )
        if _C(self.fproc, self.fproc_eargs):
            args = putil.pinspect.get_function_args(self._fproc)
            fname = self.fproc.__name__
            for key in self.fproc_eargs:
                eargs_ex(
                    all(
                        [arg not in args for arg in [key, '*args', '**kwargs']]
                    ),
                    _MF('func_name', fname, 'arg_name', key)
                )

    def _get_dep_col_label(self):
        return self._dep_col_label

    def _get_dep_var_from_file(self):
        """
        Retrieve dependent data variable from comma-separated values file
        """
        empty_ex = putil.exh.addex(
            ValueError, 'Filtered dependent variable is empty'
        )
        if _C(self._csv_obj, self.dep_col_label):
            # When object is given all arguments at construction the column
            # label checking cannot happen at property assignment because file
            # data is not yet loaded
            self._check_dep_col_label()
            self._csv_obj.cfilter = self.dep_col_label
            args = dict(filtered=True, no_empty=True)
            data = numpy.array([row[0] for row in self._csv_obj.data(**args)])
            empty_ex(not data.size)
            self._set_dep_var(data[::-1] if self._reverse_data else data)

    def _get_fname(self):
        return self._fname

    def _get_fproc(self):
        return self._fproc

    def _get_fproc_eargs(self):
        return self._fproc_eargs

    def _get_indep_col_label(self):
        return self._indep_col_label

    def _get_indep_max(self):
        return self._indep_max

    def _get_indep_min(self):
        return self._indep_min

    def _get_indep_var_from_file(self):
        """
        Retrieve independent data variable from comma-separated values file
        """
        empty_ex = putil.exh.addex(
            ValueError, 'Filtered independent variable is empty'
        )
        if _C(self._csv_obj, self.indep_col_label):
            # When object is given all arguments at construction the column
            # label checking cannot happen at property assignment because file
            # data is not yet loaded
            self._check_indep_col_label()
            self._csv_obj.cfilter = self.indep_col_label
            args = dict(filtered=True, no_empty=True)
            data = numpy.array([row[0] for row in self._csv_obj.data(**args)])
            empty_ex(not data.size)
            # Flip data if it is in descending order (affects interpolation)
            if max(numpy.diff(data)) < 0:
                self._reverse_data = True
                data = data[::-1]
            self._set_indep_var(data)

    def _get_rfilter(self):
        return self._rfilter

    def _process_data(self):
        """ Process data through call-back function """
        # pylint: disable=R0914,W0110,W0141,W0703
        invalid_ret_ex = putil.exh.addex(
            TypeError,
            'Argument `fproc` (function *[func_name]*) '
            'return value is not valid'
        )
        illegal_ret_ex = putil.exh.addex(
            RuntimeError,
            'Argument `fproc` (function *[func_name]*) '
            'returned an illegal number of values'
        )
        length_ex = putil.exh.addex(
            ValueError,
            'Processed independent and dependent variables '
            'are of different length'
        )
        empty_indep_ex = putil.exh.addex(
            ValueError, 'Processed independent variable is empty'
        )
        illegal_indep_ex = putil.exh.addex(
            TypeError, 'Processed independent variable is not valid'
        )
        empty_dep_ex = putil.exh.addex(
            ValueError, 'Processed dependent variable is empty'
        )
        illegal_dep_ex = putil.exh.addex(
            TypeError, 'Processed dependent variable is not valid'
        )
        proc_fun_ex = putil.exh.addex(
            RuntimeError,
            'Processing function *[func_name]* raised an exception when '
            'called with the following arguments:\n'
            'indep_var: *[indep_var_value]*\n'
            'dep_var: *[dep_var_value]*\n'
            'fproc_eargs: *[fproc_eargs_value]*\n'
            'Exception error: *[exception_error_message]*'
        )
        if not _C(self.fproc, self.indep_var, self.dep_var):
            return
        fproc_eargs = self.fproc_eargs or {}
        try:
            ret = self.fproc(self.indep_var, self.dep_var, **fproc_eargs)
        except Exception as error_msg:
            if fproc_eargs:
                eamsg = '\n'
                template = '   {key}: {value}\n'
                for key, value in self.fproc_eargs.items():
                    eamsg += template.format(key=key, value=value)
            eamsg = eamsg.rstrip() if fproc_eargs else 'None'
            proc_fun_ex(
                True,
                edata=_MF(
                    'func_name', self.fproc.__name__,
                    'indep_var_value', pprint(self.indep_var, limit=10),
                    'dep_var_value', pprint(self.indep_var, limit=10),
                    'fproc_eargs_value', eamsg,
                    'exception_error_message', str(error_msg),
                )
            )
        invalid_ret_ex(
            not (isinstance(ret, list) or isinstance(ret, tuple)),
            _MF('func_name', self.fproc.__name__)
        )
        illegal_ret_ex(len(ret) != 2, _MF('func_name', self.fproc.__name__))
        indep_var = ret[0]
        dep_var = ret[1]
        empty_indep_ex(
            isinstance(indep_var, numpy.ndarray) and
            not list(filter(lambda x: x is not None, indep_var))
        )
        illegal_indep_ex(_check_increasing_real_numpy_vector(indep_var))
        empty_dep_ex(
            isinstance(dep_var, numpy.ndarray) and
            not list(filter(lambda x: x is not None, dep_var))
        )
        illegal_dep_ex(_check_real_numpy_vector(dep_var))
        length_ex(indep_var.size != dep_var.size)
        # The processing function could potentially expand (say, via
        # interpolation) or shorten the data set length. To avoid errors
        # that dependent and independent variables have different number
        # of elements while setting the first processed variable (either
        # independent or dependent) both are "reset" to some dummy
        # value first
        self._raw_indep_var = None
        self._raw_dep_var = None
        self._indep_var_indexes = None
        self._set_indep_var(indep_var)
        self._set_dep_var(dep_var)

    @putil.pcontracts.contract(dep_col_label=str)
    def _set_dep_col_label(self, dep_col_label):
        self._dep_col_label = dep_col_label
        self._check_dep_col_label()
        self._apply_rfilter()
        self._process_data()

    @putil.pcontracts.contract(dep_var='real_numpy_vector')
    def _set_dep_var(self, dep_var):
        putil.exh.addex(
            ValueError,
            'Arguments `indep_var` and `dep_var`'
            ' must have the same number of elements',
            self._raw_indep_var.size != dep_var.size
        )
        self._raw_dep_var = round_mantissa(dep_var, PRECISION)
        self._update_dep_var()

    @putil.pcontracts.contract(fname='file_name_exists')
    def _set_fname(self, fname):
        # Windows compatibility: repr() escapes the slashes, but need to take
        # out explicit quotes
        self._fname = fname
        self._csv_obj = putil.pcsv.CsvFile(fname)
        self._apply_rfilter()   # This also gets indep_var,dep_var from file
        self._process_data()

    @putil.pcontracts.contract(fproc='function')
    def _set_fproc(self, fproc):
        min_args_ex = putil.exh.addex(
            ValueError,
            'Argument `fproc` (function *[func_name]*) '
            'does not have at least 2 arguments'
        )
        if fproc is not None:
            args = putil.pinspect.get_function_args(fproc)
            min_args_ex(
                (len(args) < 2) and ('*args' not in args) and
                ('**kwargs' not in args),
                _MF('func_name', fproc.__name__)
            )
        self._fproc = fproc
        self._check_fproc_eargs()
        self._process_data()

    @putil.pcontracts.contract(fproc_eargs='None|dict')
    def _set_fproc_eargs(self, fproc_eargs):
        # Check that extra arguments to see if
        # they are in the function definition
        self._fproc_eargs = fproc_eargs
        self._check_fproc_eargs()
        self._process_data()

    @putil.pcontracts.contract(indep_col_label=str)
    def _set_indep_col_label(self, indep_col_label):
        self._indep_col_label = indep_col_label
        self._check_indep_col_label()
        self._apply_rfilter()
        self._process_data()

    @putil.pcontracts.contract(indep_max='real_num')
    def _set_indep_max(self, indep_max):
        putil.exh.addex(
            ValueError,
            'Argument `indep_min` is greater than argument `indep_max`',
            _C(self.indep_min, indep_max) and (indep_max < self.indep_min)
        )
        self._indep_max = (
            round_mantissa(indep_max, PRECISION)
            if not isinstance(indep_max, int) else
            indep_max
        )
        # Apply minimum and maximum range bounding and assign it to
        # self._indep_var and thus this is what self.indep_var returns
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
            round_mantissa(indep_min, PRECISION)
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
            'Arguments `indep_var` and `dep_var`'
            ' must have the same number of elements',
            _C(indep_var, self._raw_dep_var) and
            (self._raw_dep_var.size != indep_var.size)
        )
        self._raw_indep_var = putil.eng.round_mantissa(indep_var, PRECISION)
        # Apply minimum and maximum range bounding and assign it to
        # self._indep_var and thus this is what self.indep_var returns
        self._update_indep_var()
        self._update_dep_var()

    @putil.pcontracts.contract(rfilter='csv_row_filter')
    def _set_rfilter(self, rfilter):
        # putil.pcsv is case insensitive and all caps
        self._rfilter = rfilter
        self._apply_rfilter()
        self._process_data()

    def _update_dep_var(self):
        """
        Update dependent variable (if assigned) to match the independent
        variable range bounding
        """
        self._dep_var = self._raw_dep_var
        if _C(self._indep_var_indexes, self._raw_dep_var):
            super(CsvSource, self)._set_dep_var(
                self._raw_dep_var[self._indep_var_indexes]
            )

    def _update_indep_var(self):
        """
        Update independent variable according to its minimum and maximum limits
        """
        empty_ex = putil.exh.addex(
            ValueError,
            'Argument `indep_var` is empty after '
            '`indep_min`/`indep_max` range bounding'
        )
        if self._raw_indep_var is not None:
            indep_min = _SEL(self.indep_min, self._raw_indep_var[0])
            indep_max = _SEL(self.indep_max, self._raw_indep_var[-1])
            min_indexes = self._raw_indep_var >= indep_min
            max_indexes = self._raw_indep_var <= indep_max
            self._indep_var_indexes = numpy.where(min_indexes & max_indexes)
            super(CsvSource, self)._set_indep_var(
                self._raw_indep_var[self._indep_var_indexes]
            )
            empty_ex(not self.indep_var.size)

    # Managed attributes
    dep_col_label = property(
        _get_dep_col_label,
        _set_dep_col_label,
        doc='Dependent column label (column name)'
    )
    r"""
    Gets or sets the dependent variable column label (column name)

    :type: string

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.plot.csv_source.CsvSource.dep_col_label

    :raises: (when assigned)

     * RuntimeError (Argument \`dep_col_label\` is not valid)

     * RuntimeError (Argument \`fproc\` (function *[func_name]*) returned
       an illegal number of values)

     * RuntimeError (Processing function *[func_name]* raised an exception
       when called with the following arguments: ``\n`` indep_var:
       *[indep_var_value]* ``\n`` dep_var: *[dep_var_value]* ``\n``
       fproc_eargs: *[fproc_eargs_value]* ``\n`` Exception error:
       *[exception_error_message]*)

     * TypeError (Argument \`fproc\` (function *[func_name]*) return value
       is not valid)

     * TypeError (Processed dependent variable is not valid)

     * TypeError (Processed independent variable is not valid)

     * ValueError (Column *[col_name]* (dependent column label) could not
       be found in comma-separated file *[fname]* header)

     * ValueError (Column *[col_name]* in row filter not found in comma-
       separated file *[fname]* header)

     * ValueError (Filtered dependent variable is empty)

     * ValueError (Filtered independent variable is empty)

     * ValueError (Processed dependent variable is empty)

     * ValueError (Processed independent and dependent variables are of
       different length)

     * ValueError (Processed independent variable is empty)

    .. [[[end]]]
    """

    # dep_var is read only
    dep_var = property(
        DataSource._get_dep_var,
        doc='Dependent variable Numpy vector (read only)'
    )
    """
    Gets the dependent variable Numpy vector
    """

    fname = property(
        _get_fname, _set_fname, doc='Comma-separated file name'
    )
    r"""
    Gets or sets the comma-separated values file from which data series is to
    be extracted. It is assumed that the first line of the file contains
    unique headers for each column

    :type: string

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc(exclude=exclude_list)) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.plot.csv_source.CsvSource.fname

    :raises: (when assigned)

     * OSError (File *[fname]* could not be found)

     * RuntimeError (Argument \`dep_var\` is not valid)

     * RuntimeError (Argument \`fname\` is not valid)

     * RuntimeError (Argument \`fproc\` (function *[func_name]*) returned
       an illegal number of values)

     * RuntimeError (Argument \`indep_var\` is not valid)

     * RuntimeError (Argument \`rfilter\` is not valid)

     * RuntimeError (Column headers are not unique in file *[fname]*)

     * RuntimeError (File *[fname]* has no valid data)

     * RuntimeError (File *[fname]* is empty)

     * RuntimeError (Processing function *[func_name]* raised an exception
       when called with the following arguments: ``\n`` indep_var:
       *[indep_var_value]* ``\n`` dep_var: *[dep_var_value]* ``\n``
       fproc_eargs: *[fproc_eargs_value]* ``\n`` Exception error:
       *[exception_error_message]*)

     * TypeError (Argument \`fproc\` (function *[func_name]*) return value
       is not valid)

     * TypeError (Processed dependent variable is not valid)

     * TypeError (Processed independent variable is not valid)

     * ValueError (Argument \`indep_var\` is empty after
       \`indep_min\`/\`indep_max\` range bounding)

     * ValueError (Argument \`rfilter\` is empty)

     * ValueError (Arguments \`indep_var\` and \`dep_var\` must have the
       same number of elements)

     * ValueError (Column *[col_name]* (dependent column label) could not
       be found in comma-separated file *[fname]* header)

     * ValueError (Column *[col_name]* (independent column label) could not
       be found in comma-separated file *[fname]* header)

     * ValueError (Column *[col_name]* in row filter not found in comma-
       separated file *[fname]* header)

     * ValueError (Column *[column_identifier]* not found)

     * ValueError (Filtered dependent variable is empty)

     * ValueError (Filtered independent variable is empty)

     * ValueError (Processed dependent variable is empty)

     * ValueError (Processed independent and dependent variables are of
       different length)

     * ValueError (Processed independent variable is empty)

    .. [[[end]]]
    """

    fproc = property(
        _get_fproc, _set_fproc, doc='Processing function'
    )
    r"""
    Gets or sets the data processing function pointer. The processing function
    is useful for "light" data massaging, like scaling, unit conversion, etc.;
    it is called after the data has been retrieved from the comma-separated
    values file and the resulting filtered data set has been bounded
    (if applicable). If :code:`None` no processing function is used.

    When defined the processing function is given two arguments, a Numpy vector
    containing the independent variable array (first argument) and a Numpy
    vector containing the dependent variable array (second argument).
    The expected return value is a two-item Numpy vector tuple, its first
    item being the processed independent variable array, and the second
    item being the processed dependent variable array. One valid processing
    function could be:

    .. =[=cog
    .. import docs.support.incfile
    .. docs.support.incfile.incfile('plot_example_3.py', cog.out, '19-26')
    .. =]=
    .. code-block:: python

        # indep_var is a Numpy vector, in this example time,
        # in seconds. dep_var is a Numpy vector
        def proc_func1(indep_var, dep_var):
            # Scale time to pico-seconds
            indep_var = indep_var/1e-12
            # Remove offset
            dep_var = dep_var-dep_var[0]
            return indep_var, dep_var

    .. =[=end=]=

    :type: :ref:`Function` or None

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.plot.csv_source.CsvSource.fproc

    :raises: (when assigned)

     * RuntimeError (Argument \`fproc\` (function *[func_name]*) returned
       an illegal number of values)

     * RuntimeError (Argument \`fproc\` is not valid)

     * RuntimeError (Processing function *[func_name]* raised an exception
       when called with the following arguments: ``\n`` indep_var:
       *[indep_var_value]* ``\n`` dep_var: *[dep_var_value]* ``\n``
       fproc_eargs: *[fproc_eargs_value]* ``\n`` Exception error:
       *[exception_error_message]*)

     * TypeError (Argument \`fproc\` (function *[func_name]*) return value
       is not valid)

     * TypeError (Processed dependent variable is not valid)

     * TypeError (Processed independent variable is not valid)

     * ValueError (Argument \`fproc\` (function *[func_name]*) does not
       have at least 2 arguments)

     * ValueError (Extra argument \`*[arg_name]*\` not found in argument
       \`fproc\` (function *[func_name]*) definition)

     * ValueError (Processed dependent variable is empty)

     * ValueError (Processed independent and dependent variables are of
       different length)

     * ValueError (Processed independent variable is empty)

    .. [[[end]]]
    """

    fproc_eargs = property(
        _get_fproc_eargs,
        _set_fproc_eargs,
        doc='Processing function extra argument dictionary'
    )
    # pylint: disable=W1401
    r"""
    Gets or sets the extra arguments for the data processing function. The
    arguments are specified by key-value pairs of a dictionary, for each
    dictionary element the dictionary key specifies the argument name and the
    dictionary value specifies the argument value. The extra parameters are
    passed by keyword so they must appear in the function definition explicitly
    or keyword variable argument collection must be used
    (:code:`**kwargs`, for example). If :code:`None` no extra arguments are
    passed to the processing function (if defined)

    :type: dictionary or None

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.plot.csv_source.CsvSource.fproc_eargs

    :raises: (when assigned)

     * RuntimeError (Argument \`fproc_eargs\` is not valid)

     * RuntimeError (Argument \`fproc\` (function *[func_name]*) returned
       an illegal number of values)

     * RuntimeError (Processing function *[func_name]* raised an exception
       when called with the following arguments: ``\n`` indep_var:
       *[indep_var_value]* ``\n`` dep_var: *[dep_var_value]* ``\n``
       fproc_eargs: *[fproc_eargs_value]* ``\n`` Exception error:
       *[exception_error_message]*)

     * TypeError (Argument \`fproc\` (function *[func_name]*) return value
       is not valid)

     * TypeError (Processed dependent variable is not valid)

     * TypeError (Processed independent variable is not valid)

     * ValueError (Extra argument \`*[arg_name]*\` not found in argument
       \`fproc\` (function *[func_name]*) definition)

     * ValueError (Processed dependent variable is empty)

     * ValueError (Processed independent and dependent variables are of
       different length)

     * ValueError (Processed independent variable is empty)

    .. [[[end]]]

    For example:

    .. =[=cog
    .. import docs.support.incfile
    .. docs.support.incfile.incfile('plot_example_5.py', cog.out)
    .. =]=
    .. code-block:: python

        # plot_example_5.py
        import sys, putil.misc, putil.pcsv
        if sys.hexversion < 0x03000000:
            from putil.compat2 import _write
        else:
            from putil.compat3 import _write

        def write_csv_file(file_handle):
            _write(file_handle, 'Col1,Col2\n')
            _write(file_handle, '0E-12,10\n')
            _write(file_handle, '1E-12,0\n')
            _write(file_handle, '2E-12,20\n')
            _write(file_handle, '3E-12,-10\n')
            _write(file_handle, '4E-12,30\n')

        def proc_func2(indep_var, dep_var, par1, par2):
            return (indep_var/1E-12)+(2*par1), dep_var+sum(par2)

        def create_csv_source():
            with putil.misc.TmpFile(write_csv_file) as fname:
                obj = putil.plot.CsvSource(
                    fname=fname,
                    indep_col_label='Col1',
                    dep_col_label='Col2',
                    fproc=proc_func2,
                    fproc_eargs={'par1':5, 'par2':[1, 2, 3]}
                )
            return obj

    .. =[=end=]=

    .. code-block:: python

        >>> from __future__ import print_function
        >>> import docs.support.plot_example_5
        >>> obj = docs.support.plot_example_5.create_csv_source()
        >>> print(obj)  #doctest: +ELLIPSIS
        File name: ...
        Row filter: None
        Independent column label: Col1
        Dependent column label: Col2
        Processing function: proc_func2
        Processing function extra arguments: None
        Independent variable minimum: -inf
        Independent variable maximum: +inf
        Independent variable: [ 10, 11, 12, 13, 14 ]
        Dependent variable: [ 16, 6, 26, -4, 36 ]
    """

    indep_col_label = property(
        _get_indep_col_label,
        _set_indep_col_label,
        doc='Independent column label (column name)'
    )
    r"""
    Gets or sets the independent variable column label (column name)

    :type: string

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.plot.csv_source.CsvSource.indep_col_label

    :raises: (when assigned)

     * RuntimeError (Argument \`fproc\` (function *[func_name]*) returned
       an illegal number of values)

     * RuntimeError (Argument \`indep_col_label\` is not valid)

     * RuntimeError (Processing function *[func_name]* raised an exception
       when called with the following arguments: ``\n`` indep_var:
       *[indep_var_value]* ``\n`` dep_var: *[dep_var_value]* ``\n``
       fproc_eargs: *[fproc_eargs_value]* ``\n`` Exception error:
       *[exception_error_message]*)

     * TypeError (Argument \`fproc\` (function *[func_name]*) return value
       is not valid)

     * TypeError (Processed dependent variable is not valid)

     * TypeError (Processed independent variable is not valid)

     * ValueError (Column *[col_name]* (independent column label) could not
       be found in comma-separated file *[fname]* header)

     * ValueError (Column *[col_name]* in row filter not found in comma-
       separated file *[fname]* header)

     * ValueError (Filtered dependent variable is empty)

     * ValueError (Filtered independent variable is empty)

     * ValueError (Processed dependent variable is empty)

     * ValueError (Processed independent and dependent variables are of
       different length)

     * ValueError (Processed independent variable is empty)

    .. [[[end]]]
    """

    indep_max = property(
        _get_indep_max, _set_indep_max, doc='Maximum of independent variable'
    )
    r"""
    Gets or sets the maximum independent variable limit. If :code:`None` no
    maximum thresholding is applied to the data

    :type: :ref:`RealNum` or None

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.plot.csv_source.CsvSource.indep_max

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

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.plot.csv_source.CsvSource.indep_min

    :raises: (when assigned)

     * RuntimeError (Argument \`indep_min\` is not valid)

     * ValueError (Argument \`indep_min\` is greater than argument
       \`indep_max\`)

     * ValueError (Argument \`indep_var\` is empty after
       \`indep_min\`/\`indep_max\` range bounding)

    .. [[[end]]]
    """

    # indep_var is read only
    indep_var = property(
        DataSource._get_indep_var,
        doc='Independent variable Numpy vector (read only)'
    )
    """
    Gets the independent variable Numpy vector
    """

    rfilter = property(
        _get_rfilter, _set_rfilter, doc='Row filter dictionary'
    )
    r"""
    Gets or sets the row filter. If :code:`None` no row filtering is
    performed

    :type: :ref:`CsvRowFilter` or None

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.plot.csv_source.CsvSource.rfilter

    :raises: (when assigned)

     * RuntimeError (Argument \`fproc\` (function *[func_name]*) returned
       an illegal number of values)

     * RuntimeError (Argument \`rfilter\` is not valid)

     * RuntimeError (Processing function *[func_name]* raised an exception
       when called with the following arguments: ``\n`` indep_var:
       *[indep_var_value]* ``\n`` dep_var: *[dep_var_value]* ``\n``
       fproc_eargs: *[fproc_eargs_value]* ``\n`` Exception error:
       *[exception_error_message]*)

     * TypeError (Argument \`fproc\` (function *[func_name]*) return value
       is not valid)

     * TypeError (Processed dependent variable is not valid)

     * TypeError (Processed independent variable is not valid)

     * ValueError (Argument \`rfilter\` is empty)

     * ValueError (Column *[col_name]* in row filter not found in comma-
       separated file *[fname]* header)

     * ValueError (Filtered dependent variable is empty)

     * ValueError (Filtered independent variable is empty)

     * ValueError (Processed dependent variable is empty)

     * ValueError (Processed independent and dependent variables are of
       different length)

     * ValueError (Processed independent variable is empty)

    .. [[[end]]]
    """
