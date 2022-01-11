========================
XLM-Tools plugin
========================

This plugin provide wrappers around several programs of `XLM-Tool <https://github.com/Topf-Lab/XLM-Tools>`_.

+------------------+------------------+
| stable: |stable| | devel: | |devel| |
+------------------+------------------+

.. |stable| image:: http://scipion-test.cnb.csic.es:9980/badges/eman2_prod.svg
.. |devel| image:: http://scipion-test.cnb.csic.es:9980/badges/eman2_sdevel.svg


Installation
------------

You will need to use `3.0 <https://github.com/I2PC/scipion/releases/tag/V3.0.0>`_ version of Scipion to be able to run these protocols. To install the plugin, you have two options:

a) Stable version (not avalaible yet)

.. code-block::

    scipion installp -p scipion-em-xlmtools

b) Developer's version

    * download repository

    .. code-block::

        git clone https://github.com/scipion-em/scipion-em-xlmtools.git

    * install

    .. code-block::

        scipion installp -p path_to_scipion-em-xlmtools --devel

XML-Tools binaries will be installed automatically with the plugin.

To check the installation, simply run one of the following Scipion tests:

.. code-block::

   scipion3 tests xlmtools.tests.test_protocols_xlm.TestWLM

A complete list of tests can also be seen by executing ``scipion test --show --grep xlmtools``

Supported versions
------------------

* 1.0

Protocols
---------

* XLM Tools protocol

References
----------

1. Sinnott et al., Combining Information from Crosslinks and Monolinks in the Modeling of Protein Structures, Sturcture (2020), https://doi.org/10/1016/j.str.2020.05.012
