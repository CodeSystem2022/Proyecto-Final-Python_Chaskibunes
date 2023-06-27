# csv_file.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,R0201,W0105,W0611

# Standard library imports
import csv
import operator
import os
import platform
import sys
# Putil imports
import putil.exh
import putil.misc
import putil.pcontracts
from putil.ptypes import (
    csv_col_filter,
    csv_filtered,
    csv_row_filter,
    file_name,
    file_name_exists,
    non_negative_integer
)
from .write import _write_int


###
# Exception tracing initialization code
###
"""
[[[cog
import os, sys
sys.path.append(os.environ['TRACER_DIR'])
import trace_ex_pcsv_csv_file
exobj = trace_ex_pcsv_csv_file.trace_module(no_print=True)
]]]
[[[end]]]
"""


###
# Functions
###
def _homogenize_data_filter(dfilter):
    """
    Make data filter definition consistent, create a
    tuple where first element is the row filter and
    the second element is the column filter
    """
    if isinstance(dfilter, tuple) and (len(dfilter) == 1):
        dfilter = (dfilter[0], None)
    if (dfilter is None) or (dfilter == (None, None)) or (dfilter == (None, )):
        dfilter = (None, None)
    elif isinstance(dfilter, dict):
        dfilter = (dfilter, None)
    elif (isinstance(dfilter, str) or (isinstance(dfilter, int) and
         (not isinstance(dfilter, bool))) or isinstance(dfilter, list)):
        dfilter = (None, dfilter if isinstance(dfilter, list) else [dfilter])
    elif (isinstance(dfilter[0], dict) or ((dfilter[0] is None) and
         (not isinstance(dfilter[1], dict)))):
        pass
    else:
        dfilter = (dfilter[1], dfilter[0])
    return dfilter


def _tofloat(obj):
    """ Convert to float if object is a float string """
    if 'inf' in obj.lower().strip():
        return obj
    try:
        return int(obj)
    except ValueError:
        try:
            return float(obj)
        except ValueError:
            return obj


###
# Classes
###
class CsvFile(object):
    r"""
    Processes comma-separated values (CSV) files

    :param fname: Name of the comma-separated values file to read
    :type fname: :ref:`FileNameExists`

    :param dfilter: Row and/or column filter. If None no data filtering is
                    done
    :type  dfilter: :ref:`CsvDataFilter` or None

    :param has_header: Flag that indicates whether the comma-separated
                       values file has column headers in its first line
                       (True) o not (False)
    :type  has_header: boolean

    :param frow: First data row (starting from 1). If 0 the row where data
                 starts is auto-detected as the first row that has a number
                 (integer of float) in at least one of its columns
    :type  frow: :ref:`NonNegativeInteger`

    :rtype: :py:class:`putil.pcsv.CsvFile` object

    .. [[[cog cog.out(exobj.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.pcsv.csv_file.CsvFile.__init__

    :raises:
     * OSError (File *[fname]* could not be found)

     * RuntimeError (Argument \`dfilter\` is not valid)

     * RuntimeError (Argument \`fname\` is not valid)

     * RuntimeError (Argument \`frow\` is not valid)

     * RuntimeError (Argument \`has_header\` is not valid)

     * RuntimeError (Column headers are not unique in file *[fname]*)

     * RuntimeError (File *[fname]* has no valid data)

     * RuntimeError (File *[fname]* is empty)

     * RuntimeError (Invalid column specification)

     * ValueError (Column *[column_identifier]* not found)

    .. [[[end]]]
    """
    # pylint: disable=R0902,W0631
    @putil.pcontracts.contract(
        fname='file_name_exists'
    )
    def __init__(self, fname, dfilter=None, has_header=True, frow=0):
        self._header = None
        self._header_upper = None
        self._data = None
        self._fdata = None
        self._cfilter = None
        self._rfilter = None
        self._exh = None
        self._fname = fname
        self._has_header = None
        self._data_rows = None
        self._fdata_rows = None
        self._data_cols = None
        self._fdata_cols = None
        self._set_has_header(has_header)
        # Register exceptions
        empty_exobj = putil.exh.addex(RuntimeError, 'File *[fname]* is empty')
        col_exobj = putil.exh.addex(
            RuntimeError, 'Column headers are not unique in file *[fname]*'
        )
        nvdata_exobj = putil.exh.addex(
            RuntimeError, 'File *[fname]* has no valid data'
        )
        edata = {'field':'fname', 'value':self._fname}
        # Read data
        if sys.hexversion < 0x03000000: # pragma: no cover, no branch
            fname = putil.misc.normalize_windows_fname(fname)
            with open(fname, 'r') as file_handle:
                self._raw_data = [row for row in csv.reader(file_handle)]
        else: # pragma: no cover, no branch
            with open(fname, 'r', newline='') as file_handle:
                self._raw_data = [row for row in csv.reader(file_handle)]
        # Process header
        empty_exobj(not len(self._raw_data), edata)
        if has_header:
            self._header = self._raw_data[0]
            self._header_upper = [col.upper() for col in self._header]
            col_exobj(
                len(set(self._header_upper)) != len(self._header_upper), edata
            )
        else:
            self._header = list(range(0, len(self._raw_data[0])))
            self._header_upper = self._header
        frow = self._validate_frow(frow)
        if frow == 0:
            # Find start of data row. A data row is defined as one that has at
            # least one column with a number
            for num, row in enumerate(self._raw_data[1 if has_header else 0:]):
                if any([putil.misc.isnumber(_tofloat(col)) for col in row]):
                    break
            else:
                nvdata_exobj(True, edata)
        else:
            nvdata_exobj(frow > len(self._raw_data), edata)
            num = frow-(2 if has_header else 1)
        # Set up class properties
        self._data = [
            [
                None if col.strip() == '' else _tofloat(col)
                for col in row
            ]
            for row in self._raw_data[num+(1 if has_header else 0):]
        ]
        self._data_cols = len(self._header)
        self._data_rows = len(self._data)
        self._fdata_rows = self._data_rows
        self._reset_dfilter_int()
        # [r|c]rfilter already validated, can use internal function,
        # not API end-point
        self._set_dfilter(dfilter)

    def __eq__(self, other):
        """
        Tests object equality. For example:

            >>> import putil.misc, putil.pcsv
            >>> with putil.misc.TmpFile() as fname:
            ...     putil.pcsv.write(fname, [['a'], [1]], append=False)
            ...     obj1 = putil.pcsv.CsvFile(fname, dfilter='a')
            ...     obj2 = putil.pcsv.CsvFile(fname, dfilter='a')
            ...
            >>> with putil.misc.TmpFile() as fname:
            ...     putil.pcsv.write(fname, [['a'], [2]], append=False)
            ...     obj3 = putil.pcsv.CsvFile(fname, dfilter='a')
            ...
            >>> obj1 == obj2
            True
            >>> obj1 == obj3
            False
            >>> 5 == obj3
            False
        """
        # pylint: disable=W0212
        if not isinstance(other, CsvFile):
            return False
        sfname = putil.misc.normalize_windows_fname(self._fname)
        ofname = putil.misc.normalize_windows_fname(other._fname)
        return all(
            [
                sfname == ofname,
                self._rfilter == other._rfilter,
                self._cfilter == other._cfilter,
                self._has_header == other._has_header
            ]
        )

    def __repr__(self):
        """
        Returns a string with the expression needed to re-create the object.
        For example:

            >>> import putil.misc, putil.pcsv
            >>> with putil.misc.TmpFile() as fname:
            ...     putil.pcsv.write(fname, [['a'], [1]], append=False)
            ...     obj1 = putil.pcsv.CsvFile(fname, dfilter='a')
            ...     exec("obj2="+repr(obj1))
            >>> obj1 == obj2
            True
            >>> repr(obj1)
            "putil.pcsv.CsvFile(fname=r'...', dfilter=['a'])"
        """
        dfilter_list = (
            None, self._cfilter, self._rfilter, (self._rfilter, self._cfilter)
        )
        dfilter = dfilter_list[
            2*(self._rfilter is not None)+(self._cfilter is not None)
        ]
        has_header = self._has_header
        ret = [
            "putil.pcsv.CsvFile(fname=r'{0}'".format(
                putil.misc.normalize_windows_fname(self._fname)
            )
        ]
        if dfilter:
            ret.append("dfilter={0}".format(dfilter))
        if not has_header:
            ret.append("has_header={0}".format(has_header))
        return ", ".join(ret)+")"


    def __str__(self):
        """
        Returns a string with a detailed description of the object's contents.
        For example:

            >>> from __future__ import print_function
            >>> import putil.misc, putil.pcsv
            >>> with putil.misc.TmpFile() as fname:
            ...     putil.pcsv.write(fname, [['a', 'b'], [1, 2], [3, 4]])
            ...     obj = putil.pcsv.CsvFile(fname, dfilter='a')
            ...
            >>> print(str(obj)) #doctest: +ELLIPSIS
            File: ...
            Header: ['a', 'b']
            Row filter: None
            Column filter: ['a']
            Rows: 2
            Columns: 2 (1 filtered)
        """
        ret = ['File: {0}'.format(self._fname)]
        ret += ['Header: {0}'.format(self._header)]
        ret += ['Row filter: {0}'.format(self._rfilter)]
        ret += ['Column filter: {0}'.format(self._cfilter)]
        ret += [
            'Rows: {rrows}{urows}'.format(
                rrows=self._data_rows,
                urows=(
                    ' ({rows} filtered)'.format(rows=self._fdata_rows)
                    if self._rfilter is not None else
                    ''
                )
            )
        ]
        ret += [
            'Columns: {rcols}{ucols}'.format(
                rcols=self._data_cols,
                ucols=(
                    ' ({cols} filtered)'.format(cols=self._fdata_cols)
                    if self._cfilter is not None else
                    ''
                )
            )
        ]
        return '\n'.join(ret)

    def _format_rfilter(self, rfilter):
        return [
            (
                (
                    self._header_upper.index(key.upper())
                    if isinstance(key, str) else
                    key
                ),
                (
                    [value]
                    if not putil.misc.isiterable(value) else
                    [item for item in value]
                )
            )
            for key, value in rfilter.items()
        ] if rfilter else []

    def _gen_col_index(self, filtered=True):
        col_index_list = []
        if self._cfilter and (filtered in [True, 'B', 'b', 'C', 'c']):
            for col in self._cfilter:
                if isinstance(col, str):
                    col_index_list.append(
                        self._header_upper.index(col.upper())
                    )
                else:
                    col_index_list.append(col)
            return col_index_list
        return range(len(self._header))

    def _get_cfilter(self):
        return self._cfilter

    def _get_dfilter(self):
        return (self._rfilter, self._cfilter)

    def _get_rfilter(self):
        return self._rfilter

    def _reset_dfilter_int(self, ftype=True):
        if ftype in [True, 'B', 'b', 'R', 'r']:
            self._rfilter = None
        if ftype in [True, 'B', 'b', 'C', 'c']:
            self._cfilter = None

    def _in_header(self, col):
        """ Validate column identifier(s) """
        if not self._has_header:
            # Conditionally register exceptions so that they do not appear
            # in situations where has_header is always True. In this way
            # they are not auto-documented by default
            icol_ex = putil.exh.addex(
                RuntimeError, 'Invalid column specification'
            )
        hnf_ex = putil.exh.addex(
            ValueError, 'Column *[column_identifier]* not found'
        )
        col_list = (
            [col]
            if isinstance(col, str) or isinstance(col, int) else
            col
        )
        for col in col_list:
            edata = {'field':'column_identifier', 'value':col}
            if not self._has_header:
                # Condition not subsumed in raise_exception_if
                # so that calls that always have has_header=True
                # do not pick up this exception
                icol_ex(not isinstance(col, int))
                hnf_ex((col < 0) or (col > len(self._header)-1), edata)
            else:
                hnf_ex(
                    (isinstance(col, int) and
                    ((col < 0) or (col > self._data_cols))) or
                    (isinstance(col, str) and
                    (col.upper() not in self._header_upper)),
                    edata
                )
        return col_list

    @putil.pcontracts.contract(cfilter='csv_col_filter')
    def _set_cfilter(self, cfilter):
        self._reset_dfilter_int('C')
        self._add_dfilter_int(cfilter)

    @putil.pcontracts.contract(dfilter='csv_data_filter')
    def _set_dfilter(self, dfilter):
        dfilter = _homogenize_data_filter(dfilter)
        self._reset_dfilter_int()
        self._add_dfilter_int(dfilter)

    @putil.pcontracts.contract(rfilter='csv_row_filter')
    def _set_rfilter(self, rfilter):
        self._reset_dfilter_int('R')
        self._add_dfilter_int(rfilter, letter='r')

    def _add_dfilter_int(self, dfilter, letter='d'):
        rfilter, cfilter = _homogenize_data_filter(dfilter)
        if cfilter is not None:
            cfilter = self._in_header(cfilter)
            if self._cfilter is None:
                self._cfilter = []
            self._cfilter.append(cfilter)
            cfilter = putil.misc.flatten_list(self._cfilter)
            col_indexes = (
                [
                    item
                    if isinstance(item, int) else
                    self._header_upper.index(item.upper())
                    for item in cfilter
                ]
            )
            self._cfilter = [self._header[item] for item in col_indexes]
            self._fdata_cols = len(cfilter)
        if rfilter is not None:
            self._validate_rfilter(rfilter, letter)
            for key in rfilter:
                if self._rfilter is None:
                    self._rfilter = {}
                if key in self._rfilter:
                    self._rfilter[key] = list(
                        set(
                            (
                                self._rfilter[key]
                                if isinstance(self._rfilter[key], list) else
                                [self._rfilter[key]]
                            )
                            +
                            (
                                rfilter[key]
                                if isinstance(rfilter[key], list) else
                                [rfilter[key]]
                            )
                        )
                    )
                else:
                    self._rfilter[key] = rfilter[key]
            self._fdata_rows = len(self._apply_filter('R'))

    def _apply_filter(self, ftype, no_empty=False):
        # pylint: disable=W0141
        rlist = [True, 'B', 'b', 'R', 'r']
        clist = [True, 'B', 'b', 'C', 'c']
        apply_filter = (
            self._rfilter and (ftype in rlist)
            or
            self._cfilter and (ftype in clist)
        )
        if self._rfilter and (ftype in rlist):
            # Row filter
            df_tuples = self._format_rfilter(self._rfilter)
            self._fdata = [
                row for row in self._data
                if all([row[col_num] in col_value
                for col_num, col_value in df_tuples])
            ]
        if self._cfilter and (ftype in clist):
            # Column filter
            col_index_list = self._gen_col_index()
            # Filter column data
            self._fdata = [
                [row[index] for index in col_index_list]
                for row in (
                    self._fdata
                    if self._rfilter and (ftype in rlist) else
                    self._data
                )
            ]
        data = self._fdata if apply_filter else self._data
        ffull = lambda row: not any([item is None for item in row])
        return list(filter(ffull, data)) if no_empty else data

    @putil.pcontracts.contract(has_header=bool)
    def _set_has_header(self, has_header):
        self._has_header = has_header

    def _validate_frow(self, frow):
        """ Validate frow argument """
        is_int = isinstance(frow, int) and (not isinstance(frow, bool))
        putil.exh.addai('frow', not (is_int and (frow >= 0)))
        return frow

    def _validate_rfilter(self, rfilter, letter='d'):
        """ Validate that all columns in filter are in header """
        if letter == 'd':
            putil.exh.addai(
                'dfilter', (
                    (not self._has_header)
                    and any(
                        [
                            not isinstance(item, int)
                            for item in rfilter.keys()
                        ]
                    )
                )
            )
        else:
            putil.exh.addai(
                'rfilter', (
                    (not self._has_header)
                    and any(
                        [
                            not isinstance(item, int)
                            for item in rfilter.keys()
                        ]
                    )
                )
            )
        for key in rfilter:
            self._in_header(key)
            rfilter[key] = (
                [rfilter[key]]
                if isinstance(rfilter[key], str) else
                rfilter[key]
            )

    @putil.pcontracts.contract(dfilter='csv_data_filter')
    def add_dfilter(self, dfilter):
        r"""
        Adds more row(s) or column(s) to the existing data filter.
        Duplicate filter values are eliminated

        :param dfilter: Row and/or column filter
        :type  dfilter: :ref:`CsvDataFilter`

        .. [[[cog cog.out(exobj.get_sphinx_autodoc()) ]]]
        .. Auto-generated exceptions documentation for
        .. putil.pcsv.csv_file.CsvFile.add_dfilter

        :raises:
         * RuntimeError (Argument \`dfilter\` is not valid)

         * RuntimeError (Invalid column specification)

         * ValueError (Column *[column_identifier]* not found)

        .. [[[end]]]
        """
        self._add_dfilter_int(dfilter)

    @putil.pcontracts.contract(filtered=bool)
    def cols(self, filtered=False):
        r"""
        Returns the number of data columns

        :param filtered: Flag that indicates whether the raw (input) data
                         should be used (False) or whether filtered data
                         should be used (True)
        :type  filtered: boolean

        .. [[[cog cog.out(exobj.get_sphinx_autodoc()) ]]]
        .. Auto-generated exceptions documentation for
        .. putil.pcsv.csv_file.CsvFile.cols

        :raises: RuntimeError (Argument \`filtered\` is not valid)

        .. [[[end]]]
        """
        return self._fdata_cols if filtered else self._data_cols

    @putil.pcontracts.contract(filtered='csv_filtered', no_empty=bool)
    def data(self, filtered=False, no_empty=False):
        r"""
         Returns (filtered) file data. The returned object is a list, each item
         is a sub-list corresponding to a row of data; each item in the
         sub-lists contains data corresponding to a particular column

        :param filtered: Filtering type
        :type  filtered: :ref:`CsvFiltered`

        :param no_empty: Flag that indicates whether rows with empty columns
                         should be filtered out (True) or not (False)
        :type  no_empty: bool

        :rtype: list

        .. [[[cog cog.out(exobj.get_sphinx_autodoc()) ]]]
        .. Auto-generated exceptions documentation for
        .. putil.pcsv.csv_file.CsvFile.data

        :raises:
         * RuntimeError (Argument \`filtered\` is not valid)

         * RuntimeError (Argument \`no_empty\` is not valid)

        .. [[[end]]]
        """
        return self._apply_filter(filtered, no_empty)

    @putil.pcontracts.contract(order='csv_col_sort')
    def dsort(self, order):
        r"""
        Sorts rows

        :param order: Sort order
        :type  order: :ref:`CsvColFilter`

        .. [[[cog cog.out(exobj.get_sphinx_autodoc()) ]]]
        .. Auto-generated exceptions documentation for
        .. putil.pcsv.csv_file.CsvFile.dsort

        :raises:
         * RuntimeError (Argument \`order\` is not valid)

         * RuntimeError (Invalid column specification)

         * ValueError (Column *[column_identifier]* not found)

        .. [[[end]]]
        """
        # Make order conforming to a list of dictionaries
        order = order if isinstance(order, list) else [order]
        norder = [
            {item:'A'} if not isinstance(item, dict) else item
            for item in order
        ]
        # Verify that all columns exist in file
        self._in_header([list(item.keys())[0] for item in norder])
        # Get column indexes
        clist = []
        for nitem in norder:
            for key, value in nitem.items():
                clist.append(
                    (
                        key if isinstance(key, int) else
                        self._header_upper.index(key.upper()),
                        value.upper() == 'D'
                    )
                )
        # From the Python documentation:
        # "Starting with Python 2.3, the sort() method is guaranteed to be
        # stable. A sort is stable if it guarantees not to change the
        # relative order of elements that compare equal - this is helpful
        # for sorting in multiple passes (for example, sort by department,
        # then by salary grade)."
        # This means that the sorts have to be done from "minor" column to
        # "major" column
        for (cindex, rvalue) in reversed(clist):
            fpointer = operator.itemgetter(cindex)
            self._data.sort(key=fpointer, reverse=rvalue)


    @putil.pcontracts.contract(filtered=bool)
    def header(self, filtered=False):
        r"""
        Returns the data header. When the raw (input) data is used the data
        header is a list of the comma-separated values file header if the file
        is loaded with header (each list item is a column header) or a list of
        column numbers if the file is loaded without header (column zero is
        the leftmost column). When filtered data is used the data header
        is the active column filter, if any, otherwise it is the same as the
        raw (input) data header

        :param filtered: Flag that indicates whether the raw (input) data
                         should be used (False) or whether filtered data
                         should be used (True)
        :type  filtered: boolean

        :rtype: list of strings or integers

        .. [[[cog cog.out(exobj.get_sphinx_autodoc()) ]]]
        .. Auto-generated exceptions documentation for
        .. putil.pcsv.csv_file.CsvFile.header

        :raises: RuntimeError (Argument \`filtered\` is not valid)

        .. [[[end]]]
        """
        return (
            self._header
            if (not filtered) or (filtered and self._cfilter is None) else
            self._cfilter
        )

    @putil.pcontracts.contract(rdata='list(list)', filtered='csv_filtered')
    def replace(self, rdata, filtered=False):
        r"""
        Replaces data

        :param rdata: Replacement data
        :type  rdata: list of lists

        :param filtered: Filtering type
        :type  filtered: :ref:`CsvFiltered`

        .. [[[cog cog.out(exobj.get_sphinx_autodoc(width=63)) ]]]
        .. Auto-generated exceptions documentation for
        .. putil.pcsv.csv_file.CsvFile.replace

        :raises:
         * RuntimeError (Argument \`filtered\` is not valid)

         * RuntimeError (Argument \`rdata\` is not valid)

         * ValueError (Number of columns mismatch between input and
           replacement data)

         * ValueError (Number of rows mismatch between input and
           replacement data)

        .. [[[end]]]
        """
        # pylint: disable=R0914
        rdata_ex = putil.exh.addai('rdata')
        rows_ex = putil.exh.addex(
            ValueError,
            'Number of rows mismatch between input and replacement data'
        )
        cols_ex = putil.exh.addex(
            ValueError,
            'Number of columns mismatch between input and replacement data'
        )
        rdata_ex(any([len(item) != len(rdata[0]) for item in rdata]))
        # Use all columns if no specification has been given
        cfilter = (
            self._cfilter
            if filtered in [True, 'B', 'b', 'C', 'c'] else
            self._header
        )
        # Verify column names, has to be done before getting data
        col_num = len(self._data[0])-1
        odata = self._apply_filter(filtered)
        cfilter = (
            self._cfilter
            if filtered in [True, 'B', 'b', 'C', 'c'] else
            self._header
        )
        col_index = [
            self._header_upper.index(col_id.upper())
            if isinstance(col_id, str) else
            col_id
            for col_id in cfilter
        ]
        rows_ex(len(odata) != len(rdata))
        cols_ex(len(odata[0]) != len(rdata[0]))
        df_tuples = self._format_rfilter(self._rfilter)
        rnum = 0
        for row in self._data:
            if (not filtered) or (filtered and
                all([row[col_num] in col_value
                for col_num, col_value in df_tuples])):
                for col_num, new_data in zip(col_index, rdata[rnum]):
                    row[col_num] = new_data
                rnum = rnum+1

    @putil.pcontracts.contract(ftype='csv_filtered')
    def reset_dfilter(self, ftype=True):
        r"""
        Reset (clears) the data filter

        :param ftype: Filter type
        :type  ftype: :ref:`CsvFiltered`

        .. [[[cog cog.out(exobj.get_sphinx_autodoc()) ]]]
        .. Auto-generated exceptions documentation for
        .. putil.pcsv.csv_file.CsvFile.reset_dfilter

        :raises: RuntimeError (Argument \`ftype\` is not valid)

        .. [[[end]]]
        """
        self._reset_dfilter_int(ftype)

    @putil.pcontracts.contract(filtered=bool)
    def rows(self, filtered=False):
        r"""
        Returns the number of data rows

        :param filtered: Flag that indicates whether the raw (input) data
                         should be used (False) or whether filtered data
                         should be used (True)
        :type  filtered: boolean

        .. [[[cog cog.out(exobj.get_sphinx_autodoc()) ]]]
        .. Auto-generated exceptions documentation for
        .. putil.pcsv.csv_file.CsvFile.rows

        :raises: RuntimeError (Argument \`filtered\` is not valid)

        .. [[[end]]]
        """
        return self._fdata_rows if filtered else self._data_rows

    @putil.pcontracts.contract(
            fname='None|file_name',
            filtered='csv_filtered',
            header='str|bool|list[>0](str)',
            append=bool
    )
    def write(self, fname=None, filtered=False, header=True, append=False):
        r"""
        Writes (processed) data to a specified comma-separated values (CSV)
        file

        :param fname: Name of the comma-separated values file to be
                      written. If None the file from which the data originated
                      is overwritten
        :type  fname: :ref:`FileName`

        :param filtered: Filtering type
        :type  filtered: :ref:`CsvFiltered`

        :param header: If a list, column headers to use in the file. If
                       boolean, flag that indicates whether the input column
                       headers should be written (True) or not (False)
        :type  header: string, list of strings or boolean

        :param append: Flag that indicates whether data is added to an
                       existing file (or a new file is created if it does not
                       exist) (True), or whether data overwrites the file
                       contents (if the file exists) or creates a new file if
                       the file does not exists (False)
        :type  append: boolean

        .. [[[cog cog.out(exobj.get_sphinx_autodoc()) ]]]
        .. Auto-generated exceptions documentation for
        .. putil.pcsv.csv_file.CsvFile.write

        :raises:
         * OSError (File *[fname]* could not be created: *[reason]*)

         * RuntimeError (Argument \`append\` is not valid)

         * RuntimeError (Argument \`filtered\` is not valid)

         * RuntimeError (Argument \`fname\` is not valid)

         * RuntimeError (Argument \`header\` is not valid)

         * RuntimeError (Argument \`no_empty\` is not valid)

         * ValueError (There is no data to save to file)

        .. [[[end]]]
        """
        # pylint: disable=R0913
        write_ex = putil.exh.addex(
            ValueError, 'There is no data to save to file'
        )
        fname = self._fname if fname is None else fname
        data = self.data(filtered=filtered)
        write_ex(
            (len(data) == 0) or ((len(data) == 1) and (len(data[0]) == 0))
        )
        if header:
            header = [header] if isinstance(header, str) else header
            cfilter = self._gen_col_index(filtered=filtered)
            filtered_header = (
                [self._header[item] for item in cfilter]
                if self._has_header else
                cfilter
            )
            file_header = (
                filtered_header
                if isinstance(header, bool) else
                header
            )
        # Convert None's to ''
        data = [
            ["''" if item is None else item for item in row] for row in data
        ]
        _write_int(
            fname, [file_header]+data if header else data, append=append
        )

    # Managed attributes
    cfilter = property(_get_cfilter, _set_cfilter, doc='Column filter')
    r"""
    Sets or returns the column filter

    :type: :ref:`CsvColFilter` or None. If None no column filtering is done

    :rtype: :ref:`CsvColFilter` or None

    .. [[[cog cog.out(exobj.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.pcsv.csv_file.CsvFile.cfilter

    :raises: (when assigned)

     * RuntimeError (Argument \`cfilter\` is not valid)

     * RuntimeError (Invalid column specification)

     * ValueError (Column *[column_identifier]* not found)

    .. [[[end]]]
    """

    dfilter = property(_get_dfilter, _set_dfilter, doc='Data filter')
    r"""
    Sets or returns the data (row and/or column) filter. The first tuple
    item is the row filter and the second tuple item is the column filter

    :type: :ref:`CsvDataFilter` or None. If None no data filtering is done

    :rtype: :ref:`CsvDataFilter` or None

    .. [[[cog cog.out(exobj.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.pcsv.csv_file.CsvFile.dfilter

    :raises: (when assigned)

     * RuntimeError (Argument \`dfilter\` is not valid)

     * RuntimeError (Invalid column specification)

     * ValueError (Column *[column_identifier]* not found)

    .. [[[end]]]
    """

    rfilter = property(_get_rfilter, _set_rfilter, doc='Returns row filter')
    r"""
    Sets or returns the row filter

    :type: :ref:`CsvRowFilter` or None. If None no row filtering is done

    :rtype: :ref:`CsvRowFilter` or None

    .. [[[cog cog.out(exobj.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.pcsv.csv_file.CsvFile.rfilter

    :raises: (when assigned)

     * RuntimeError (Argument \`rfilter\` is not valid)

     * RuntimeError (Invalid column specification)

     * ValueError (Argument \`rfilter\` is empty)

     * ValueError (Column *[column_identifier]* not found)

    .. [[[end]]]
    """
