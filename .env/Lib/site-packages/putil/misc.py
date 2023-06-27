# misc.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,E0611,R0903,W0611

# Standard library imports
from __future__ import print_function
import ast
import collections
import inspect
import os
import platform
import re
import sys
import tempfile
import time
import types
from fractions import Fraction
# PyPI imports
import decorator
import numpy
# Putil imports
import putil.eng

if os.environ.get('APPVEYOR', None):    # pragma: no cover
    tempfile.tempdir = os.environ['CITMP']


###
# Global constants
###
_OCTAL_ALPHABET = [
    chr(_NUM)
    if (_NUM >= 32) and (_NUM <= 126) else
    '\\'+str(oct(_NUM)).lstrip('0')
    for _NUM in range(0, 256)
]
_OCTAL_ALPHABET[0] = '\\0'   # Null character
_OCTAL_ALPHABET[7] = '\\a'   # Bell/alarm
_OCTAL_ALPHABET[8] = '\\b'   # Back space
_OCTAL_ALPHABET[9] = '\\t'   # Horizontal tab
_OCTAL_ALPHABET[10] = '\\n'  # Line feed
_OCTAL_ALPHABET[11] = '\\v'  # Vertical tab
_OCTAL_ALPHABET[12] = '\\f'  # Form feed
_OCTAL_ALPHABET[13] = '\\r'  # Carriage return


###
# Context managers
###
@decorator.contextmanager
def ignored(*exceptions):
    """
    Executes commands and selectively ignores exceptions
    (Inspired by `"Transforming Code into Beautiful, Idiomatic Python"
    <http://pyvideo.org/video/1780/
    transforming-code-into-beautiful-idiomatic-pytho>`_ talk at PyCon US
    2013 by Raymond Hettinger)

    :param exceptions: Exception type(s) to ignore
    :type  exceptions: Exception object, i.e. RuntimeError, OSError, etc.

    For example:

    .. =[=cog
    .. import docs.support.incfile
    .. docs.support.incfile.incfile('misc_example_1.py', cog.out)
    .. =]=
    .. code-block:: python

        # misc_example_1.py
        from __future__ import print_function
        import os, putil.misc

        def ignored_example():
            fname = 'somefile.tmp'
            open(fname, 'w').close()
            print('File {0} exists? {1}'.format(
                fname, os.path.isfile(fname)
            ))
            with putil.misc.ignored(OSError):
                os.remove(fname)
            print('File {0} exists? {1}'.format(
                fname, os.path.isfile(fname)
            ))
            with putil.misc.ignored(OSError):
                os.remove(fname)
            print('No exception trying to remove a file that does not exists')
            try:
                with putil.misc.ignored(RuntimeError):
                    os.remove(fname)
            except:
                print('Got an exception')

    .. =[=end=]=

    .. code-block:: python

        >>> import docs.support.misc_example_1
        >>> docs.support.misc_example_1.ignored_example()
        File somefile.tmp exists? True
        File somefile.tmp exists? False
        No exception trying to remove a file that does not exists
        Got an exception
    """
    try:
        yield
    except exceptions:
        pass


class Timer(object):
    r"""
    Profiles blocks of code by calculating elapsed time between the context
    manager entry and exit time points. Inspired by `Huy Nguyen's blog
    <http://www.huyng.com/posts/python-performance-analysis/>`_

    :param verbose: Flag that indicates whether the elapsed time is printed
                    upon exit (True) or not (False)
    :type  verbose: boolean

    :returns: :py:class:`putil.misc.Timer`

    :raises: RuntimeError (Argument \`verbose\` is not valid)

    For example:

    .. =[=cog
    .. import docs.support.incfile
    .. docs.support.incfile.incfile('misc_example_2.py', cog.out)
    .. =]=
    .. code-block:: python

        # misc_example_2.py
        from __future__ import print_function
        import putil.misc

        def timer(num_tries, fpointer):
            with putil.misc.Timer() as tobj:
                for _ in range(num_tries):
                    fpointer()
            print('Time per call: {0} seconds'.format(
                tobj.elapsed_time/(2.0*num_tries)
            ))

        def sample_func():
            count = 0
            for num in range(0, count):
                count += num

    .. =[=end=]=

    .. code-block:: python

        >>> from docs.support.misc_example_2 import *
        >>> timer(100, sample_func) #doctest: +ELLIPSIS
        Time per call: ... seconds
    """
    def __init__(self, verbose=False):
        if not isinstance(verbose, bool):
            raise RuntimeError('Argument `verbose` is not valid')
        self._tstart = None
        self._tstop = None
        self._elapsed_time = None
        self._verbose = verbose

    def __enter__(self):
        self._tstart = time.time()
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self._tstop = time.time()
        # time.time() returns time in seconds since the epoch
        self._elapsed_time = 1000.0*(self._tstop-self._tstart)
        if self._verbose:
            print('Elapsed time: {time}[msec]'.format(time=self._elapsed_time))
        if exc_type is not None:
            return False

    def _get_elapsed_time(self):
        return self._elapsed_time

    elapsed_time = property(_get_elapsed_time, doc='Elapsed time')
    """
    Returns elapsed time (in seconds) between context manager entry and exit
    time points

    :rtype: float
    """


class TmpFile(object):
    r"""
    Creates a temporary file and optionally sets up hooks for a function to
    write data to it

    :param fpointer: Pointer to a function that writes data to file.
                     If the argument is not None the function pointed to
                     receives exactly one argument, a file-like object
    :type  fpointer: function object or None

    :returns:   temporary file name

    :raises:    RuntimeError (Argument \`fpointer\` is not valid)

    .. warning:: The file name returned uses the forward slash (``/``) as
       the path separator regardless of the platform. This avoids
       `problems <https://pythonconquerstheuniverse.wordpress.com/2008/06/04/
       gotcha-%E2%80%94-backslashes-in-windows-filenames/>`_ with
       escape sequences or mistaken Unicode character encodings (``\\user``
       for example). Many functions in the os module of the standard library (
       `os.path.normpath()
       <https://docs.python.org/2/library/os.path.html#os.path.normpath>`_ and
       others) can change this path separator to the operating system path
       separator if needed

    For example:

    .. =[=cog
    .. import docs.support.incfile
    .. docs.support.incfile.incfile('misc_example_3.py', cog.out)
    .. =]=
    .. code-block:: python

        # misc_example_3.py
        from __future__ import print_function
        import putil.misc

        def write_data(file_handle):
            file_handle.write('Hello world!')

        def show_tmpfile():
            with putil.misc.TmpFile(write_data) as fname:
                with open(fname, 'r') as fobj:
                    lines = fobj.readlines()
            print('\n'.join(lines))

    .. =[=end=]=

    .. code-block:: python

        >>> from docs.support.misc_example_3 import *
        >>> show_tmpfile()
        Hello world!
    """
    # pylint: disable=E1129
    def __init__(self, fpointer=None):
        if (fpointer and
           (not isinstance(fpointer, types.FunctionType)) and
           (not isinstance(fpointer, types.LambdaType))):
            raise RuntimeError('Argument `fpointer` is not valid')
        self._fname = None
        self._fpointer = fpointer

    def __enter__(self):
        fdesc, fname = tempfile.mkstemp()
        # fdesc is an OS-level file descriptor, see problems if this
        # is not properly closed in this post:
        # https://www.logilab.org/blogentry/17873
        os.close(fdesc)
        if platform.system().lower() == 'windows':  # pragma: no cover
            fname = fname.replace(os.sep, '/')
        self._fname = fname
        if self._fpointer:
            with open(self._fname, 'w') as fobj:
                self._fpointer(fobj)
        return self._fname

    def __exit__(self, exc_type, exc_value, exc_tb):
        with ignored(OSError):
            os.remove(self._fname)
        if exc_type is not None:
            return False


###
# Functions
###
def binary_string_to_octal_string(text):
    r"""
    Returns a binary-packed string in octal representation aliasing typical
    codes to their escape sequences

    :param  text: Text to convert
    :type   text: string

    :rtype: string

    +------+-------+-----------------+
    | Code | Alias |   Description   |
    +======+=======+=================+
    |    0 |   \\0 | Null character  |
    +------+-------+-----------------+
    |    7 |   \\a | Bell / alarm    |
    +------+-------+-----------------+
    |    8 |   \\b | Backspace       |
    +------+-------+-----------------+
    |    9 |   \\t | Horizontal tab  |
    +------+-------+-----------------+
    |   10 |   \\n | Line feed       |
    +------+-------+-----------------+
    |   11 |   \\v | Vertical tab    |
    +------+-------+-----------------+
    |   12 |   \\f | Form feed       |
    +------+-------+-----------------+
    |   13 |   \\r | Carriage return |
    +------+-------+-----------------+

    For example:

        >>> import putil.misc, struct, sys
        >>> def py23struct(num):
        ...    if sys.hexversion < 0x03000000:
        ...        return struct.pack('h', num)
        ...    else:
        ...        return struct.pack('h', num).decode('ascii')
        >>> nums = range(1, 15)
        >>> putil.misc.binary_string_to_octal_string(
        ...     ''.join([py23struct(num) for num in nums])
        ... ).replace('o', '')  #doctest: +ELLIPSIS
        '\\1\\0\\2\\0\\3\\0\\4\\0\\5\\0\\6\\0\\a\\0\\b\\0\\t\\0\\...
    """
    # pylint: disable=C0103
    return ''.join([_OCTAL_ALPHABET[ord(char)] for char in text])


def char_to_decimal(text):
    """
    Converts a string to its decimal ASCII representation, with spaces between
    characters

    :param text: Text to convert
    :type  text: string

    :rtype: string

    For example:

        >>> import putil.misc
        >>> putil.misc.char_to_decimal('Hello world!')
        '72 101 108 108 111 32 119 111 114 108 100 33'
    """
    return ' '.join([str(ord(char)) for char in text])


def elapsed_time_string(start_time, stop_time):
    r"""
    Returns a formatted string with the elapsed time between two time points.
    The string includes years (365 days), months (30 days), days (24 hours),
    hours (60 minutes), minutes (60 seconds) and seconds. If both arguments
    are equal, the string returned is :code:`'None'`; otherwise, the string
    returned is [YY year[s], [MM month[s], [DD day[s], [HH hour[s],
    [MM minute[s] [and SS second[s\]\]\]\]\]\]. Any part (year[s], month[s],
    etc.) is omitted if the value of that part is null/zero

    :param start_time: Starting time point
    :type  start_time: `datetime <https://docs.python.org/2/library/
                       datetime.html#datetime-objects>`_

    :param stop_time: Ending time point
    :type  stop_time: `datetime`

    :rtype: string

    :raises: RuntimeError (Invalid time delta specification)

    For example:

        >>> import datetime, putil.misc
        >>> start_time = datetime.datetime(2014, 1, 1, 1, 10, 1)
        >>> stop_time = datetime.datetime(2015, 1, 3, 1, 10, 3)
        >>> putil.misc.elapsed_time_string(start_time, stop_time)
        '1 year, 2 days and 2 seconds'
    """
    if start_time > stop_time:
        raise RuntimeError('Invalid time delta specification')
    delta_time = stop_time-start_time
    # Python 2.6 datetime objects do not have total_seconds() method
    tot_seconds = int(
        (
            delta_time.microseconds+
            (delta_time.seconds+delta_time.days*24*3600)*10**6
        )
        /
        10**6
    )
    years, remainder = divmod(tot_seconds, 365*24*60*60)
    months, remainder = divmod(remainder, 30*24*60*60)
    days, remainder = divmod(remainder, 24*60*60)
    hours, remainder = divmod(remainder, 60*60)
    minutes, seconds = divmod(remainder, 60)
    token_iter = zip(
        [years, months, days, hours, minutes, seconds],
        ['year', 'month', 'day', 'hour', 'minute', 'second']
    )
    ret_list = [
        '{token} {token_name}{plural}'.format(
            token=num, token_name=desc, plural='s' if num > 1 else ''
        ) for num, desc in token_iter if num > 0
    ]
    if len(ret_list) == 0:
        return 'None'
    elif len(ret_list) == 1:
        return ret_list[0]
    elif len(ret_list) == 2:
        return ret_list[0]+' and '+ret_list[1]
    else:
        return (', '.join(ret_list[0:-1]))+' and '+ret_list[-1]


def flatten_list(lobj):
    """
    Recursively flattens a list

    :param lobj: List to flatten
    :type  lobj: list

    :rtype: list

    For example:

        >>> import putil.misc
        >>> putil.misc.flatten_list([1, [2, 3, [4, 5, 6]], 7])
        [1, 2, 3, 4, 5, 6, 7]
    """
    ret = []
    for item in lobj:
        if isinstance(item, list):
            for sub_item in flatten_list(item):
                ret.append(sub_item)
        else:
            ret.append(item)
    return ret


def gcd(vector):
    """
    Calculates the greatest common divisor (GCD) of a list of numbers or a
    Numpy vector of numbers. The computations are carried out with a precision
    of 1E-12 if the objects are not
    `fractions <https://docs.python.org/2/library/fractions.html>`_. When
    possible it is best to use the `fractions
    <https://docs.python.org/2/library/fractions.html>`_ data type with
    the numerator and denominator arguments when computing the GCD of
    floating point numbers.

    :param vector: Vector of numbers
    :type  vector: list of numbers or Numpy vector of numbers
    """
    if len(vector) == 0:
        return None
    if len(vector) == 1:
        return vector[0]
    if len(vector) == 2:
        return pgcd(vector[0], vector[1])
    current_gcd = pgcd(vector[0], vector[1])
    for element in vector[2:]:
        current_gcd = pgcd(current_gcd, element)
    return current_gcd


def isalpha(obj):
    """
    Tests if the argument is a string representing a number

    :param obj: Object
    :type  obj: any

    :rtype: boolean

    For example:

        >>> import putil.misc
        >>> putil.misc.isalpha('1.5')
        True
        >>> putil.misc.isalpha('1E-20')
        True
        >>> putil.misc.isalpha('1EA-20')
        False
    """
    try:
        float(obj)
        return True
    except ValueError:
        return False


def ishex(obj):
    """
    Tests if the argument is a string representing a valid hexadecimal digit

    :param obj: Object
    :type  obj: any

    :rtype: boolean
    """
    return (
        (isinstance(obj, str) and
        (len(obj) == 1) and
        (obj.upper() in '0123456789ABCDEF'))
    )


def isiterable(obj):
    """
    Tests if the argument is an iterable

    :param obj: Object
    :type  obj: any

    :rtype: boolean
    """
    try:
        iter(obj)
    except TypeError:
        return False
    else:
        return True


def isnumber(obj):
    """
    Tests if the argument is a number (complex, float or integer)

    :param obj: Object
    :type  obj: any

    :rtype: boolean
    """
    return (
        (((obj is not None) and
        (not isinstance(obj, bool)) and
        (isinstance(obj, int) or
        isinstance(obj, float) or
        isinstance(obj, complex))))
    )


def isreal(obj):
    """
    Tests if the argument is a real number (float or integer)

    :param obj: Object
    :type  obj: any

    :rtype: boolean
    """
    return (
        ((obj is not None) and
        (not isinstance(obj, bool)) and (
        isinstance(obj, int) or
        isinstance(obj, float)))
    )


def make_dir(fname):
    """
    Creates the directory of a fully qualified file name if it does not exist

    :param fname: File name
    :type  fname: string

    Equivalent to these Bash shell commands:

    .. code-block:: bash

        $ dir=$(dirname ${fname})
        $ mkdir -p ${dir}

    :param fname: Fully qualified file name
    :type  fname: string
    """
    file_path, fname = os.path.split(os.path.abspath(fname))
    if os.path.exists(file_path) is False:
        os.makedirs(file_path)


def normalize(value, series, offset=0):
    r"""
    Scales a value to the range defined by a series

    :param value: Value to normalize
    :type  value: number

    :param series: List of numbers that defines the normalization range
    :type  series: list

    :param offset: Normalization offset, i.e. the returned value will be in
                   the range [**offset**, 1.0]
    :type  offset: number

    :rtype: number

    :raises:
     * RuntimeError (Argument \`offset\` is not valid)

     * RuntimeError (Argument \`series\` is not valid)

     * RuntimeError (Argument \`value\` is not valid)

     * ValueError (Argument \`offset\` has to be in the [0.0, 1.0] range)

     * ValueError (Argument \`value\` has to be within the bounds of the
       argument \`series\`)

    For example::

        >>> import putil.misc
        >>> putil.misc.normalize(15, [10, 20])
        0.5
        >>> putil.misc.normalize(15, [10, 20], 0.5)
        0.75
    """
    if not isreal(value):
        raise RuntimeError('Argument `value` is not valid')
    if not isreal(offset):
        raise RuntimeError('Argument `offset` is not valid')
    try:
        assert isreal(min(series))
        assert isreal(max(series))
    except AssertionError:
        raise RuntimeError('Argument `series` is not valid')
    if (offset < 0) or (offset > 1):
        raise ValueError('Argument `offset` has to be in the [0.0, 1.0] range')
    if (value < min(series)) or (value > max(series)):
        raise ValueError(
            'Argument `value` has to be within the bounds of argument `series`'
        )
    return (
        offset+((1.0-offset)*
        ((value-float(min(series)))/(float(max(series))-float(min(series)))))
    )


def normalize_windows_fname(fname, _force=False):
    """
    Fix potential problems with a Microsoft Windows file name. Superfluous
    backslashes are removed and unintended escape sequences are converted
    to their equivalent (presumably correct and intended) representation,
    for example :code:`r'\\\\x07pps'` is transformed to
    :code:`r'\\\\\\\\apps'`. A file name is considered network shares if
    the file does not include a drive letter and they start with a double
    backslash (:code:`'\\\\\\\\'`)

    :param fname: File name
    :type  fname: string

    :rtype: string
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
    network_share = fname.startswith(r'\\')
    while tmp != ret:
        tmp, ret = ret, ret.replace(r'\\\\', r'\\')
    ret = ret.replace(r'\\\\', r'\\')
    # Put back network share if needed
    if network_share:
        ret = r'\\'+ret.lstrip(r'\\')
    return ret


def per(arga, argb, prec=10):
    r"""
    Calculates the percentage difference between two numbers or the
    element-wise percentage difference between two lists of numbers or Numpy
    vectors. If any of the numbers in the arguments is zero the value returned
    is 1E+20

    :param arga: First number, list of numbers or Numpy vector
    :type  arga: float, integer, list of floats or integers, or Numpy vector
                 of floats or integers

    :param argb: Second number, list of numbers or or Numpy vector
    :type  argb: float, integer, list of floats or integers, or Numpy vector
                 of floats or integers

    :param prec: Maximum length of the fractional part of the result
    :type  prec: integer

    :rtype: Float, list of floats or Numpy vector, depending on the arguments
     type

    :raises:
     * RuntimeError (Argument \`arga\` is not valid)

     * RuntimeError (Argument \`argb\` is not valid)

     * RuntimeError (Argument \`prec\` is not valid)

     * TypeError (Arguments are not of the same type)
    """
    # pylint: disable=E1101,R0204
    if not isinstance(prec, int):
        raise RuntimeError('Argument `prec` is not valid')
    arga_type = (
        1
        if isreal(arga) else
        (2 if isinstance(arga, numpy.ndarray) or isinstance(arga, list) else 0)
    )
    argb_type = (
        1
        if isreal(argb) else
        (2 if isinstance(argb, numpy.ndarray) or isinstance(argb, list) else 0)
    )
    if not arga_type:
        raise RuntimeError('Argument `arga` is not valid')
    if not argb_type:
        raise RuntimeError('Argument `argb` is not valid')
    if arga_type != argb_type:
        raise TypeError('Arguments are not of the same type')
    if arga_type == 1:
        arga = float(arga)
        argb = float(argb)
        num_max = max(arga, argb)
        num_min = min(arga, argb)
        return (
            0
            if arga == argb else
            (1e20 if (not num_min) else round((num_max/num_min)-1, prec))
        )
    else:
        arga = numpy.array(arga)
        argb = numpy.array(argb)
        num_max = numpy.maximum(arga, argb)
        num_min = numpy.minimum(arga, argb)
        # Numpy where() function seems to evaluate both arguments after the
        # condition, which prints an error to the console if any element
        # in num_min is zero
        lim_num = 1e+20*numpy.ones(len(num_max))
        safe_indexes = numpy.where(num_min != 0)
        lim_num[safe_indexes] = (num_max[safe_indexes]/num_min[safe_indexes])-1
        return numpy.round(numpy.where(arga == argb, 0, lim_num), prec)


def pcolor(text, color, indent=0):
    r"""
    Returns a string that once printed is colorized

    :param text: Text to colorize
    :type  text: string

    :param  color: Color to use, one of :code:`'black'`, :code:`'red'`,
                   :code:`'green'`, :code:`'yellow'`, :code:`'blue'`,
                   :code:`'magenta'`, :code:`'cyan'`, :code:`'white'` or
                   :code:`'none'` (case insensitive)
    :type   color: string

    :param indent: Number of spaces to prefix the output with
    :type  indent: integer

    :rtype: string

    :raises:
     * RuntimeError (Argument \`color\` is not valid)

     * RuntimeError (Argument \`indent\` is not valid)

     * RuntimeError (Argument \`text\` is not valid)

     * ValueError (Unknown color *[color]*)
    """
    esc_dict = {
        'black':30, 'red':31, 'green':32, 'yellow':33, 'blue':34, 'magenta':35,
        'cyan':36, 'white':37, 'none':-1
    }
    if not isinstance(text, str):
        raise RuntimeError('Argument `text` is not valid')
    if not isinstance(color, str):
        raise RuntimeError('Argument `color` is not valid')
    if not isinstance(indent, int):
        raise RuntimeError('Argument `indent` is not valid')
    color = color.lower()
    if color not in esc_dict:
        raise ValueError('Unknown color {color}'.format(color=color))
    if esc_dict[color] != -1:
        return (
            '\033[{color_code}m{indent}{text}\033[0m'.format(
                color_code=esc_dict[color], indent=' '*indent, text=text
            )
        )
    return '{indent}{text}'.format(indent=' '*indent, text=text)


def pgcd(numa, numb):
    """
    Calculate the greatest common divisor (GCD) of two numbers

    :param numa: First number
    :type  numa: number

    :param numb: Second number
    :type  numb: number

    :rtype: number

    For example:

        >>> import putil.misc, fractions
        >>> putil.misc.pgcd(10, 15)
        5
        >>> str(putil.misc.pgcd(0.05, 0.02))
        '0.01'
        >>> str(putil.misc.pgcd(5/3.0, 2/3.0))[:6]
        '0.3333'
        >>> putil.misc.pgcd(
        ...     fractions.Fraction(str(5/3.0)),
        ...     fractions.Fraction(str(2/3.0))
        ... )
        Fraction(1, 3)
        >>> putil.misc.pgcd(
        ...     fractions.Fraction(5, 3),
        ...     fractions.Fraction(2, 3)
        ... )
        Fraction(1, 3)
    """
    int_args = isinstance(numa, int) and isinstance(numb, int)
    fraction_args = isinstance(numa, Fraction) and isinstance(numb, Fraction)
    # Limit floating numbers to a "sane" fractional part resolution
    if (not int_args) and (not fraction_args):
        numa, numb = (
            Fraction(putil.eng.no_exp(numa)).limit_denominator(),
            Fraction(putil.eng.no_exp(numb)).limit_denominator()
        )
    while numb:
        numa, numb = (
            numb,
            (numa % numb if int_args else (numa % numb).limit_denominator())
        )
    return int(numa) if int_args else (numa if fraction_args else float(numa))


def quote_str(obj):
    """
    Adds extra quotes to a string. If the argument is not a string it is
    returned unmodified

    :param obj: Object
    :type  obj: any

    :rtype: Same as argument

    For example:

        >>> import putil.misc
        >>> putil.misc.quote_str(5)
        5
        >>> putil.misc.quote_str('Hello!')
        '"Hello!"'
        >>> putil.misc.quote_str('He said "hello!"')
        '\\'He said "hello!"\\''
    """
    if not isinstance(obj, str):
        return obj
    else:
        return (
            "'{obj}'".format(obj=obj)
            if '"' in obj else
            '"{obj}"'.format(obj=obj)
        )


def strframe(obj, extended=False):
    """
    Returns a string with a frame record (typically an item in a list generated
    by `inspect.stack()
    <https://docs.python.org/2/library/inspect.html#inspect.stack>`_) pretty
    printed

    :param obj: Frame record
    :type  obj: tuple

    :param extended: Flag that indicates whether contents of the frame object
                     are printed (True) or not (False)
    :type  extended: boolean

    :rtype:     string
    """
    # Stack frame -> (frame object [0], filename [1], line number of current
    # line [2], function name [3], list of lines of context from source
    # code [4], index of current line within list [5])
    ret = list()
    ret.append(
        pcolor('Frame object ID: {0}'.format(hex(id(obj[0]))), 'yellow')
    )
    ret.append('File name......: {0}'.format(obj[1]))
    ret.append('Line number....: {0}'.format(obj[2]))
    ret.append('Function name..: {0}'.format(obj[3]))
    ret.append('Context........: {0}'.format(obj[4]))
    ret.append('Index..........: {0}'.format(obj[5]))
    if extended:
        ret.append('f_back ID......: {0}'.format(hex(id(obj[0].f_back))))
        ret.append('f_builtins.....: {0}'.format(obj[0].f_builtins))
        ret.append('f_code.........: {0}'.format(obj[0].f_code))
        ret.append('f_globals......: {0}'.format(obj[0].f_globals))
        ret.append('f_lasti........: {0}'.format(obj[0].f_lasti))
        ret.append('f_lineno.......: {0}'.format(obj[0].f_lineno))
        ret.append('f_locals.......: {0}'.format(obj[0].f_locals))
        if hasattr(obj[0], 'f_restricted'): # pragma: no cover
            ret.append('f_restricted...: {0}'.format(obj[0].f_restricted))
        ret.append('f_trace........: {0}'.format(obj[0].f_trace))
    return '\n'.join(ret)


###
# Classes
###
# Inspired from https://stackoverflow.com/
# questions/3387691/python-how-to-perfectly-override-a-dict
class CiDict(collections.MutableMapping):
    def __init__(self, *args, **kwargs):
        self._store = dict()
        self.update(dict(*args, **kwargs))

    def __getitem__(self, key):
        return self._store[self.__keytransform__(key)]

    def __setitem__(self, key, value):
        self._store[self.__keytransform__(key)] = value

    def __delitem__(self, key):
        del self._store[self.__keytransform__(key)]

    def __iter__(self):
        return iter(self._store)

    def __len__(self):
        return len(self._store)

    def __keytransform__(self, key):
        # pylint: disable=R0201
        return key.lower() if isinstance(key, str) else key
