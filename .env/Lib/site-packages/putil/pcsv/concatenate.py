# concatenate.py
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
import trace_ex_pcsv_concatenate
exobj = trace_ex_pcsv_concatenate.trace_module(no_print=True)
]]]
[[[end]]]
"""


###
# Functions
###
_C = lambda *x: all([item is not None for item in x])

@putil.pcontracts.contract(
    fname1='file_name_exists', fname2='file_name_exists',
    dfilter1='csv_data_filter', dfilter2='csv_data_filter',
    has_header1=bool, has_header2=bool,
    frow1='non_negative_integer', frow2='non_negative_integer',
    ofname='None|file_name', ocols='None|list(str)'
)
def concatenate(
    fname1, fname2,
    dfilter1=None, dfilter2=None,
    has_header1=True, has_header2=True,
    frow1=0, frow2=0,
    ofname=None, ocols=None):
    r"""
    Concatenates two comma-separated values file. Data rows from the second
    file are appended at the end of the data rows from the first file

    :param fname1: Name of the first comma-separated values file, the file
                   whose data appears first in the output file
    :type  fname1: :ref:`FileNameExists`

    :param fname2: Name of the second comma-separated values file, the file
                   whose data appears last in the output file
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
                  If None the column names in the first file are used if
                  **has_header1** is True or the column names in the second
                  files are used if **has_header1** is False and
                  **has_header2** is True, otherwise no header is used
    :type  ocols: list or None

    .. [[[cog cog.out(exobj.get_sphinx_autodoc(raised=True)) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.pcsv.concatenate.concatenate

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

     * RuntimeError (File *[fname]* has no valid data)

     * RuntimeError (File *[fname]* is empty)

     * RuntimeError (Files have different number of columns)

     * RuntimeError (Invalid column specification)

     * RuntimeError (Number of columns in data files and output columns are
       different)

     * ValueError (Column *[column_identifier]* not found)

    .. [[[end]]]
    """
    # pylint: disable=R0913,R0914
    iro = putil.exh.addex(
        RuntimeError, 'Files have different number of columns'
    )
    iom = putil.exh.addex(
        RuntimeError,
        'Number of columns in data files and output columns are different'
    )
    # Read and validate file 1
    obj1 = CsvFile(
        fname=fname1, dfilter=dfilter1, has_header=has_header1, frow=frow1)
    # Read and validate file 2
    obj2 = CsvFile(
        fname=fname2, dfilter=dfilter2, has_header=has_header2, frow=frow2)
    # Assign output data structure
    ofname = fname1 if ofname is None else ofname
    # Create new header
    if (ocols is None) and has_header1:
        ocols = [obj1.header()] if obj1.cfilter is None else [obj1.cfilter]
    elif (ocols is None) and has_header2:
        ocols = [obj2.header()] if obj2.cfilter is None else [obj2.cfilter]
    elif ocols is None:
        ocols = []
    else:
        iom((obj1.cfilter is not None) and (len(obj1.cfilter) != len(ocols)))
        ocols = [ocols]
    # Miscellaneous data validation
    iro(
        _C(obj1.cfilter, obj2.cfilter) and
        (len(obj1.cfilter) != len(obj2.cfilter))
    )
    # Write final output
    data = ocols+obj1.data(filtered=True)+obj2.data(filtered=True)
    write(fname=ofname, data=data, append=False)
