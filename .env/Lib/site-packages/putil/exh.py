# exh.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0411,E0012,E0611,E1101,E1103,F0401
# pylint: disable=R0201,R0912,R0913,R0914,R0915,W0122,W0212,W0613,W0631

# Standard library imports
import copy
import imp
import inspect
import itertools
import os
import sys
if sys.hexversion < 0x03000000: # pragma: no cover
    import __builtin__
else: # pragma: no cover
    import builtins as __builtin__
# PyPI imports
import decorator
# Putil imports
if sys.hexversion < 0x03000000: # pragma: no cover
    from putil.compat2 import _ex_type_str, _get_ex_msg, _get_func_code, _rwtb
else:   # pragma: no cover
    from putil.compat3 import _ex_type_str, _get_ex_msg, _get_func_code, _rwtb
import putil.pinspect


###
# Global variables
###
_BREAK_LIST = ['_pytest']
_INVALID_MODULES_LIST = [
    os.path.join('putil', 'exh.py'),
    os.path.join('putil', 'exdoc.py')
]

###
# Functions
###
def _build_exclusion_list(exclude):
    """
    Build list of file names corresponding to modules to exclude
    from exception handling
    """
    mod_files = []
    if exclude:
        for mod in exclude:
            mdir = None
            mod_file = None
            for token in mod.split('.'):
                try:
                    mfile, mdir, _ = imp.find_module(token, mdir and [mdir])
                    if mfile:
                        mod_file = mfile.name
                        mfile.close()
                except ImportError:
                    msg = ('Source for module {mod_name} could not be found')
                    raise ValueError(msg.format(mod_name=mod))
            if mod_file:
                mod_files.append(mod_file.replace('.pyc', '.py'))
    return mod_files


def _invalid_frame(fobj):
    """ Selects valid stack frame to process """
    fin = fobj.f_code.co_filename
    invalid_module = any(
        [fin.endswith(item) for item in _INVALID_MODULES_LIST]
    )
    return invalid_module or (not os.path.isfile(fin))


def _isiterable(obj):
    """
    Copied from putil.misc module, not included to avoid recursive inclusion
    of putil.pcontracts module
    """
    try:
        iter(obj)
    except TypeError:
        return False
    else:
        return True


def _merge_cdicts(self, clut, exdict, separator):
    """ Merge exception dictionaries from two objects """
    if not self._full_cname:
        return
    # Find all callables that are not in self exceptions dictionary
    # and create new tokens for them
    repl_dict = {}
    for key, value in clut.items():
        otoken = self._clut.get(key, None)
        if not otoken:
            otoken = str(len(self._clut))
            self._clut[key] = otoken
        repl_dict[value] = otoken
    # Update other dictionaries to the mapping to self
    # exceptions dictionary
    for fdict in exdict.values():
        for entry in fdict.values():
            olist = []
            for item in entry['function']:
                if item is None:
                    # Callable name is None when callable is
                    # part of exclude list
                    olist.append(None)
                else:
                    itokens = item.split(separator)
                    itokens = [repl_dict.get(itoken) for itoken in itokens]
                    olist.append(separator.join(itokens))
            entry['function'] = olist


def addex(extype, exmsg, condition=None, edata=None):
    r"""
    Adds an exception in the global exception handler

    :param extype: Exception type; *must* be derived from the `Exception
                   <https://docs.python.org/2/library/exceptions.html#
                   exceptions.Exception>`_ class
    :type  extype: Exception type object, i.e. RuntimeError, TypeError,
                   etc.

    :param exmsg: Exception message; it can contain fields to be replaced
                  when the exception is raised via
                  :py:meth:`putil.exh.ExHandle.raise_exception_if`.
                  A field starts with the characters :code:`'\*['` and
                  ends with the characters :code:`']\*'`, the field name
                  follows the same rules as variable names and is between
                  these two sets of characters. For example,
                  :code:`'\*[fname]\*'` defines the fname field
    :type  exmsg: string

    :param condition: Flag that indicates whether the exception is
                      raised *(True)* or not *(False)*. If None the
                      flag is not used an no exception is raised
    :type  condition: boolean or None

    :param edata: Replacement values for fields in the exception message
                  (see :py:meth:`putil.exh.ExHandle.add_exception` for how
                  to define fields). Each dictionary entry can only have
                  these two keys:

                  * **field** *(string)* -- Field name

                  * **value** *(any)* -- Field value, to be converted into
                    a string with the `format
                    <https://docs.python.org/2/library/stdtypes.html#
                    str.format>`_ string method

                  If None no field replacement is done

    :rtype: (if condition is not given or None) function

    :raises:
     * RuntimeError (Argument \`condition\` is not valid)

     * RuntimeError (Argument \`edata\` is not valid)

     * RuntimeError (Argument \`exmsg\` is not valid)

     * RuntimeError (Argument \`extype\` is not valid)
    """
    return _ExObj(extype, exmsg, condition, edata).craise


def addai(argname, condition=None):
    r"""
    Adds an exception of the type :code:`RuntimeError('Argument \`*[argname]*\`
    is not valid')` in the global exception handler where :code:`*[argname]*`
    is the value of the **argname** argument

    :param argname: Argument name
    :type  argname: string

    :param condition: Flag that indicates whether the exception is
                      raised *(True)* or not *(False)*. If None the flag is not
                      used and no exception is raised
    :type  condition: boolean or None

    :rtype: (if condition is not given or None) function

    :raises:
     * RuntimeError (Argument \`argname\` is not valid)

     * RuntimeError (Argument \`condition\` is not valid)
    """
    # pylint: disable=C0123
    if not isinstance(argname, str):
        raise RuntimeError('Argument `argname` is not valid')
    if (condition is not None) and (type(condition) != bool):
        raise RuntimeError('Argument `condition` is not valid')
    obj = _ExObj(
        RuntimeError,
        'Argument `{0}` is not valid'.format(argname),
        condition
    )
    return obj.craise


def del_exh_obj():
    """
    Deletes global exception handler (if set)
    """
    try:
        delattr(__builtin__, '_EXH')
    except AttributeError:
        pass


def get_exh_obj():
    """
    Returns the global exception handler

    :rtype: :py:class:`putil.exh.ExHandle` if global exception handler
            is set, None otherwise
    """
    return getattr(__builtin__, '_EXH', None)


def get_or_create_exh_obj(
    full_cname=False, exclude=None, callables_fname=None
):
    """
    Returns the global exception handler if it is set, otherwise creates a new
    global exception handler and returns it

    :param full_cname: Flag that indicates whether fully qualified
                       function/method/class property names are obtained for
                       functions/methods/class properties that use the
                       exception manager (True) or not (False).

                       There is a performance penalty if the flag is True as
                       the call stack needs to be traced. This argument is
                       only relevant if the global exception handler is not
                       set and a new one is created
    :type  full_cname: boolean

    :param exclude: Module exclusion list. A particular callable in an
                    otherwise fully qualified name is omitted if it belongs
                    to a module in this list. If None all callables are
                    included
    :type  exclude: list of strings or None

    :param callables_fname: File name that contains traced modules information.
                            File can be produced by either the
                            :py:meth:`putil.pinspect.Callables.save` or
                            :py:meth:`putil.exh.ExHandle.save_callables`
                            methods
    :type  callables_fname: :ref:`FileNameExists` or None

    :rtype: :py:class:`putil.exh.ExHandle`

    :raises:
     * OSError (File *[callables_fname]* could not be found

     * RuntimeError (Argument \\`exclude\\` is not valid)

     * RuntimeError (Argument \\`callables_fname\\` is not valid)

     * RuntimeError (Argument \\`full_cname\\` is not valid)
    """
    if not hasattr(__builtin__, '_EXH'):
        set_exh_obj(
            ExHandle(
                full_cname=full_cname,
                exclude=exclude,
                callables_fname=callables_fname
            )
        )
    return get_exh_obj()


def set_exh_obj(obj):
    """
    Sets the global exception handler

    :param obj: Exception handler
    :type  obj: :py:class:`putil.exh.ExHandle`

    :raises: RuntimeError (Argument \\`obj\\` is not valid)
    """
    if not isinstance(obj, ExHandle):
        raise RuntimeError('Argument `obj` is not valid')
    setattr(__builtin__, '_EXH', obj)


###
# Classes
###
class _ExObj(object):
    # pylint: disable=R0903
    r"""
    Exception object

    :param extype: Exception type; *must* be derived from the `Exception
                   <https://docs.python.org/2/library/exceptions.html#
                   exceptions.Exception>`_ class
    :type  extype: Exception type object, i.e. RuntimeError, TypeError,
                   etc.

    :param exmsg: Exception message; it can contain fields to be replaced
                  when the exception is raised via
                  :py:meth:`putil.exh.ExHandle.raise_exception_if`.
                  A field starts with the characters :code:`'\*['` and
                  ends with the characters :code:`']\*'`, the field name
                  follows the same rules as variable names and is between
                  these two sets of characters. For example,
                  :code:`'\*[fname]\*'` defines the fname field
    :type  exmsg: string

    :param condition: Flag that indicates whether the exception is
                      raised *(True)* or not *(False)*
    :type  condition: boolean

    :param edata: Replacement values for fields in the exception message
                  (see :py:meth:`putil.exh.ExHandle.add_exception` for how
                  to define fields). Each dictionary entry can only have
                  these two keys:

                  * **field** *(string)* -- Field name

                  * **value** *(any)* -- Field value, to be converted into
                    a string with the `format
                    <https://docs.python.org/2/library/stdtypes.html#
                    str.format>`_ string method

                  If None no field replacement is done

    :type  edata: dictionary, iterable of dictionaries or None

    :param exclude: Module exclusion list. A particular callable in an
                    otherwise fully qualified name is omitted if it belongs
                    to a module in this list. If None all callables are
                    included
    :type  exclude: list of strings or None

    :param callables_fname: File name that contains traced modules information.
                            File can be produced by either the
                            :py:meth:`putil.pinspect.Callables.save` or
                            :py:meth:`putil.exh.ExHandle.save_callables`
                            methods
    :type  callables_fname: :ref:`FileNameExists` or None

    :rtype: :py:class:`putil.exh.ExHandle`

    :raises:
     * OSError (File *[callables_fname]* could not be found

     * RuntimeError (Argument \`callables_fname\` is not valid)

     * RuntimeError (Argument \`condition\` is not valid)

     * RuntimeError (Argument \`edata\` is not valid)

      * RuntimeError (Argument \`exclude\` is not valid)

     * RuntimeError (Argument \`exname\` is not valid)

     * RuntimeError (Argument \`extype\` is not valid)

     * RuntimeError (Argument \`full_cname\` is not valid)

     * ValueError (Source for module *[module_name]* could not be found)
    """

    _count = itertools.count(0)

    def __init__(
            self, extype, exmsg, condition=None, edata=None, exclude=None,
            callables_fname=None
    ):
        super(_ExObj, self).__init__()
        self._exh = get_or_create_exh_obj(
            exclude=exclude, callables_fname=callables_fname
        )
        next(self._count)
        self._exname = '__exobj_pid_{0}_ex{1}__'.format(
            os.getpid(), self._count
        )
        self._ex_data = self._exh.add_exception(
            self._exname, extype, exmsg
        )
        if condition is not None:
            self.craise(condition, edata)

    def craise(self, condition, edata=None):
        """
        Raises exception conditionally

        :param condition: Flag that indicates whether the exception is
                          raised *(True)* or not *(False)*
        :type  condition: boolean

        :param edata: Replacement values for fields in the exception message
                      (see :py:meth:`putil.exh.ExHandle.add_exception` for how
                      to define fields). Each dictionary entry can only have
                      these two keys:

                      * **field** *(string)* -- Field name

                      * **value** *(any)* -- Field value, to be converted into
                        a string with the `format
                        <https://docs.python.org/2/library/stdtypes.html#
                        str.format>`_ string method

                      If None no field replacement is done
        :type  edata: dictionary, iterable of dictionaries or None

        :raises:
         * RuntimeError (Argument \\`condition\\` is not valid)

         * RuntimeError (Argument \\`edata\\` is not valid)

         * RuntimeError (Argument \\`exname\\` is not valid)

         * RuntimeError (Field *[field_name]* not in exception message)

         * ValueError (Exception name *[name]* not found')

        """
        self._exh.raise_exception_if(
            self._exname,
            condition,
            edata,
            _keys=self._ex_data
        )


# In the second line of some examples, the function
# putil.exh.get_or_create_exh_obj() is not used because if any other
# module that registers exceptions is executed first in the doctest run,
# the exception handler is going to be non-empty and then some of the
# tests in the examples may fail because there is previous history.
# Setting the global exception handler to a new object makes the example
# start with a clean global exception handler
class ExHandle(object):
    """
    Exception handler

    :param full_cname: Flag that indicates whether fully qualified
                       function/method/class property names are obtained for
                       functions/methods/class properties that use the
                       exception manager (True) or not (False).

                       There is a performance penalty if the flag is True as
                       the call stack needs to be traced
    :type  full_cname: boolean

    :param exclude: Module exclusion list. A particular callable in an
                    otherwise fully qualified name is omitted if it belongs
                    to a module in this list. If None all callables are
                    included
    :type  exclude: list of strings or None

    :param callables_fname: File name that contains traced modules information.
                            File can be produced by either the
                            :py:meth:`putil.pinspect.Callables.save` or
                            :py:meth:`putil.exh.ExHandle.save_callables`
                            methods
    :type  callables_fname: :ref:`FileNameExists` or None

    :rtype: :py:class:`putil.exh.ExHandle`

    :raises:
     * OSError (File *[callables_fname]* could not be found

     * RuntimeError (Argument \\`exclude\\` is not valid)

     * RuntimeError (Argument \\`callables_fname\\` is not valid)

     * RuntimeError (Argument \\`full_cname\\` is not valid)

     * ValueError (Source for module *[module_name]* could not be found)
    """
    # pylint: disable=R0902,W0703
    def __init__(
        self, full_cname=False, exclude=None, callables_fname=None, _copy=False
    ):
        if not isinstance(full_cname, bool):
            raise RuntimeError('Argument `full_cname` is not valid')
        if ((exclude and (not isinstance(exclude, list))) or
           (isinstance(exclude, list) and
           any([not isinstance(item, str) for item in exclude]))):
            raise RuntimeError('Argument `exclude` is not valid')
        self._ex_dict = {}
        self._clut = {}
        self._callables_separator = '/'
        self._full_cname = full_cname
        self._exclude = exclude
        self._callables_obj = None
        self._exclude_list = []
        if not _copy:
            self._callables_obj = putil.pinspect.Callables()
            if callables_fname is not None:
                self._callables_obj.load(callables_fname)
            self._exclude_list = _build_exclusion_list(exclude)

    def __add__(self, other):
        """
        Merges two objects.

        :raises:
         * RuntimeError (Incompatible exception handlers)

         * TypeError (Unsupported operand type(s) for +:
           putil.exh.ExHandle and *[other_type]*)

        For example:

            >>> import copy, putil.exh, putil.eng, putil.tree
            >>> exhobj = putil.exh.set_exh_obj(putil.exh.ExHandle())
            >>> putil.eng.peng(100, 3, True)
            ' 100.000 '
            >>> tobj = putil.tree.Tree().add_nodes([{'name':'a', 'data':5}])
            >>> obj1 = copy.copy(putil.exh.get_exh_obj())
            >>> putil.exh.del_exh_obj()
            >>> exhobj = putil.exh.get_or_create_exh_obj()
            >>> putil.eng.peng(100, 3, True) # Trace some exceptions
            ' 100.000 '
            >>> obj2 = copy.copy(putil.exh.get_exh_obj())
            >>> putil.exh.del_exh_obj()
            >>> exhobj = putil.exh.get_or_create_exh_obj()
            >>> tobj = putil.tree.Tree().add_nodes([{'name':'a', 'data':5}])
            >>> obj3 = copy.copy(putil.exh.get_exh_obj())
            >>> obj1 == obj2
            False
            >>> obj1 == obj3
            False
            >>> obj1 == obj2+obj3
            True
        """
        if not isinstance(other, ExHandle):
            stype = str(type(other))
            offset = stype.index("'")+1
            raise TypeError(
                'Unsupported operand type(s) for +: putil.exh.ExHandle and '+
                stype[offset:-2]
            )
        if ((self._full_cname != other._full_cname) or
           (self._exclude != other._exclude)):
            raise RuntimeError('Incompatible exception handlers')
        robj = ExHandle(
            full_cname=self._full_cname, exclude=self._exclude, _copy=True
        )
        ex_dict = copy.deepcopy(other._ex_dict)
        robj._ex_dict = copy.deepcopy(self._ex_dict)
        robj._clut = copy.deepcopy(self._clut)
        _merge_cdicts(robj, other._clut, ex_dict, other._callables_separator)
        robj._ex_dict.update(ex_dict)
        robj._callables_obj = (
            copy.copy(self._callables_obj)+copy.copy(other._callables_obj)
        )
        return robj

    def __bool__(self): # pragma: no cover
        """
        Returns :code:`False` if exception handler does not have any exception
        defined, :code:`True` otherwise.

        .. note:: This method applies to Python 3.x

        For example:

            >>> from __future__ import print_function
            >>> import putil.exh
            >>> obj = putil.exh.ExHandle()
            >>> if obj:
            ...     print('Boolean test returned: True')
            ... else:
            ...     print('Boolean test returned: False')
            Boolean test returned: False
            >>> def my_func(exhobj):
            ...     exhobj.add_exception('test', RuntimeError, 'Message')
            >>> my_func(obj)
            >>> if obj:
            ...     print('Boolean test returned: True')
            ... else:
            ...     print('Boolean test returned: False')
            Boolean test returned: True
        """
        return bool(self._ex_dict)

    def __copy__(self):
        """
        Copies object. For example:

            >>> import copy, putil.exh, putil.eng
            >>> exhobj = putil.exh.set_exh_obj(putil.exh.ExHandle())
            >>> putil.eng.peng(100, 3, True)
            ' 100.000 '
            >>> obj1 = putil.exh.get_exh_obj()
            >>> obj2 = copy.copy(obj1)
            >>> obj1 == obj2
            True
        """
        cobj = ExHandle(
            full_cname=self._full_cname, exclude=self._exclude, _copy=True
        )
        cobj._ex_dict = copy.deepcopy(self._ex_dict)
        cobj._clut = copy.deepcopy(self._clut)
        cobj._exclude_list = self._exclude_list[:]
        cobj._callables_obj = copy.copy(self._callables_obj)
        return cobj

    def __eq__(self, other):
        """
        Tests object equality. For example:

            >>> import copy, putil.exh, putil.eng
            >>> exhobj = putil.exh.set_exh_obj(putil.exh.ExHandle())
            >>> putil.eng.peng(100, 3, True)
            ' 100.000 '
            >>> obj1 = putil.exh.get_exh_obj()
            >>> obj2 = copy.copy(obj1)
            >>> obj1 == obj2
            True
            >>> 5 == obj1
            False
        """
        return (
            isinstance(other, ExHandle) and
            (sorted(self._ex_dict) == sorted(other._ex_dict)) and
            (self._callables_obj == other._callables_obj) and
            (sorted(self._clut) == sorted(other._clut))
        )

    def __iadd__(self, other):
        """
        Merges an object into an existing object.

        :raises:
         * RuntimeError (Incompatible exception handlers)

         * TypeError (Unsupported operand type(s) for +:
           putil.exh.ExHandle and *[other_type]*)

        For example:

            >>> import copy, putil.exh, putil.eng, putil.tree
            >>> exhobj = putil.exh.set_exh_obj(putil.exh.ExHandle())
            >>> putil.eng.peng(100, 3, True)
            ' 100.000 '
            >>> tobj = putil.tree.Tree().add_nodes([{'name':'a', 'data':5}])
            >>> obj1 = copy.copy(putil.exh.get_exh_obj())
            >>> putil.exh.del_exh_obj()
            >>> exhobj = putil.exh.get_or_create_exh_obj()
            >>> putil.eng.peng(100, 3, True) # Trace some exceptions
            ' 100.000 '
            >>> obj2 = copy.copy(putil.exh.get_exh_obj())
            >>> putil.exh.del_exh_obj()
            >>> exhobj = putil.exh.get_or_create_exh_obj()
            >>> tobj = putil.tree.Tree().add_nodes([{'name':'a', 'data':5}])
            >>> obj3 = copy.copy(putil.exh.get_exh_obj())
            >>> obj1 == obj2
            False
            >>> obj1 == obj3
            False
            >>> obj2 += obj3
            >>> obj1 == obj2
            True
        """
        if not isinstance(other, ExHandle):
            stype = str(type(other))
            offset = stype.index("'")+1
            raise TypeError(
                'Unsupported operand type(s) for +: putil.exh.ExHandle and '+
                stype[offset:-2]
            )
        if ((self._full_cname != other._full_cname) or
           (self._exclude != other._exclude)):
            raise RuntimeError('Incompatible exception handlers')
        ex_dict = copy.deepcopy(other._ex_dict)
        _merge_cdicts(self, other._clut, ex_dict, other._callables_separator)
        self._ex_dict.update(ex_dict)
        self._callables_obj += copy.copy(other._callables_obj)
        return self

    def __nonzero__(self):  # pragma: no cover
        """
        Returns :code:`False` if exception handler does not have any exception
        defined, :code:`True` otherwise.

        .. note:: This method applies to Python 2.7

        For example:

            >>> from __future__ import print_function
            >>> import putil.exh
            >>> obj = putil.exh.ExHandle()
            >>> if obj:
            ...     print('Boolean test returned: True')
            ... else:
            ...     print('Boolean test returned: False')
            Boolean test returned: False
            >>> def my_func(exhobj):
            ...     exhobj.add_exception('test', RuntimeError, 'Message')
            >>> my_func(obj)
            >>> if obj:
            ...     print('Boolean test returned: True')
            ... else:
            ...     print('Boolean test returned: False')
            Boolean test returned: True
        """
        return bool(self._ex_dict)

    def __str__(self):
        """
        Returns a string with a detailed description of the object's contents.
        For example:

            >>> from __future__ import print_function
            >>> import docs.support.exh_example
            >>> putil.exh.del_exh_obj()
            >>> docs.support.exh_example.my_func('Tom')
            My name is Tom
            >>> print(str(putil.exh.get_exh_obj())) #doctest: +ELLIPSIS
            Name    : ...
            Type    : TypeError
            Message : Argument `name` is not valid
            Function: None
        """
        ret = []
        fex_dict = self._flatten_ex_dict()
        for key in sorted(fex_dict.keys()):
            # Exception name and details
            rstr = []
            extype = _ex_type_str(fex_dict[key]['type'])
            exmsg = fex_dict[key]['msg']
            rstr.append('Name    : {exname}'.format(exname=key))
            rstr.append('Type    : {extype}'.format(extype=extype))
            rstr.append('Message : {exmsg}'.format(exmsg=exmsg))
            # Callable paths: a given callable that registers an exception
            # can be called multiple times following different calling paths,
            # so there could potentially be multiple items in the
            # self._ex_dict[key]['function'] list
            flist = [
                self.decode_call(item)
                for item in fex_dict[key]['function']
            ]
            iobj = enumerate(sorted(flist))
            for fnum, func_name in iobj:
                rindex = flist.index(func_name)
                rstr.append(
                   '{callable_type}{callable_name}{rtext}'.format(
                       callable_type='Function: ' if fnum == 0 else ' '*10,
                       callable_name=func_name,
                       rtext=(
                           ' [raised]'
                           if fex_dict[key]['raised'][rindex] else
                           ''
                       )
                   )
                )
            ret.append('\n'.join(rstr))
        return '\n\n'.join(ret)

    def _flatten_ex_dict(self):
        """ Flatten structure of exceptions dictionary """
        odict = {}
        for _, fdict in self._ex_dict.items():
            for (extype, exmsg), value in fdict.items():
                key = value['name']
                odict[key] = copy.deepcopy(value)
                del odict[key]['name']
                odict[key]['type'] = extype
                odict[key]['msg'] = exmsg
        return odict

    def _format_msg(self, msg, edata):
        """ Substitute parameters in exception message """
        edata = edata if isinstance(edata, list) else [edata]
        for fdict in edata:
            if '*[{token}]*'.format(token=fdict['field']) not in msg:
                raise RuntimeError(
                    'Field {token} not in exception message'.format(
                        token=fdict['field']
                    )
                )
            msg = msg.replace(
                '*[{token}]*'.format(token=fdict['field']), '{value}'
            ).format(value=fdict['value'])
        return msg

    def _get_callables_db(self):
        """ Returns database of callables """
        return self._callables_obj.callables_db

    def _get_callable_full_name(self, fob, fin, uobj):
        """
        Get full path [module, class (if applicable) and function name]
        of callable
        """
        # Check if object is a class property
        name = self._property_search(fob)
        if name:
            del fob, fin, uobj
            return name
        if os.path.isfile(fin):
            lineno = fob.f_lineno
            ret = self._callables_obj.get_callable_from_line(fin, lineno)
            del fob, fin, uobj, name, lineno
            return ret
        # Code executed in doctests does not have an actual callable object
        # exec-based callables do not have a valid file name
        fname = uobj and _get_func_code(uobj).co_filename
        if (not fname) or (fname and (not os.path.isfile(fname))):
            del fob, fin, uobj, name, fname
            return 'dynamic'
        code_id = (
            inspect.getfile(uobj).replace('.pyc', 'py'),
            inspect.getsourcelines(uobj)[1]
        )
        self._callables_obj.trace([code_id[0]])
        ret = self._callables_obj.reverse_callables_db[code_id]
        del fob, fin, uobj, name, fname, code_id
        return ret

    if (hasattr(sys.modules['decorator'], '__version__') and
       (int(decorator.__version__.split('.')[0]) == 3)):   # pragma: no cover
        # Method works with decorator 3.x series
        def _get_callable_path(self):
            """ Get fully qualified calling function name """
            # If full_cname is False, then the only thing that matters is to
            # return the ID of the calling function as fast as possible. If
            # full_cname is True, the full calling path has to be calculated
            # because multiple callables can call the same callable, thus the
            # ID does not uniquely identify the callable path
            fnum = 0
            frame = sys._getframe(fnum)
            while _invalid_frame(frame):
                fnum += 1
                frame = sys._getframe(fnum)
            callable_id = id(frame.f_code)
            if not self._full_cname:
                del frame
                return callable_id, None
            # Filter stack to omit frames that are part of the exception
            # handling module, argument validation, or top level (tracing)
            # module Stack frame -> (frame object [0], filename [1], line
            # number of current line [2], function name [3], list of lines
            # of context from source code [4], index of current line within
            # list [5]) Classes initialization appear as:
            # filename = '<string>', function name = '__init__', list of lines
            # of context from source code = None, index of current line within
            # list = None
            stack = []
            ### Check to see if path has modules in exclude list
            fin, lin, fun, fuc, fui = inspect.getframeinfo(frame)
            uobj, ufin = self._unwrap_obj(frame, fun)
            if ufin in self._exclude_list:
                del uobj, frame
                return callable_id, None
            tokens = frame.f_code.co_filename.split(os.sep)
            ###
            while not any([token.startswith(item)
                  for token in tokens for item in _BREAK_LIST]):
                # Gobble up two frames if it is a decorator. 4th stack list
                # tuple element (index 3) indicates whether the frame
                # corresponds to a decorator or not
                if (fin, lin, fuc, fui) == ('<string>', 2, None, None):
                    stack.pop()
                    if stack:
                        stack[-1][3] = True
                stack.append([frame, fin, uobj, False])
                fnum += 1
                try:
                    frame = sys._getframe(fnum)
                except ValueError:
                    # Got to top of stack
                    break
                ### Check to see if path has modules in exclude list
                # Repeated to avoid an expensive function call
                fin, lin, fun, fuc, fui = inspect.getframeinfo(frame)
                uobj, ufin = self._unwrap_obj(frame, fun)
                if ufin in self._exclude_list:
                    del uobj, frame, stack
                    return callable_id, None
                tokens = frame.f_code.co_filename.split(os.sep)
                ###
            # Stack is from most recent frame out, fully qualified
            # callable path is from first callable to lat callable
            stack.reverse()
            # Decorator flag vector
            idv = [item[3] for item in stack]
            # Fully qualified callable path construction
            ret = list(
                self._get_callable_full_name(fob, fin, uobj)
                for fob, fin, uobj, _ in stack
            )
            # Eliminate callables that are in a decorator chain
            iobj = enumerate(zip(ret[1:], ret, idv[1:]))
            num_del_items = 0
            for num, (name, prev_name, in_decorator) in iobj:
                if in_decorator and (name == prev_name):
                    del ret[num-num_del_items]
                    num_del_items += 1
            del uobj, frame, stack
            return callable_id, self._callables_separator.join(ret)
    else:   # pragma: no cover
        # Method works with decorator 4.x series
        def _get_callable_path(self):
            """ Get fully qualified calling function name """
            # If full_cname is False, then the only thing that matters is to
            # return the ID of the calling function as fast as possible. If
            # full_cname is True, the full calling path has to be calculated
            # because multiple callables can call the same callable, thus the
            # ID does not uniquely identify the callable path
            fnum = 0
            frame = sys._getframe(fnum)
            while _invalid_frame(frame):
                fnum += 1
                frame = sys._getframe(fnum)
            callable_id = id(frame.f_code)
            if not self._full_cname:
                del frame
                return callable_id, None
            # Filter stack to omit frames that are part of the exception
            # handling module, argument validation, or top level (tracing)
            # module Stack frame -> (frame object [0], filename [1], line
            # number of current line [2], function name [3], list of lines
            # of context from source code [4], index of current line within
            # list [5]) Classes initialization appear as:
            # filename = '<string>', function name = '__init__', list of lines
            # of context from source code = None, index of current line within
            # list = None
            stack = []
            ### Check to see if path has modules in exclude list
            fin, _, fun, _, _ = inspect.getframeinfo(frame)
            uobj, ufin = self._unwrap_obj(frame, fun)
            if ufin in self._exclude_list:
                del uobj, frame
                return callable_id, None
            tokens = frame.f_code.co_filename.split(os.sep)
            ###
            while not any([token.startswith(item)
                  for token in tokens for item in _BREAK_LIST]):
                stack.append([frame, fin, uobj])
                fnum += 1
                try:
                    frame = sys._getframe(fnum)
                except ValueError:
                    # Got to top of stack
                    break
                ### Check to see if path has modules in exclude list
                # Repeated to avoid an expensive function call
                fin, _, fun, _, _ = inspect.getframeinfo(frame)
                uobj, ufin = self._unwrap_obj(frame, fun)
                if ufin in self._exclude_list:
                    del uobj, frame, stack
                    return callable_id, None
                tokens = frame.f_code.co_filename.split(os.sep)
                ###
            # Stack is from most recent frame out, fully qualified
            # callable path is from first callable to lat callable
            stack.reverse()
            # Fully qualified callable path construction (exclude
            # pcontracts decorators)
            ret = []
            skip = 0
            dlist = ['putil.pcontracts', 'putil.pcontracts.contract.wrapper']
            for fob, fin, uobj in stack:
                if skip > 0:
                    skip -= 1
                else:
                    item = self._get_callable_full_name(fob, fin, uobj)
                    if item in dlist:
                        skip = 3
                    else:
                        ret.append(item)
            del fob, uobj, frame, stack
            return callable_id, self._callables_separator.join(ret)

    def _get_callables_separator(self):
        """ Get callable separator character """
        return self._callables_separator

    def _get_exceptions_db(self):
        """
        Returns a list of dictionaries suitable to be used with
        putil.tree module
        """
        template = '{extype} ({exmsg}){raised}'
        if not self._full_cname:
            # When full callable name is not used the calling path is
            # irrelevant and there is no function associated with an
            # exception
            ret = []
            for _, fdict in self._ex_dict.items():
                for key in fdict.keys():
                    ret.append(
                        {
                            'name':fdict[key]['name'],
                            'data':template.format(
                                extype=_ex_type_str(key[0]),
                                exmsg=key[1],
                                raised='*' if fdict[key]['raised'][0] else ''
                            )
                        }
                    )
            return ret
        # When full callable name is used, all calling paths are saved
        ret = []
        for fdict in self._ex_dict.values():
            for key in fdict.keys():
                for func_name in fdict[key]['function']:
                    rindex = fdict[key]['function'].index(func_name)
                    raised = fdict[key]['raised'][rindex]
                    ret.append(
                        {
                            'name':self.decode_call(func_name),
                            'data':template.format(
                                extype=_ex_type_str(key[0]),
                                exmsg=key[1],
                                raised='*' if raised else ''
                            )
                        }
                    )
        return ret

    def _get_ex_data(self):
        """ Returns hierarchical function name """
        func_id, func_name = self._get_callable_path()
        if self._full_cname:
            func_name = self.encode_call(func_name)
        return func_id, func_name

    def _property_search(self, fobj):
        """
        Check if object is a class property and if so return full name,
        otherwise return None
        """
        # Get class object
        scontext = fobj.f_locals.get('self', None)
        class_obj = scontext.__class__ if scontext is not None else None
        if not class_obj:
            del fobj, scontext, class_obj
            return
        # Get class properties objects
        class_props = [
            (member_name, member_obj)
            for member_name, member_obj in inspect.getmembers(class_obj)
            if isinstance(member_obj, property)
        ]
        if not class_props:
            del fobj, scontext, class_obj
            return
        class_file = inspect.getfile(class_obj).replace('.pyc', '.py')
        class_name = self._callables_obj.get_callable_from_line(
            class_file,
            inspect.getsourcelines(class_obj)[1]
        )
        # Get properties actions
        prop_actions_dicts = {}
        for prop_name, prop_obj in class_props:
            prop_dict = {'fdel':None, 'fget':None, 'fset':None}
            for action in prop_dict.keys():
                action_obj = getattr(prop_obj, action)
                if action_obj:
                    # Unwrap action object. Contracts match the wrapped
                    # code object while exceptions registered in the
                    # body of the function/method which has decorators
                    # match the unwrapped object
                    prev_func_obj, next_func_obj = (
                        action_obj,
                        getattr(action_obj, '__wrapped__', None)
                    )
                    while next_func_obj:
                        prev_func_obj, next_func_obj = (
                            next_func_obj,
                            getattr(next_func_obj, '__wrapped__', None)
                        )
                    prop_dict[action] = [
                        id(_get_func_code(action_obj)),
                        id(_get_func_code(prev_func_obj))
                    ]
            prop_actions_dicts[prop_name] = prop_dict
        # Create properties directory
        func_id = id(fobj.f_code)
        desc_dict = {
            'fget':'getter',
            'fset':'setter',
            'fdel':'deleter',
        }
        for prop_name, prop_actions_dict in prop_actions_dicts.items():
            for action_name, action_id_list in prop_actions_dict.items():
                if action_id_list and (func_id in action_id_list):
                    prop_name = '.'.join([class_name, prop_name])
                    del fobj, scontext, class_obj, class_props
                    return '{prop_name}({prop_action})'.format(
                        prop_name=prop_name,
                        prop_action=desc_dict[action_name]
                    )

    def _raise_exception(self, eobj, edata=None):
        """ Raise exception by name """
        _, _, tbobj = sys.exc_info()
        if edata:
            emsg = self._format_msg(eobj['msg'], edata)
            _rwtb(eobj['type'], emsg, tbobj)
        else:
            _rwtb(eobj['type'], eobj['msg'], tbobj)

    def _unwrap_obj(self, fobj, fun):
        """ Unwrap decorators """
        try:
            prev_func_obj, next_func_obj = (
                fobj.f_globals[fun],
                getattr(fobj.f_globals[fun], '__wrapped__', None)
            )
            while next_func_obj:
                prev_func_obj, next_func_obj = (
                    next_func_obj,
                    getattr(next_func_obj, '__wrapped__', None)
                )
            return (
                prev_func_obj,
                inspect.getfile(prev_func_obj).replace('.pyc', 'py')
            )
        except  (KeyError, AttributeError, TypeError):
            # KeyErrror: fun not in fobj.f_globals
            # AttributeError: fobj.f_globals does not have
            #                 a __wrapped__ attribute
            # TypeError: pref_func_obj does not have a file associated with it
            return None, None

    def _validate_edata(self, edata):
        """ Validate edata argument of raise_exception_if method """
        # pylint: disable=R0916
        if edata is None:
            return True
        if not (isinstance(edata, dict) or _isiterable(edata)):
            return False
        edata = [edata] if isinstance(edata, dict) else edata
        for edict in edata:
            if ((not isinstance(edict, dict)) or
               (isinstance(edict, dict) and
               (('field' not in edict) or
               ('field' in edict and (not isinstance(edict['field'], str))) or
               ('value' not in edict)))):
                return False
        return True

    def add_exception(self, exname, extype, exmsg):
        r"""
        Adds an exception to the handler

        :param exname: Exception name; has to be unique within the namespace,
                       duplicates are eliminated
        :type  exname: non-numeric string

        :param extype: Exception type; *must* be derived from the `Exception
                       <https://docs.python.org/2/library/exceptions.html#
                       exceptions.Exception>`_ class
        :type  extype: Exception type object, i.e. RuntimeError, TypeError,
                       etc.

        :param exmsg: Exception message; it can contain fields to be replaced
                      when the exception is raised via
                      :py:meth:`putil.exh.ExHandle.raise_exception_if`.
                      A field starts with the characters :code:`'\*['` and
                      ends with the characters :code:`']\*'`, the field name
                      follows the same rules as variable names and is between
                      these two sets of characters. For example,
                      :code:`'\*[fname]\*'` defines the fname field
        :type  exmsg: string

        :rtype: tuple

        The returned tuple has the following items:

          * **callable id** (string) first returned item, identification (as
            reported by the `id
            <https://docs.python.org/2/library/functions.html#id>`_ built-in
            function) of the callable where the exception was added

          * **exception definition** (tuple), second returned item, first item
            is the exception type and the second item is the exception message

          * **callable name** (string), third returned item, callable full
            name (encoded with the :py:meth:`ExHandle.encode_call` method

        :raises:
         * RuntimeError (Argument \`exmsg\` is not valid)

         * RuntimeError (Argument \`exname\` is not valid)

         * RuntimeError (Argument \`extype\` is not valid)
        """
        if not isinstance(exname, str):
            raise RuntimeError('Argument `exname` is not valid')
        number = True
        try:
            int(exname)
        except ValueError:
            number = False
        if number:
            raise RuntimeError('Argument `exname` is not valid')
        if not isinstance(exmsg, str):
            raise RuntimeError('Argument `exmsg` is not valid')
        msg = ''
        try:
            raise extype(exmsg)
        except Exception as eobj:
            msg = _get_ex_msg(eobj)
        if msg != exmsg:
            raise RuntimeError('Argument `extype` is not valid')
        # A callable that defines an exception can be accessed by
        # multiple functions or paths, therefore the callable
        # dictionary key 'function' is a list
        func_id, func_name = self._get_ex_data()
        if func_id not in self._ex_dict:
            self._ex_dict[func_id] = {}
        key = (extype, exmsg)
        exname = '{0}{1}{2}'.format(func_id, self._callables_separator, exname)
        entry = self._ex_dict[func_id].get(
            key, {'function':[], 'name':exname, 'raised':[]}
        )
        if func_name not in entry['function']:
            entry['function'].append(func_name)
            entry['raised'].append(False)
        self._ex_dict[func_id][key] = entry
        return (func_id, key, func_name)

    def decode_call(self, call):
        """
        Replaces callable tokens with callable names

        :param call: Encoded callable  name
        :type  call: string

        :rtype: string
        """
        # Callable name is None when callable is part of exclude list
        if call is None:
            return
        itokens = call.split(self._callables_separator)
        odict = {}
        for key, value in self._clut.items():
            if value in itokens:
                odict[itokens[itokens.index(value)]] = key
        return self._callables_separator.join(
            [odict[itoken] for itoken in itokens]
        )

    def encode_call(self, call):
        """
        Replaces callables with tokens to reduce object memory footprint. A
        callable token is an integer that denotes the order in which the
        callable was encountered by the encoder, i.e. the first callable
        encoded is assigned token 0, the second callable encoded is assigned
        token 1, etc.

        :param call: Callable name
        :type  call: string

        :rtype: string
        """
        # Callable name is None when callable is part of exclude list
        if call is None:
            return
        itokens = call.split(self._callables_separator)
        otokens = []
        for itoken in itokens:
            otoken = self._clut.get(itoken, None)
            if not otoken:
                otoken = str(len(self._clut))
                self._clut[itoken] = otoken
            otokens.append(otoken)
        return self._callables_separator.join(otokens)

    def raise_exception_if(self, exname, condition, edata=None, _keys=None):
        """
        Raises exception conditionally

        :param exname: Exception name
        :type  exname: string

        :param condition: Flag that indicates whether the exception is
                          raised *(True)* or not *(False)*
        :type  condition: boolean

        :param edata: Replacement values for fields in the exception message
                      (see :py:meth:`putil.exh.ExHandle.add_exception` for how
                      to define fields). Each dictionary entry can only have
                      these two keys:

                      * **field** *(string)* -- Field name

                      * **value** *(any)* -- Field value, to be converted into
                        a string with the `format
                        <https://docs.python.org/2/library/stdtypes.html#
                        str.format>`_ string method

                      If None no field replacement is done
        :type  edata: dictionary, iterable of dictionaries or None

        :raises:
         * RuntimeError (Argument \\`condition\\` is not valid)

         * RuntimeError (Argument \\`edata\\` is not valid)

         * RuntimeError (Argument \\`exname\\` is not valid)

         * RuntimeError (Field *[field_name]* not in exception message)

         * ValueError (Exception name *[name]* not found')

        """
        # _edict is an argument used by the _ExObj class which saves a
        # second exception look-up since the _ExObj class can save the
        # call dictionary
        if not isinstance(condition, bool):
            raise RuntimeError('Argument `condition` is not valid')
        if not self._validate_edata(edata):
            raise RuntimeError('Argument `edata` is not valid')
        if _keys is None:
            if not isinstance(exname, str):
                raise RuntimeError('Argument `exname` is not valid')
            # Find exception object
            func_id, func_name = self._get_ex_data()
            name = '{0}{1}{2}'.format(
                func_id, self._callables_separator, exname
            )
            for key, value in self._ex_dict[func_id].items():
                if value['name'] == name:
                    break
            else:
                raise ValueError(
                    'Exception name {exname} not found'.format(exname=exname)
                )
            _keys = (func_id, key, func_name)
        eobj = self._ex_dict[_keys[0]][_keys[1]]
        if condition:
            eobj['raised'][eobj['function'].index(_keys[2])] = True
            self._raise_exception(
                {'type':_keys[1][0], 'msg':_keys[1][1]}, edata
            )

    def save_callables(self, callables_fname):
        """
        Saves traced modules information to a `JSON <http://www.json.org>`_
        file. If the file exists it is overwritten

        :param callables_fname: File name
        :type  callables_fname: :ref:`FileName`

        :raises: RuntimeError (Argument \\`callables_fname\\` is not valid)
        """
        self._callables_obj.save(callables_fname)

    # Managed attributes
    callables_db = property(_get_callables_db, doc='Dictionary of callables')
    """
    Returns the callables database of the modules using the exception handler,
    as reported by :py:meth:`putil.pinspect.Callables.callables_db`
    """

    callables_separator = property(
        _get_callables_separator, doc='Callable separator character'
    )
    """
    Returns the character (:code:`'/'`) used to separate the sub-parts of fully
    qualified function names in :py:meth:`putil.exh.ExHandle.callables_db` and
    **name** key in :py:meth:`putil.exh.ExHandle.exceptions_db`
    """

    exceptions_db = property(_get_exceptions_db, doc='Formatted exceptions')
    """
    Returns the exceptions database. This database is a list of dictionaries
    that contain the following keys:

     * **name** *(string)* -- Exception name of the form
       :code:`'[callable_identifier]/[exception_name]'`. The contents of
       :code:`[callable_identifier]` depend on the value of the argument
       **full_cname** used to create the exception handler.

       If **full_cname** is True, :code:`[callable_identifier]` is the fully
       qualified callable name as it appears in the callables database
       (:py:meth:`putil.exh.ExHandle.callables_db`).

       If **full_cname** is False, then :code:`[callable_identifier]` is a
       decimal string representation of the callable's code identifier as
       reported by the
       `id() <https://docs.python.org/2/library/functions.html#id>`_
       function.

       In either case :code:`[exception_name]` is the name of the exception
       provided when it was defined in
       :py:meth:`putil.exh.ExHandle.add_exception` (**exname** argument)

     * **data** *(string)* -- Text of the form :code:`'[exception_type]
       ([exception_message])[raised]'` where :code:`[exception_type]` and
       :code:`[exception_message]` are the exception type and exception
       message, respectively, given when the exception was defined by
       :py:meth:`putil.exh.ExHandle.add_exception` (**extype** and
       **exmsg** arguments); and :code:`raised` is an asterisk (:code:`'*'`)
       when the exception has been raised via
       :py:meth:`putil.exh.ExHandle.raise_exception_if`, the empty string
       (:code:`''`) otherwise
    """
