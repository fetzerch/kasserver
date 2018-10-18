.. image:: https://travis-ci.org/fetzerch/kasserver.svg?branch=master
    :target: https://travis-ci.org/fetzerch/kasserver
    :alt: Travis CI Status

.. image:: https://coveralls.io/repos/github/fetzerch/kasserver/badge.svg?branch=master
    :target: https://coveralls.io/github/fetzerch/kasserver?branch=master
    :alt: Coveralls Status

.. image:: https://img.shields.io/pypi/v/kasserver.svg
    :target: https://pypi.org/project/kasserver
    :alt: PyPI Version

kasserver - Manage domains hosted on All-Inkl.com through the KAS server API
============================================================================

This project consists of the Python library *kasserver* and a few
command line utilities to manage domains of the German webhoster
`All-Inkl.com`_ through their `KAS server API`_.

At the moment the main focus is managing DNS record as this allows to
automate the creation of `Let’s Encrypt`_ (wildcard) certificates with
the `ACME DNS-01 challenge`_.

Installation
------------

*kasserver* (and its dependencies) can be installed from PyPI with:
``pip3 install kasserver``

Authentication
--------------

Both library and command line utilities require access to the KAS
credentials. Username and password are read from the ``KASSERVER_USER``
and ``KASSERVER_PASSWORD`` environment variables or from the
``~/.netrc`` file:

.. code:: console

   machine kasapi.kasserver.com
   login USERNAME
   password PASSWORD

The file must be accessible only by your user account:
``chmod 600 ~/.netrc``.

Scripts
-------

``kasserver-dns``
~~~~~~~~~~~~~~~~~

A generic program to manage DNS records.

DNS records can be listed with:

.. code:: console

   $ kasserver-dns list example.com
   ID C Zone        Name Type  Data               Aux
    1 Y example.com      A     X.X.X.X            0
    0 N example.com      NS    ns5.kasserver.com. 0
    0 N example.com      NS    ns6.kasserver.com. 0
    0 N example.com www  CNAME example.com        0

A new DNS record is added with:

.. code:: console

   kasserver-dns add test.example.com CNAME example.com

An existing DNS record is removed with:

.. code:: console

   kasserver-dns remove test.example.com CNAME

``kasserver-dns-*``
~~~~~~~~~~~~~~~~~~~

The following programs are designed to be used together with ACME
clients to automate DNS record creation/removal as it is required by a
Let’s Encryt `ACME DNS-01 challenge`_ for automatic certificate renewal.

``kasserver-dns-certbot``
^^^^^^^^^^^^^^^^^^^^^^^^^

This program is designed to be used with `Certbot`_:

.. code:: console

   certbot certonly -d foo.exmaple.com --preferred-challenges dns \
                    --manual --manual-auth-hook kasserver-dns-certbot \
                             --manual-cleanup-hook kasserver-dns-certbot \
                    -m invalid@example.com

``kasserver-dns-lego``
^^^^^^^^^^^^^^^^^^^^^^

This program is designed to be used with `lego`_:

.. code:: console

   EXEC_PATH=kasserver-dns-lego lego --dns exec \
       --domains foo.example.com --email invalid@example.com run

License
-------

This projected is licensed under the terms of the MIT license.

.. _All-Inkl.com: https://all-inkl.com/
.. _KAS server API: https://kasapi.kasserver.com/
.. _Let’s Encrypt: https://letsencrypt.org
.. _ACME DNS-01 challenge: https://www.eff.org/de/deeplinks/2018/02/technical-deep-dive-securing-automation-acme-dns-challenge-validation
.. _Certbot: https://certbot.eff.org
.. _lego: https://github.com/xenolf/lego
