# merge.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,W0105,W0611

# Putil imports
import putil.exh
import putil.pcontracts
from putil.ptypes import (
    csv_col_filter,
    csv_row_filter,
    file_name,
    file_name_exists,
    non_negative_integer
)
from .csv_file import CsvFile
from .write import write


###
# Exception tracing initialization code
###
"""
[[[cog
import os, sys
sys.path.append(os.environ['TRACER_DIR'])
import trace_ex_pcsv_merge
exobj = trace_ex_pcsv_merge.trace_module(no_print=True)
]]]
[[[end]]]
"""


###
# Functions
###
@putil.pcontracts.contract(
    fname1='file_name_exists', fname2='file_name_exists',
    dfilter1='csv_data_filter', dfilter2='csv_data_filter',
    has_header1=bool, has_header2=bool,
    frow1='non_negative_integer', frow2='non_negative_integer',
    ofname='None|file_name', ocols='None|list(str)'
)
def merge(
    fname1, fname2,
    dfilter1=None, dfilter2=None,
    has_header1=True, has_header2=True,
    frow1=0, frow2=0,
    ofname=None, ocols=None):
    r"""
    Merges two comma-separated values files. Data columns from the second
    file are appended after data columns from the first file. Empty values in
    columns are used if the files have different number of rows

    :param fname1: Name of the first comma-separated values file, the file
                   whose columns appear first in the output file
    :type  fname1: :ref:`FileNameExists`

    :param fname2: Name of the second comma-separated values file, the file
                   whose columns appear last in the output file
    :type  fname2: :ref:`FileNameExists`

    :param dfilter1: Row and/or column filter for the first file. If None no
                     data filtering is done on the file
    :type  dfilter1: :ref:`CsvDataFilter` or None

    :param dfilter2: Row and/or column filter for the second file. If None no
                     data filtering is done on the file
    :type  dfilter2: :ref:`CsvDataFilter` or None

    :param has_header1: Flag that indicates whether the first comma-separated
                        values file has column headers in its first line (True)
                        or not (False)
    :type  has_header1: boolean

    :param has_header2: Flag that indicates whether the second comma-separated
                        values file has column headers in its first line (True)
                        or not (False)
    :type  has_header2: boolean

    :param frow1: First comma-separated values file first data row (starting
                  from 1). If 0 the row where data starts is auto-detected as
                  the first row that has a number (integer of float) in at
                  least one of its columns
    :type  frow1: :ref:`NonNegativeInteger`

    :param frow2: Second comma-separated values file first data row (starting
                  from 1). If 0 the row where data starts is auto-detected as
                  the first row that has a number (integer of float) in at
                  least one of its columns
    :type  frow2: :ref:`NonNegativeInteger`

    :param ofname: Name of the output comma-separated values file, the file
                   that will contain the data from the first and second files.
                   If None the first file is replaced "in place"
    :type  ofname: :ref:`FileName` or None

    :param ocols: Column names of the output comma-separated values file.
                  If None the column names in the first and second files are
                  used if **has_header1** and/or **has_header2** are True. The
                  column labels :code:`'Column [column_number]'` are used when
                  one of the two files does not have a header, where
                  :code:`[column_number]` is an integer representing the column
                  number (column 0 is the leftmost column). No header is used
                  if **has_header1** and **has_header2** are False
    :type  ocols: list or None

    .. [[[cog cog.out(exobj.get_sphinx_autodoc(raised=True)) ]]]
    .. Auto-generated exceptions documentation for putil.pcsv.merge.merge

    :raises:
     * OSError (File *[fname]* could not be found)

     * RuntimeError (Argument \`dfilter1\` is not valid)

     * RuntimeError (Argument \`dfilter2\` is not valid)

     * RuntimeError (Argument \`fname1\` is not valid)

     * RuntimeError (Argument \`fname2\` is not valid)

     * RuntimeError (Argument \`frow1\` is not valid)

     * RuntimeError (Argument \`frow2\` is not valid)

     * RuntimeError (Argument \`ocols\` is not valid)

     * RuntimeError (Argument \`ofname\` is not valid)

     * RuntimeError (Column headers are not unique in file *[fname]*)

     * RuntimeError (Combined columns in data files and output columns are
       different)

     * RuntimeError (File *[fname]* has no valid data)

     * RuntimeError (File *[fname]* is empty)

     * RuntimeError (Invalid column specification)

     * ValueError (Column *[column_identifier]* not found)

    .. [[[end]]]
    """
    # pylint: disable=R0913,R0914
    iomm_ex = putil.exh.addex(
        RuntimeError,
        'Combined columns in data files and output columns are different'
    )
    # Read and validate file 1
    obj1 = CsvFile(
        fname=fname1, dfilter=dfilter1, has_header=has_header1, frow=frow1
    )
    # Read and validate file 2
    obj2 = CsvFile(
        fname=fname2, dfilter=dfilter2, has_header=has_header2, frow=frow2
    )
    # Assign output data structure
    ofname = fname1 if ofname is None else ofname
    cfilter1 = obj1.header() if obj1.cfilter is None else obj1.cfilter
    cfilter2 = obj2.header() if obj1.cfilter is None else obj2.cfilter
    # Create new header
    cols1 = len(cfilter1)
    cols2 = len(cfilter2)
    if (ocols is None) and has_header1 and has_header2:
        ocols = [cfilter1+cfilter2]
    elif (ocols is None) and has_header1 and (not has_header2):
        ocols = [
            cfilter1+
            [
                'Column {0}'.format(item)
                for item in range(cols1+1, cols1+cols2+1)
            ]
        ]
    elif (ocols is None) and (not has_header1) and has_header2:
        ocols = [
            [
                'Column {0}'.format(item)
                for item in range(1, cols1+1)
            ]
            +cfilter2
        ]
    elif ocols is None:
        ocols = []
    else:
        iomm_ex(cols1+cols2 != len(ocols))
        ocols = [ocols]
    # Even out rows
    delta = obj1.rows(filtered=True)-obj2.rows(filtered=True)
    data1 = obj1.data(filtered=True)
    data2 = obj2.data(filtered=True)
    if delta > 0:
        row = [cols2*[None]]
        data2 += delta*row
    elif delta < 0:
        row = [cols1*[None]]
        data1 += abs(delta)*row
    data = ocols
    for item1, item2 in zip(data1, data2):
        data.append(item1+item2)
    write(
        fname=ofname,
        data=data,
        append=False
    )
