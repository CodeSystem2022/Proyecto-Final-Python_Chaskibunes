.. README.rst
.. Copyright (c) 2013-2016 Pablo Acosta-Serafini
.. See LICENSE for details


.. image:: https://badge.fury.io/py/putil.svg
    :target: https://pypi.python.org/pypi/putil
    :alt: PyPI version

.. image:: https://img.shields.io/pypi/l/putil.svg
    :target: https://pypi.python.org/pypi/putil
    :alt: License

.. image:: https://img.shields.io/pypi/pyversions/putil.svg
    :target: https://pypi.python.org/pypi/putil
    :alt: Python versions supported

.. image:: https://img.shields.io/pypi/format/putil.svg
    :target: https://pypi.python.org/pypi/putil
    :alt: Format

|

.. image::
   https://travis-ci.org/pmacosta/putil.svg?branch=master

.. image::
   https://ci.appveyor.com/api/projects/status/
   7dpk342kxs8kcg5t/branch/master?svg=true
   :alt: Windows continuous integration

.. image::
   https://codecov.io/github/pmacosta/putil/coverage.svg?branch=master
   :target: https://codecov.io/github/pmacosta/putil?branch=master
   :alt: Continuous integration coverage

.. image::
   https://readthedocs.org/projects/pip/badge/?version=stable
   :target: http://pip.readthedocs.org/en/stable/?badge=stable
   :alt: Documentation status

|

Putil Library
=============

This package has been broken off into smaller modules and packages. Development
continues in these with enhancements, bug fixes and additions as warranted.

* The **eng** module is the base of the
  `peng <https://pypi.python.org/pypi/peng>`_ package

* The **exdoc**, **exh**, **pcontracts**, **pinspect** and part of the
  **ptypes** module are the base of the
  `pexdoc <https://pypi.python.org/pypi/pexdoc>`_ package

* The **misc** and **test** modules are the base of the
  `pmisc <https://pypi.python.org/pypi/pmisc>`_ package

* The **pcsv** module and part of the **ptypes** module are the base of the
  `pcsv <https://pypi.python.org/pypi/pcsv>`_ package

* The **plot** module and part of the **ptypes** module are the base of the
  `pplot <https://pypi.python.org/pypi/pplot>`_ package

* The **tree** module is the base of the
  `ptrie <https://pypi.python.org/pypi/ptrie>`_ package


License
=======

The MIT License (MIT)

Copyright (c) 2013-2016 Pablo Acosta-Serafini

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
.. CHANGELOG.rst
.. Copyright (c) 2013-2016 Pablo Acosta-Serafini
.. See LICENSE for details

Changelog
=========

* 0.9.12 [2016-05-16]: Broke off package into smaller modules and packages

* 0.9.11 [2016-04-15]:

  * Created new APIs in the exh module to simplify adding and conditionally
    raising exceptions that can be auto-documented with the exdoc module

  * Homogenized API arguments in several pcsv module functions

  * Bug fixes

  * Documentation updates

* 0.9.10 [2016-03-10]: Final release of 0.9.10 branch
* 0.9.10rc1 [2016-03-09]: Apple OS X compatibility changes. Reduced memory
  consumption during exception auto-documentation process. Bug fixes
* 0.9.9 [2016-01-27]: Fixed documentation bugs that were causing errors with
  Sphinx 1.3.5+
* 0.9.8 [2016-01-22]: Bug fixes
* 0.9.7 [2016-01-22]: Enhanced control of exceptions automatic documentation
  output
* 0.9.6 [2016-01-20]: Bug fixes
* 0.9.5 [2016-01-08]: Bug fixes
* 0.9.4 [2015-12-18]: Minor documentation update regarding continuous
  integration setup
* 0.9.3 [2015-12-17]: Fixed critical bug in plot module that prevented figures
  without any axis labels from being generated
* 0.9.2 [2015-12-15]: Speed improvements in plot module
* 0.9.1 [2015-12-01]: Final release of 0.9.1 branch
* 0.9.1rc5 [2015-12-01]: Fixed documentation URL in top-level README.rst
* 0.9.1rc4 [2015-12-01]: Fixed bug in top-level README.rst verification
* 0.9.1rc3 [2015-12-01]:

  * Documentation updates

  * Package verification improvements

* 0.9.1rc2 [2015-12-01]: Fixed top-level README.rst file
* 0.9.1rc1 [2015-11-30]: Initial public release


