Installation
=============

Before installing Distance Closure, verify that you have
`setuptools <https://pypi.python.org/pypi/setuptools>`_ installed.


Quick Install
--------------

The easiest way to install this package is with pip.
Run the following command in your terminal:

.. code-block:: bash

	$pip install distanceclosure


Source code
------------

The latest development release and source code is available on GitHub at `github.com/rionbr/distanceclosure <https://github.com/rionbr/distanceclosure>`_ and can be installed with the command:

.. code-block:: bash

	$pip install git+git://github.com/rionbr/distanceclosure.

You can also download stable releases from the Python Package Index (Pypi) at
https://pypi.python.org/pypi/distanceclosure.


Requirements
-------------

- **Python 3**: The latest release of :doc:`DistanceClosure <index>` is built on Python 3.
- **Cython**: Some functions have been cythonized for efficiency. https://cython.org/
- **NetworkX**: Whenever possible we use NetworkX Graphs for handling networks. https://networkx.org/
- **NumPy**: Provides matrix representation of graphs and is used in some graph algorithms for high-performance matrix computations. http://scipy.org
- **SciPy**: Provides sparse matrix representation of graphs and many numerical scientific tools. http://scipy.org
- **Pandas**: Provides easy handling of large data tables and formats. http://pandas.pydata.org

.. note:: 
	All requirements are automatically satisfied if you have an Anaconda installation.