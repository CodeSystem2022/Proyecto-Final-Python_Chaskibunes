# compat2.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,W0122,W0613


###
# Functions
###
def _ex_type_str(exobj):
    """ Returns a string corresponding to the exception type """
    return str(exobj).split('.')[-1][:-2]


def _get_ex_msg(obj):
    """ Get exception message """
    return obj.value.message if hasattr(obj, 'value') else obj.message


def _get_func_code(obj):
    """ Get funcion code """
    return obj.func_code


def _raise_exception(exception_object):
    """ Raise exception with short traceback """
    raise exception_object


def _read(fname):
    """ Read data from file """
    with open(fname, 'r') as frobj:
        return frobj.read()


def _readlines(fname):
    """ Read all lines from file """
    with open(fname, 'r') as fobj:
        return fobj.readlines()


def _rwtb(extype, exmsg, extb): # pragma: no cover
    """ Python 2 exception raising with traceback """
    exec('raise extype, exmsg, extb')


def _unicode_char(char):
    """ Returns true if character is Unicode (non-ASCII) character """
    try:
        char.encode('ascii')
    except UnicodeDecodeError:
        return True
    return False


# Largely from From https://stackoverflow.com/questions/956867/
# how-to-get-string-objects-instead-of-unicode-ones-from-json-in-python
# with Python 2.6 compatibility changes
def _unicode_to_ascii(obj):
    # pylint: disable=E0602
    if isinstance(obj, dict):
        return dict(
            [
                (_unicode_to_ascii(key), _unicode_to_ascii(value))
                for key, value in obj.items()
            ]
        )
    elif isinstance(obj, list):
        return [_unicode_to_ascii(element) for element in obj]
    elif isinstance(obj, unicode):
        return obj.encode('utf-8')
    else:
        return obj


def _write(fobj, data):
    """ Write data to file """
    fobj.write(data)
