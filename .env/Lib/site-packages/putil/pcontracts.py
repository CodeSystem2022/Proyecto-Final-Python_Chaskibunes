# pcontracts.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,E0102,E0611,E1101,F0401,R0912,R0914,W0212,W0613

# Standard library imports
import inspect
import os
import re
import sys
# PyPI imports
if os.environ.get('READTHEDOCS', False) != 'True': # pragma: no branch
    # The PyContracts module imports numpy, which is not allowed in
    # the ReadTheDocs environment
    import contracts
import decorator
try:    # pragma: no cover
    from funcsigs import signature, Parameter
except ImportError: # pragma: no cover
    signature = inspect.signature
    Parameter = inspect.Parameter
# Putil imports
import putil.exh
if sys.hexversion < 0x03000000: # pragma: no cover
    from putil.compat2 import _raise_exception
else:   # pragma: no cover
    from putil.compat3 import _raise_exception


###
# Global variables
###
RTD = os.environ.get('READTHEDOCS', False) == 'True'
_CUSTOM_CONTRACTS = dict()


###
# Functions
###
def _create_argument_value_pairs(func, *args, **kwargs):
    """
    Creates a dictionary where the keys are the argument names and the values
    are the passed arguments values (if any)

    An empty dictionary is returned if an error is detected, such as more
    arguments than in the function definition, argument(s) defined by position
    and keyword, etc.
    """
    # Capture parameters that have been explicitly specified in function call
    try:
        arg_dict = signature(func).bind_partial(*args, **kwargs).arguments
    except TypeError:
        return dict()
    # Capture parameters that have not been explicitly specified
    # but have default values
    arguments = signature(func).parameters
    for arg_name in arguments:
        if ((arguments[arg_name].default != Parameter.empty) and
           (arguments[arg_name].name not in arg_dict)):
            arg_dict[arguments[arg_name].name] = arguments[arg_name].default
    return arg_dict


def _format_arg(arg):
    """ Validate one exception specification contract tuple/list """
    # Check that the argument conforms to one of the acceptable types, a string
    # (when the default exception type is used), an exception type (when the
    # default exception message is used) or a list/tuple to specify both
    # exception type and exception message
    if (not (isinstance(arg, str) or _isexception(arg) or
       isinstance(arg, tuple) or isinstance(arg, list))):
        raise TypeError('Illegal custom contract exception definition')
    # Check that when the argument is a list or tuple, they only have at most
    # 2 items, the exception type and the exception message
    if ((isinstance(arg, tuple) or isinstance(arg, list)) and
       ((len(arg) == 0) or (len(arg) > 2))):
        raise TypeError('Illegal custom contract exception definition')
    # When only an exception message is given (and the default RuntimeError
    # exception type is used), check that the message is not empty
    if isinstance(arg, str) and (len(arg) == 0):
        raise ValueError('Empty custom contract exception message')
    # When only an exception message is defined,
    # use the default exception type
    if isinstance(arg, str):
        return {'msg':arg, 'type':RuntimeError}
    # When only an exception type is defined,
    # use the default exception message
    if _isexception(arg):
        return {'msg':'Argument `*[argument_name]*` is not valid', 'type':arg}
    # If a list/tuple definition is used, check that if is not a string, it is
    # a valid exception type (i.e. that it actually raises an exception)
    if ((len(arg) == 1) and
       (not isinstance(arg[0], str)) and
       (not _isexception(arg[0]))):
        raise TypeError('Illegal custom contract exception definition')
    if ((len(arg) == 2) and
       (not ((isinstance(arg[0], str) and
       _isexception(arg[1])) or
       (isinstance(arg[1], str) and _isexception(arg[0]))))):
        raise TypeError('Illegal custom contract exception definition')
    # Check that the exception definition has a non-empty exception message
    # when a list/tuple definition is used
    if (len(arg) == 1) and isinstance(arg[0], str) and (len(arg[0]) == 0):
        raise ValueError('Empty custom contract exception message')
    if ((len(arg) == 2) and ((isinstance(arg[0], str) and (len(arg[0]) == 0))
       or (isinstance(arg[1], str) and (len(arg[1]) == 0)))):
        raise ValueError('Empty custom contract exception message')
    # Return conforming dictionary with default exception type and exception
    # message applied (if necessary)
    if len(arg) == 1:
        return {
            'msg':(
                arg[0]
                if isinstance(arg[0], str) else
                'Argument `*[argument_name]*` is not valid'
            ),
            'type':arg[0] if _isexception(arg[0]) else RuntimeError
        }
    else:   # len(arg) == 2
        return {
            'msg':arg[0] if isinstance(arg[0], str) else arg[1],
            'type':arg[0] if _isexception(arg[0]) else arg[1]
        }


def _get_contract_exception_dict(contract_msg):
    """ Generate message for exception """
    # A pcontract-defined custom exception message is wrapped in a string
    # that starts with '[START CONTRACT MSG:' and ends with
    # '[STOP CONTRACT MSG]'. This is done to easily detect if an
    # exception raised is from a custom contract and thus be able
    # to easily retrieve the actual exception message
    start_token = '[START CONTRACT MSG: '
    stop_token = '[STOP CONTRACT MSG]'
    # No custom contract
    if contract_msg.find(start_token) == -1:
        return {
            'num':0,
            'msg':'Argument `*[argument_name]*` is not valid',
            'type':RuntimeError, 'field':'argument_name'
        }
    else:
        # Custom contract
        msg_start = contract_msg.find(start_token)+len(start_token)
        contract_msg = contract_msg[msg_start:]
        contract_name = contract_msg[:contract_msg.find(']')]
        contract_msg = contract_msg[
            contract_msg.find(']')+1:contract_msg.find(stop_token)
        ]
        exdict = _CUSTOM_CONTRACTS[contract_name]
        for exvalue in exdict.values(): # pragma: no branch
            if exvalue['msg'] == contract_msg:
                return exvalue


def _get_custom_contract(param_contract):
    """
    Returns True if the parameter contract is a custom contract,
    False otherwise
    """
    if not isinstance(param_contract, str):
        return None
    for custom_contract in _CUSTOM_CONTRACTS:
        if re.search(r'\b{0}\b'.format(custom_contract), param_contract):
            return custom_contract
    return None


def _isexception(obj):
    """
    Tests if the argument is an exception object

    :param obj: Object
    :type  obj: any

    :rtype: boolean
    """
    return False if not inspect.isclass(obj) else issubclass(obj, Exception)


def all_disabled():
    """
    Wraps PyContracts `all_disabled()
    <http://andreacensi.github.io/contracts/api/contracts.html#
    module-contracts.enabling>`_ function. From the PyContracts documentation:
    "Returns true if all contracts are disabled"
    """
    return contracts.all_disabled()


def disable_all():
    """
    Wraps PyContracts `disable_all()
    <http://andreacensi.github.io/contracts/api/contracts.html#
    module-contracts.enabling>`_ function. From the PyContracts documentation:
    "Disables all contract checks"
    """
    contracts.disable_all()


def enable_all():
    """
    Wraps PyContracts `enable_all()
    <http://andreacensi.github.io/contracts/api/contracts.html#
    module-contracts.enabling>`_ function. From the PyContracts documentation:
    "Enables all contract checks. Can be overridden by an environment variable"
    """
    contracts.enable_all()


def get_exdesc():
    """
    Retrieves the contract exception(s) message(s). If the custom contract is
    specified with only one exception the return value is the message
    associated with that exception; if the custom contract is specified with
    several exceptions, the return value is a dictionary whose keys are the
    exception names and whose values are the exception messages.

    :raises: RuntimeError (Function object could not be found for
     function *[function_name]*)
    :rtype: string or dictionary

    For example:

    .. =[=cog
    .. import docs.support.incfile
    .. docs.support.incfile.incfile('pcontracts_example_2.py', cog.out)
    .. =]=
    .. code-block:: python

        # pcontracts_example_2.py
        import putil.pcontracts

        @putil.pcontracts.new_contract('Only one exception')
        def custom_contract_a(name):
            msg = putil.pcontracts.get_exdesc()
            if not name:
                raise ValueError(msg)

        @putil.pcontracts.new_contract(ex1='Empty name', ex2='Invalid name')
        def custom_contract_b(name):
            msg = putil.pcontracts.get_exdesc()
            if not name:
                raise ValueError(msg['ex1'])
            elif name.find('[') != -1:
                raise ValueError(msg['ex2'])

    .. =[=end=]=


    In :code:`custom_contract1()` the variable :code:`msg` contains the string
    ``'Only one exception'``, in :code:`custom_contract2()` the variable
    :code:`msg` contains the dictionary
    :code:`{'ex1':'Empty name', 'ex2':'Invalid name'}`.

    """
    # First frame is own function (get_exdesc), next frame is the calling
    # function, of which its name is needed
    fname = inspect.getframeinfo(sys._getframe(1))[2]
    # Find function object in stack
    count = 0
    fobj = None
    while not (fobj and hasattr(fobj, 'exdesc')):
        count = count+1
        try:
            sitem = sys._getframe(count)
        except ValueError:
            # Got to top of stack
            raise RuntimeError(
                'Function object could not be found for function `{0}`'.format(
                    fname
                )
            )
        fobj = (
            sitem.f_locals[fname] if fname in sitem.f_locals else
            (sitem.f_globals[fname] if fname in sitem.f_globals else None)
        )
    # Return function attribute created by new contract decorator
    exdesc = getattr(fobj, 'exdesc')
    return exdesc if len(exdesc) > 1 else exdesc[next(iter(exdesc))]


def _get_num_contracts(contracts_list, param_name):
    """
    Returns the number of simple/default contracts (the ones which raise a
    RuntimeError with message 'Argument `*[argument_name]*` is not valid'
    """
    msg = 'Argument `*[argument_name]*` is not valid'
    return sum(
        [
            1
            if item['msg'] == msg.replace('*[argument_name]*', param_name) else
            0
            for item in contracts_list
        ]
    )


def _get_replacement_token(msg):
    """ Extract replacement token from exception message """
    return (
        None
        if not re.search(r'\*\[[\w|\W]+\]\*', msg) else
        re.search(r'\*\[[\w|\W]+\]\*', msg).group()[2:-2]
    )


def _parse_new_contract_args(*args, **kwargs):
    """ Parse argument for new_contract() function """
    # No arguments
    if (len(args) == 0) and (len(kwargs) == 0):
        return [
            {
                'name':'argument_invalid',
                'msg':'Argument `*[argument_name]*` is not valid',
                'type':RuntimeError
            }
        ]
    # Process args
    if (len(args) > 1) or ((len(args) == 1) and (len(kwargs) > 0)):
        raise TypeError('Illegal custom contract exception definition')
    elif len(args) == 1:
        return [dict([('name', 'default')]+list(_format_arg(args[0]).items()))]
    # Process kwargs
    return [
        dict([('name', name)]+list(_format_arg(kwargs[name]).items()))
        for name in sorted(list(kwargs.keys()))
    ]


def _register_custom_contracts(contract_name, contract_exceptions):
    """ Homogenize custom contract exception definition """
    # pylint: disable=W0602
    global _CUSTOM_CONTRACTS
    # Validate arguments and homogenize contract exceptions
    if not isinstance(contract_name, str):
        raise TypeError('Argument `contract_name` is of the wrong type')
    # A contract exception can be a string (only one exception, default
    # exception type) or a dictionary of exception definitions, if there is
    # more than one or if the type if different than the default
    if ((not isinstance(contract_exceptions, list)) and
       (not isinstance(contract_exceptions, str)) and
       (not isinstance(contract_exceptions, dict))):
        raise TypeError('Argument `contract_exceptions` is of the wrong type')
    if isinstance(contract_exceptions, dict):
        contract_exceptions = [contract_exceptions]
    if (isinstance(contract_exceptions, list) and
       any([not isinstance(key, str) for item in contract_exceptions
       for key in item.keys()])):
        raise TypeError('Contract exception definition is of the wrong type')
    # Validate individual exception definitions
    if (isinstance(contract_exceptions, list) and
       any([not ((set(item.keys()) == set(['name', 'msg'])) or
       (set(item.keys()) == set(['name', 'msg', 'type'])))
       for item in contract_exceptions])):
        raise TypeError('Contract exception definition is of the wrong type')
    extype = type(ValueError)
    if (isinstance(contract_exceptions, list) and
       any([(not isinstance(item['name'], str)) or
       (not isinstance(item['msg'], str)) or
       (not isinstance(item.get('type', extype), extype))
       for item in contract_exceptions])):
        raise TypeError('Contract exception definition is of the wrong type')
    # Homogenize exception definitions
    if isinstance(contract_exceptions, list):
        homogenized_exdict = dict(
            (
                exdict['name'], {
                    'num':exnum,
                    'msg':exdict['msg'],
                    'type':exdict.get('type', RuntimeError),
                    'field':_get_replacement_token(exdict['msg'])
                }
            ) for exnum, exdict in enumerate(contract_exceptions)
        )
    else:
        homogenized_exdict = {
            'default':{
                'num':0,
                'msg':contract_exceptions,
                'type':RuntimeError,
                'field':_get_replacement_token(contract_exceptions)
            }
        }
    # Verify exception names are unique
    if (isinstance(contract_exceptions, list) and
       (len(homogenized_exdict) != len(contract_exceptions))):
        raise ValueError('Contract exception names are not unique')
    # Verify that exception messages are unique
    msgs = [exvalue['msg'] for exvalue in homogenized_exdict.values()]
    if len(set(msgs)) != len(msgs):
        raise ValueError('Contract exception messages are not unique')
    # Verify that a custom contract is not being redefined
    if ((contract_name in _CUSTOM_CONTRACTS) and
       (_CUSTOM_CONTRACTS[contract_name] != contract_exceptions)):
        raise RuntimeError(
            'Attempt to redefine custom contract `{0}`'.format(contract_name)
        )
    # Verify that there are at most only two replacement fields, and one of
    # them should be argument_name
    fields = [
        exdict['field'] for exdict in homogenized_exdict.values()
        if exdict['field'] is not None
    ]
    if ((len(fields) > 2) or
       ((len(fields) == 2) and (fields[0] != 'argument_name') and
       (fields[1] != 'argument_name'))):
        raise ValueError(
            'Multiple replacement fields to be substituted by argument value'
        )
    # Register new contract
    _CUSTOM_CONTRACTS[contract_name] = homogenized_exdict
    return contract_exceptions


###
# Decorators
###
# Function docstring in rst documentation
def contract(**contract_args):
    # pylint: disable=W0631
    @decorator.decorator
    def wrapper(func, *args, **kwargs):
        """ Decorator """
        # Register exceptions if exception handler object exists
        if all_disabled():
            return func(*args, **kwargs)
        exhobj = putil.exh.get_exh_obj()
        exdata = {}
        if exhobj is not None:
            for param_name, param_contract in contract_args.items():
                # param_name=param_value, as in num='str|float'
                contracts_dicts = list()
                # Create dictionary of custom contracts
                if _get_custom_contract(param_contract):
                    key = _get_custom_contract(param_contract)
                    contracts_dicts += _CUSTOM_CONTRACTS[key].values()
                else: # Add regular PyContracts contracts
                    msg = 'Argument `*[argument_name]*` is not valid'
                    contracts_dicts += [
                        {
                            'num':_get_num_contracts(
                                contracts_dicts, param_name
                            ),
                            'type':RuntimeError,
                            'msg':msg.replace(
                                '*[argument_name]*', param_name
                            )
                        }
                    ]
                func_module = (
                    getattr(func, '__module__')
                    if hasattr(func, '__module__') else
                    'unknown'
                )
                for exdict in contracts_dicts:
                    exname = 'contract:{0}.{1}_{2}'.format(
                        '{0}.{1}'.format(func_module, func.__name__),
                        param_name,
                        exdict['num']
                    )
                    exdata[exname] = exhobj.add_exception(
                        exname=exname,
                        extype=exdict['type'],
                        exmsg=exdict['msg'].replace(
                            '*[argument_name]*',
                            param_name
                        )
                    )
        # Argument validation. PyContracts "entry" is the
        # contracts.contract_decorator, which has some logic to figure out
        # which way the contract was specified. Since this module
        # (pcontracts) supports only the decorator way of specifying the
        # contracts, all the mentioned logic can be bypassed by calling
        # contracts.contracts_decorate, which is renamed to
        # contracts.decorate in the contracts __init__.py file
        try:
            return (
                contracts.decorate(
                    func,
                    False,
                    **contract_args
                )(*args, **kwargs)
            )
        except contracts.ContractSyntaxError:
            raise
        except contracts.ContractNotRespected as eobj:
            # Extract which function parameter triggered exception
            param_dict = _create_argument_value_pairs(
                func, *args, **kwargs
            )
            # re.search returns the string with quotes in it
            param_name = re.search(r"'\w+'", eobj.error).group()[1:-1]
            # Raise exception
            exdict = _get_contract_exception_dict(eobj.error)
            func_module = (
                getattr(func, '__module__')
                if hasattr(func, '__module__') else
                'unknown'
            )
            exname = 'contract:{0}.{1}_{2}'.format(
                '{0}.{1}'.format(func_module, func.__name__),
                param_name,
                exdict['num']
            )
            efield = exdict['field']
            edata = (
                {'field':efield, 'value':param_dict[param_name]}
                if (efield and (efield != 'argument_name')) else
                None
            )
            if exhobj is not None:
                exhobj.raise_exception_if(
                    exname=exname,
                    condition=True,
                    edata=edata,
                    _keys=exdata[exname]
                )
            else:
                # Pick "nice" variable names because the raise line is
                # going to be shown in the exception traceback
                exception_type = exdict['type']
                exception_message = exdict['msg'].replace(
                    '*[{0}]*'.format(exdict['field']),
                    param_name if exdict['field'] == 'argument_name' else
                    '{0}'.format(param_dict[param_name])
                )
                _raise_exception(exception_type(exception_message))
    return wrapper

def new_contract(*args, **kwargs):
    def wrapper(func):
        """ Decorator """
        contract_name = func.__name__
        exdesc = _parse_new_contract_args(*args, **kwargs)
        # Pass to the custom contract, via a property, only the
        # exception descriptions
        func.exdesc = dict(
            (
                value['name'],
                (
                    '[START CONTRACT MSG: {0}]{1}'
                    '[STOP CONTRACT MSG]'.format(
                        contract_name, value['msg']
                    )
                )
            ) for value in exdesc
        )
        # Register custom contract
        _register_custom_contracts(contract_name, exdesc)
        # Apply PyContracts decorator
        return contracts.new_contract(func)
    return wrapper

if RTD: # pragma: no cover
    def contract(**contract_args):
        @decorator.decorator
        def wrapper(func, *args, **kwargs):
            return func
        return wrapper

    def new_contract(*args, **kwargs):
        def wrapper(func):
            return func
        return wrapper
