# dsort.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,W0105,W0611

# Putil imports
import putil.pcontracts
from putil.ptypes import csv_col_sort, file_name_exists, non_negative_integer
from .csv_file import CsvFile
from .write import write


###
# Exception tracing initialization code
###
"""
[[[cog
import os, sys
sys.path.append(os.environ['TRACER_DIR'])
import trace_ex_pcsv_dsort
exobj = trace_ex_pcsv_dsort.trace_module(no_print=True)
]]]
[[[end]]]
"""


###
# Functions
###
@putil.pcontracts.contract(
    fname='file_name_exists',
    order='csv_col_sort',
    has_header=bool,
    frow='non_negative_integer',
    ofname='None|file_name',
)
def dsort(
    fname, order, has_header=True, frow=0, ofname=None):
    r"""
    Sorts file data

    :param fname: Name of the comma-separated values file to sort
    :type  fname: :ref:`FileNameExists`

    :param order: Sort order
    :type  order: :ref:`CsvColFilter`

    :param has_header: Flag that indicates whether the comma-separated
                       values file to sort has column headers in its first line
                       (True) or not (False)
    :type  has_header: boolean

    :param frow: First data row (starting from 1). If 0 the row where data
                 starts is auto-detected as the first row that has a number
                 (integer of float) in at least one of its columns
    :type  frow: :ref:`NonNegativeInteger`

    :param ofname: Name of the output comma-separated values file, the file
                   that will contain the sorted data. If None the sorting is
                   done "in place"
    :type  ofname: :ref:`FileName` or None

    .. [[[cog cog.out(exobj.get_sphinx_autodoc(raised=True)) ]]]
    .. Auto-generated exceptions documentation for putil.pcsv.dsort.dsort

    :raises:
     * OSError (File *[fname]* could not be found)

     * RuntimeError (Argument \`fname\` is not valid)

     * RuntimeError (Argument \`frow\` is not valid)

     * RuntimeError (Argument \`has_header\` is not valid)

     * RuntimeError (Argument \`ofname\` is not valid)

     * RuntimeError (Argument \`order\` is not valid)

     * RuntimeError (Column headers are not unique in file *[fname]*)

     * RuntimeError (File *[fname]* has no valid data)

     * RuntimeError (File *[fname]* is empty)

     * RuntimeError (Invalid column specification)

     * ValueError (Column *[column_identifier]* not found)

    .. [[[end]]]
    """
    ofname = fname if ofname is None else ofname
    obj = CsvFile(fname=fname, has_header=has_header, frow=frow)
    obj.dsort(order)
    obj.write(fname=ofname, header=has_header, append=False)
