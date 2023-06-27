# ptypes.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

# Standard library imports
import os
import platform
import inspect
# PyPI imports
import numpy
# Putil imports
import putil.pcontracts


###
# Global variables
###
_SUFFIX_TUPLE = (
    'y', 'z', 'a', 'f', 'p', 'n', 'u', 'm',
    ' ',
    'k', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y'
)


###
# Functions
###
def _check_csv_col_filter(obj):
    # pylint: disable=R0916
    if (not isinstance(obj, bool)) and ((obj is None) or
       isinstance(obj, str) or isinstance(obj, int) or
       (isinstance(obj, list) and (len(obj) > 0) and
       all([(isinstance(item, str) or isinstance(item, int)) and
       (not isinstance(item, bool)) for item in obj]))):
        return False
    return True


def _check_csv_row_filter(obj):
    # pylint: disable=R0911
    if obj is None:
        return 0
    if not isinstance(obj, dict):
        return 1
    if not len(obj):
        return 2
    if any(
            [
                not (isinstance(col_name, str) or isinstance(col_name, int))
                for col_name in obj.keys()
            ]
    ):
        return 1
    for col_name, col_value in obj.items(): # pragma: no branch
        if ((not isinstance(obj[col_name], list)) and
           (not _isnumber(obj[col_name])) and
           (not isinstance(obj[col_name], str))):
            return 1
        if isinstance(col_value, list):
            for element in col_value:   # pragma: no branch
                if ((not _isnumber(element)) and
                   (not isinstance(element, str))):
                    return 1
    return 0


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


def _check_real_numpy_vector(obj):
    if (isinstance(obj, numpy.ndarray) and
       (len(obj.shape) == 1) and (obj.shape[0] > 0) and
       ((obj.dtype.type == numpy.array([0]).dtype.type) or
       (obj.dtype.type == numpy.array([0.0]).dtype.type))):
        return False
    return True


def _homogenize_data_filter(dfilter):
    """
    Make data filter definition consistent, create a
    tuple where first element is the row filter and
    the second element is the column filter
    """
    if (dfilter is None) or (dfilter == (None, None)) or (dfilter == (None, )):
        dfilter = (None, None)
    if (isinstance(dfilter, bool) or (not any(
            [
                isinstance(dfilter, item) for item in
                [tuple, dict, str, int, list]
            ]))):
        dfilter = (2.0, 2.0)
    if isinstance(dfilter, tuple) and (len(dfilter) == 1):
        dfilter = (dfilter[0], None)
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


def _isnumber(obj):
    """
    Function copied from putil.misc module to avoid
    import loops
    """
    return (
        (((obj is not None) and
        (not isinstance(obj, bool)) and
        (isinstance(obj, int) or
        isinstance(obj, float) or
        isinstance(obj, complex))))
    )


def _normalize_windows_fname(fname, _force=False):  # pragma: no cover
    """
    Function copied from putil.misc module to avoid
    import loops
    """
    if ((platform.system().lower() != 'windows')
       and (not _force)):   # pragma: no cover
        return fname
    # Replace unintended escape sequences that could be in
    # the file name, like "C:\appdata"
    rchars = {
        '\x07': r'\\a',
        '\x08': r'\\b',
        '\x0C': r'\\f',
        '\x0A': r'\\n',
        '\x0D': r'\\r',
        '\x09': r'\\t',
        '\x0B': r'\\v',
    }
    ret = ''
    for char in os.path.normpath(fname):
        ret = ret+rchars.get(char, char)
    # Remove superfluous double backslashes
    network_share = False
    tmp = None
    while tmp != ret:
        tmp, ret = ret, ret.replace('\\\\', '\\')
        if ret.startswith(r'\\') and (len(ret) > 2) and (ret[2] != r'\\'):
            network_share = True
    ret = ret.replace('\\\\', '\\')
    # Put back network share if needed
    if network_share:
        ret = r'\\'+ret.lstrip(r'\\')
    return ret


@putil.pcontracts.new_contract(
    argument_invalid='Argument `*[argument_name]*` is not valid',
    argument_bad_choice=(
        ValueError,
        (
            "Argument `*[argument_name]*` is not one of 'binary', 'Blues', "
            "'BuGn', 'BuPu', 'GnBu', 'Greens', 'Greys', 'Oranges', 'OrRd', "
            "'PuBu', 'PuBuGn', 'PuRd', 'Purples', 'RdPu', 'Reds', 'YlGn', "
            "'YlGnBu', 'YlOrBr' or 'YlOrRd' (case insensitive)"
        )
    )
)
def color_space_option(obj):
    r"""
    Validates if an object is a ColorSpaceOption pseudo-type object

    :param obj: Object
    :type  obj: any

    :raises:
     * RuntimeError (Argument \`*[argument_name]*\` is not valid). The token
       \*[argument_name]\* is replaced by the name of the argument the contract
       is attached to

     * RuntimeError (Argument \`*[argument_name]*\` is not one of 'binary',
       'Blues', 'BuGn', 'BuPu', 'GnBu', 'Greens', 'Greys', 'Oranges', 'OrRd',
       'PuBu', 'PuBuGn', 'PuRd', 'Purples', 'RdPu', 'Reds', 'YlGn', 'YlGnBu',
       'YlOrBr' or 'YlOrRd). The token \*[argument_name]\* is replaced by the
       name of the argument the contract is attached to

    :rtype: None
    """
    exdesc = putil.pcontracts.get_exdesc()
    if (obj is not None) and (not isinstance(obj, str)):
        raise ValueError(exdesc['argument_invalid'])
    if (obj is None) or (obj and any([
            item.lower() == obj.lower()
            for item in [
                    'binary', 'Blues', 'BuGn', 'BuPu', 'GnBu', 'Greens',
                    'Greys', 'Oranges', 'OrRd', 'PuBu', 'PuBuGn', 'PuRd',
                    'Purples', 'RdPu', 'Reds', 'YlGn', 'YlGnBu',
                    'YlOrBr', 'YlOrRd'
            ]
    ])):
        return None
    raise ValueError(exdesc['argument_bad_choice'])


@putil.pcontracts.new_contract()
def csv_col_filter(obj):
    r"""
    Validates if an object is a CsvColFilter pseudo-type object

    :param obj: Object
    :type  obj: any

    :raises:
     * RuntimeError (Argument \`*[argument_name]*\` is not valid). The token
       \*[argument_name]\* is replaced by the *name* of the argument the
       contract is attached to

    :rtype: None
    """
    if _check_csv_col_filter(obj):
        raise ValueError(putil.pcontracts.get_exdesc())


@putil.pcontracts.new_contract()
def csv_col_sort(obj):
    r"""
    Validates if an object is a CsvColSort pseudo-type object

    :param obj: Object
    :type  obj: any

    :raises:
     * RuntimeError (Argument \`*[argument_name]*\` is not valid). The token
       \*[argument_name]\* is replaced by the *name* of the argument the
       contract is attached to

    :rtype: None
    """
    exdesc = putil.pcontracts.get_exdesc()
    obj = obj if isinstance(obj, list) else [obj]
    if len(obj) == 0:
        raise ValueError(exdesc)
    for item in obj:
        # Weed out items not having the right basic types
        if isinstance(item, bool) or ((not isinstance(item, str))
           and (not isinstance(item, int)) and (not isinstance(item, dict))):
            raise ValueError(exdesc)
        # If it is a dictionary, the key has to be a valid column name and the
        # sort order has to be either 'A' (for ascending) or 'D' (for
        # descending), case insensitive
        if isinstance(item, dict):
            keys = list(item.keys())
            if (len(keys) > 1) or ((len(keys) == 1) and
               ((not isinstance(keys[0], int)) and
               (not isinstance(keys[0], str)))):
                raise ValueError(exdesc)
            value = item[keys[0]]
            if value not in ['A', 'D', 'a', 'd']:
                raise ValueError(exdesc)


@putil.pcontracts.new_contract()
def csv_data_filter(obj):
    r"""
    Validates if an object is a CsvDataFilter pseudo-type object

    :param obj: Object
    :type  obj: any

    :raises:
     * RuntimeError (Argument \`*[argument_name]*\` is not valid). The token
       \*[argument_name]\* is replaced by the *name* of the argument the
       contract is attached to

    :rtype: None
    """
    if isinstance(obj, tuple) and len(obj) > 2:
        raise ValueError(putil.pcontracts.get_exdesc())
    else:
        obj = _homogenize_data_filter(obj)
    row_value = _check_csv_row_filter(obj[0])
    col_value = _check_csv_col_filter(obj[1])
    if col_value or (row_value != 0):
        raise ValueError(putil.pcontracts.get_exdesc())


@putil.pcontracts.new_contract()
def csv_filtered(obj):
    r"""
    Validates if an object is a CsvFilter pseudo-type object

    :param obj: Object
    :type  obj: any

    :raises:
     * RuntimeError (Argument \`*[argument_name]*\` is not valid). The token
       \*[argument_name]\* is replaced by the *name* of the argument the
       contract is attached to

    :rtype: None
    """
    if obj in [True, False, 'B', 'b', 'C', 'c', 'R', 'r', 'N', 'n']:
        return None
    raise ValueError(putil.pcontracts.get_exdesc())


@putil.pcontracts.new_contract(
    argument_invalid='Argument `*[argument_name]*` is not valid',
    argument_empty=(ValueError, 'Argument `*[argument_name]*` is empty')
)
def csv_row_filter(obj):
    r"""
    Validates if an object is a CsvRowFilter pseudo-type object

    :param obj: Object
    :type  obj: any

    :raises:
     * RuntimeError (Argument \`*[argument_name]*\` is not valid). The token
       \*[argument_name]\* is replaced by the *name* of the argument the
       contract is attached to

     * ValueError (Argument \`*[argument_name]*\` is empty). The token
       \*[argument_name]\* is replaced by the *name* of the argument the
       contract is attached to

    :rtype: None
    """
    exdesc = putil.pcontracts.get_exdesc()
    ecode = _check_csv_row_filter(obj)
    if ecode == 1:
        raise ValueError(exdesc['argument_invalid'])
    elif ecode == 2:
        raise ValueError(exdesc['argument_empty'])


@putil.pcontracts.new_contract()
def engineering_notation_number(obj):
    r"""
    Validates if an object is an EngineeringNotationNumber pseudo-type object

    :param obj: Object
    :type  obj: any

    :raises: RuntimeError (Argument \`*[argument_name]*\` is not valid). The
     token \*[argument_name]\* is replaced by the name of the argument the
     contract is attached to

    :rtype: None
    """
    try:
        obj = obj.rstrip()
        float(obj[:-1] if obj[-1] in _SUFFIX_TUPLE else obj)
        return None
    except (AttributeError, IndexError, ValueError):
        # AttributeError: obj.rstrip(), object could not be a string
        # IndexError: obj[-1], when an empty string
        # ValueError: float(), when not a string representing a number
        raise ValueError(putil.pcontracts.get_exdesc())


@putil.pcontracts.new_contract()
def engineering_notation_suffix(obj):
    r"""
    Validates if an object is an EngineeringNotationSuffix pseudo-type object

    :param obj: Object
    :type  obj: any

    :raises: RuntimeError (Argument \`*[argument_name]*\` is not valid). The
     token \*[argument_name]\* is replaced by the *name* of the argument the
     contract is attached to

    :rtype: None
    """
    try:
        assert obj in _SUFFIX_TUPLE
    except AssertionError:
        raise ValueError(putil.pcontracts.get_exdesc())


@putil.pcontracts.new_contract()
def file_name(obj):
    r"""
    Validates if an object is a legal name for a file
    (i.e. does not have extraneous characters, etc.)

    :param obj: Object
    :type  obj: any

    :raises: RuntimeError (Argument \`*[argument_name]*\` is not
     valid). The token \*[argument_name]\* is replaced by the name
     of the argument the contract is attached to

    :rtype: None
    """
    msg = putil.pcontracts.get_exdesc()
    # Check that argument is a string
    if ((not isinstance(obj, str) or
       (isinstance(obj, str) and ('\0' in obj)))):
        raise ValueError(msg)
    # If file exists, argument is a valid file name, otherwise test
    # if file can be created. User may not have permission to
    # write file, but call to os.access should not fail if the file
    # name is correct
    try:
        if not os.path.exists(obj):
            os.access(obj, os.W_OK)
    except (TypeError, ValueError): # pragma: no cover
        raise ValueError(msg)


@putil.pcontracts.new_contract(
    argument_invalid='Argument `*[argument_name]*` is not valid',
    file_not_found=(OSError, 'File *[fname]* could not be found')
)
def file_name_exists(obj):
    r"""
    Validates if an object is a legal name for a file
    (i.e. does not have extraneous characters, etc.) *and* that the
    file exists

    :param obj: Object
    :type  obj: any

    :raises:
     * OSError (File *[fname]* could not be found). The
       token \*[fname]\* is replaced by the *value* of the
       argument the contract is attached to

     * RuntimeError (Argument \`*[argument_name]*\` is not valid).
       The token \*[argument_name]\* is replaced by the name of
       the argument the contract is attached to

    :rtype: None
    """
    exdesc = putil.pcontracts.get_exdesc()
    msg = exdesc['argument_invalid']
    # Check that argument is a string
    if ((not isinstance(obj, str) or
       (isinstance(obj, str) and ('\0' in obj)))):
        raise ValueError(msg)
    # Check that file name is valid
    try:
        os.path.exists(obj)
    except (TypeError, ValueError): # pragma: no cover
        raise ValueError(msg)
    # Check that file exists
    obj = _normalize_windows_fname(obj)
    if not os.path.exists(obj):
        msg = exdesc['file_not_found']
        raise ValueError(msg)


@putil.pcontracts.new_contract()
def function(obj):
    r"""
    Validates if an object is a function pointer or :code:`None`

    :param obj: Object
    :type  obj: any

    :raises: RuntimeError (Argument \`*[argument_name]*\` is not valid). The
     token \*[argument_name]\* is replaced by the name of the argument the
     contract is attached to

    :rtype: None
    """
    if (obj is None) or inspect.isfunction(obj):
        return None
    raise ValueError(putil.pcontracts.get_exdesc())


@putil.pcontracts.new_contract()
def increasing_real_numpy_vector(obj):
    r"""
    Validates if an object is IncreasingRealNumpyVector pseudo-type object

    :param obj: Object
    :type  obj: any

    :raises: RuntimeError (Argument \`*[argument_name]*\` is not valid). The
     token \*[argument_name]\* is replaced by the name of the argument the
     contract is attached to

    :rtype: None
    """
    if _check_increasing_real_numpy_vector(obj):
        raise ValueError(putil.pcontracts.get_exdesc())


@putil.pcontracts.new_contract(
    argument_invalid='Argument `*[argument_name]*` is not valid',
    argument_bad_choice=(
        ValueError,
        (
            "Argument `*[argument_name]*` is not one of ['STRAIGHT', 'STEP', "
            "'CUBIC', 'LINREG'] (case insensitive)"
        )
    )
)
def interpolation_option(obj):
    r"""
    Validates if an object is an InterpolationOption pseudo-type object

    :param obj: Object
    :type  obj: any

    :raises:
     * RuntimeError (Argument \`*[argument_name]*\` is not valid). The token
       \*[argument_name]\* is replaced by the name of the argument the contract
       is attached to

     * RuntimeError (Argument \`*[argument_name]*\` is not one of ['STRAIGHT',
       'STEP', 'CUBIC', 'LINREG'] (case insensitive)). The token
       \*[argument_name]\* is replaced by the name of the argument
       the contract is attached to

    :rtype: None
    """
    exdesc = putil.pcontracts.get_exdesc()
    if (obj is not None) and (not isinstance(obj, str)):
        raise ValueError(exdesc['argument_invalid'])
    if ((obj is None) or
       (obj and any([
           item.lower() == obj.lower()
           for item in ['STRAIGHT', 'STEP', 'CUBIC', 'LINREG']]))):
        return None
    raise ValueError(exdesc['argument_bad_choice'])


@putil.pcontracts.new_contract(
    argument_invalid='Argument `*[argument_name]*` is not valid',
    argument_bad_choice=(
        ValueError,
        "Argument `*[argument_name]*` is not one of ['-', '--', '-.', ':']"
    )
)
def line_style_option(obj):
    r"""
    Validates if an object is a LineStyleOption pseudo-type object

    :param obj: Object
    :type  obj: any

    :raises:
     * RuntimeError (Argument \`*[argument_name]*\` is not valid). The token
       \*[argument_name]\* is replaced by the name of the argument the contract
       is attached to

     * RuntimeError (Argument \`*[argument_name]*\` is not one of ['-', '--',
       '-.', ':']). The token \*[argument_name]\* is replaced by the name of
       the argument the contract is attached to

    :rtype: None
    """
    exdesc = putil.pcontracts.get_exdesc()
    if (obj is not None) and (not isinstance(obj, str)):
        raise ValueError(exdesc['argument_invalid'])
    if obj in [None, '-', '--', '-.', ':']:
        return None
    raise ValueError(exdesc['argument_bad_choice'])


@putil.pcontracts.new_contract()
def non_negative_integer(obj):
    r"""
    Validates if an object is a non-negative (zero or positive) integer

    :param obj: Object
    :type  obj: any

    :raises: RuntimeError (Argument \`*[argument_name]*\` is not valid). The
     token \*[argument_name]\* is replaced by the *name* of the argument the
     contract is attached to

    :rtype: None
    """
    if isinstance(obj, int) and (not isinstance(obj, bool)) and (obj >= 0):
        return None
    raise ValueError(putil.pcontracts.get_exdesc())


@putil.pcontracts.new_contract()
def offset_range(obj):
    r"""
    Validates if an object is a number in the [0, 1] range

    :param obj: Object
    :type  obj: any

    :raises: RuntimeError (Argument \`*[argument_name]*\` is not valid). The
     token \*[argument_name]\* is replaced by the name of the argument the
     contract is attached to

    :rtype: None
    """
    if ((isinstance(obj, int) or isinstance(obj, float)) and
       (not isinstance(obj, bool)) and (obj >= 0) and (obj <= 1)):
        return None
    raise ValueError(putil.pcontracts.get_exdesc())


@putil.pcontracts.new_contract()
def positive_real_num(obj):
    r"""
    Validates if an object is a positive integer, positive float
    or :code:`None`

    :param obj: Object
    :type  obj: any

    :raises: RuntimeError (Argument \`*[argument_name]*\` is not valid). The
     token \*[argument_name]\* is replaced by the name of the argument the
     contract is attached to

    :rtype: None
    """
    if ((obj is None) or ((isinstance(obj, int) or
       isinstance(obj, float)) and (obj > 0) and (not isinstance(obj, bool)))):
        return None
    raise ValueError(putil.pcontracts.get_exdesc())


@putil.pcontracts.new_contract()
def real_num(obj):
    r"""
    Validates if an object is an integer, float or :code:`None`

    :param obj: Object
    :type  obj: any

    :raises: RuntimeError (Argument \`*[argument_name]*\` is not valid). The
     token \*[argument_name]\* is replaced by the name of the argument the
     contract is attached to

    :rtype: None
    """
    if ((obj is None) or
       ((isinstance(obj, int) or isinstance(obj, float)) and
       (not isinstance(obj, bool)))):
        return None
    raise ValueError(putil.pcontracts.get_exdesc())


@putil.pcontracts.new_contract()
def real_numpy_vector(obj):
    r"""
    Validates if an object is a RealNumpyVector pseudo-type object

    :param obj: Object
    :type  obj: any

    :raises: RuntimeError (Argument \`*[argument_name]*\` is not valid). The
     token \*[argument_name]\* is replaced by the name of the argument the
     contract is attached to

    :rtype: None
    """
    if _check_real_numpy_vector(obj):
        raise ValueError(putil.pcontracts.get_exdesc())
