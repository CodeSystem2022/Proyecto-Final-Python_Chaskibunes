# replace.py
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
import trace_ex_pcsv_replace
exobj = trace_ex_pcsv_replace.trace_module(no_print=True)
]]]
[[[end]]]
"""


###
# Functions
###
@putil.pcontracts.contract(
    fname1='file_name_exists',
    fname2='file_name_exists',
    dfilter1='csv_data_filter',
    dfilter2='csv_data_filter',
    has_header1=bool,
    has_header2=bool,
    frow1='non_negative_integer',
    frow2='non_negative_integer',
    ofname='None|file_name',
    ocols='None|list(str)'
)
def replace(
    fname1, fname2,
    dfilter1, dfilter2,
    has_header1=True, has_header2=True,
    frow1=0, frow2=0,
    ofname=None, ocols=None):
    r"""
    Replaces data in one file with data from another file

    :param fname1: Name of the input comma-separated values file, the file
                   that contains the columns to be replaced
    :type  fname1: :ref:`FileNameExists`

    :param fname2: Name of the replacement comma-separated values file, the
                   file that contains the replacement data
    :type  fname2: :ref:`FileNameExists`

    :param dfilter1: Row and/or column filter for the input file
    :type  dfilter1: :ref:`CsvDataFilter`

    :param dfilter2: Row and/or column filter for the replacement file
    :type  dfilter2: :ref:`CsvDataFilter`

    :param has_header1: Flag that indicates whether the input comma-separated
                        values file has column headers in its first line (True)
                        or not (False)
    :type  has_header1: boolean

    :param has_header2: Flag that indicates whether the replacement
                        comma-separated values file has column headers in its
                        first line (True) or not (False)
    :type  has_header2: boolean

    :param frow1: Input comma-separated values file first data row (starting
                  from 1). If 0 the row where data starts is auto-detected as
                  the first row that has a number (integer of float) in at
                  least one of its columns
    :type  frow1: :ref:`NonNegativeInteger`

    :param frow2: Replacement comma-separated values file first data row
                  (starting from 1). If 0 the row where data starts is
                  auto-detected as the first row that has a number (integer of
                  float) in at least one of its columns
    :type  frow2: :ref:`NonNegativeInteger`

    :param ofname: Name of the output comma-separated values file, the file
                   that will contain the input file data but with some columns
                   replaced with data from the replacement file. If None the
                   input file is replaced "in place"
    :type  ofname: :ref:`FileName` or None

    :param ocols: Names of the replaced columns in the output comma-separated
                  values file. If None the column names in the input file are
                  used if **has_header1** is True, otherwise no header is used
    :type  ocols: list or None

    .. [[[cog cog.out(exobj.get_sphinx_autodoc(raised=True)) ]]]
    .. Auto-generated exceptions documentation for
    .. putil.pcsv.replace.replace

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

     * RuntimeError (Invalid column specification)

     * RuntimeError (Number of input and output columns are different)

     * RuntimeError (Number of input and replacement columns are
       different)

     * ValueError (Column *[column_identifier]* not found)

     * ValueError (Number of rows mismatch between input and replacement
       data)

    .. [[[end]]]
    """
    # pylint: disable=R0913,R0914
    irmm_ex = putil.exh.addex(
        RuntimeError, 'Number of input and replacement columns are different'
    )
    iomm_ex = putil.exh.addex(
        RuntimeError, 'Number of input and output columns are different'
    )
    # Read and validate input data
    iobj = CsvFile(
        fname=fname1, dfilter=dfilter1, has_header=has_header1, frow=frow1
    )
    # Read and validate replacement data
    robj = CsvFile(
        fname=fname2, dfilter=dfilter2, has_header=has_header2, frow=frow2
    )
    # Assign output data structure
    ofname = fname1 if ofname is None else ofname
    icfilter = iobj.header() if iobj.cfilter is None else iobj.cfilter
    rcfilter = robj.header() if robj.cfilter is None else robj.cfilter
    ocols = icfilter if ocols is None else ocols
    # Miscellaneous data validation
    irmm_ex(len(icfilter) != len(rcfilter))
    iomm_ex(len(icfilter) != len(ocols))
    # Replace data
    iobj.replace(rdata=robj.data(filtered=True), filtered=True)
    iheader_upper = [
        item.upper()
        if isinstance(item, str) else item
        for item in iobj.header()
    ]
    icfilter_index = [
        iheader_upper.index(item.upper() if isinstance(item, str) else item)
        for item in icfilter
    ]
    # Create new header
    orow = []
    if has_header1:
        for col_num, idata in enumerate(iobj.header()):
            orow.append(
                ocols[icfilter_index.index(col_num)]
                if col_num in icfilter_index else
                idata
            )
    # Write (new) file
    iobj.write(fname=ofname, header=orow if orow else False, append=False)
