[![Build Status](https://github.com/fetzerch/kasserver/actions/workflows/check.yml/badge.svg)](https://github.com/fetzerch/kasserver/actions/workflows/check.yml)
[![Coverage Status](https://coveralls.io/repos/github/fetzerch/kasserver/badge.svg)](https://coveralls.io/github/fetzerch/kasserver)
[![PyPI Version](https://img.shields.io/pypi/v/kasserver.svg)](https://pypi.org/project/kasserver)

# kasserver - Manage domains hosted on All-Inkl.com through the KAS server API

This project consists of the Python library *kasserver* and a few command line
utilities to manage domains of the German webhoster [All-Inkl.com] through
their [KAS server API].

At the moment the main focus is managing DNS record as this allows to automate
the creation of [Let's Encrypt] (wildcard) certificates with the
[ACME DNS-01 challenge].

## Installation

*kasserver* (and its dependencies) can be installed from PyPI with:
`pip3 install kasserver`

## Authentication

Both library and command line utilities require access to the KAS credentials.
Username and password are read from the `KASSERVER_USER` and
`KASSERVER_PASSWORD` environment variables or from the `~/.netrc` file:

```console
machine kasapi.kasserver.com
login USERNAME
password PASSWORD
```

The file must be accessible only by your user account: `chmod 600 ~/.netrc`.

## Scripts

### `kasserver-dns`

A generic program to manage DNS records.

DNS records can be listed with:

```console
$ kasserver-dns list example.com
ID C Zone        Name Type  Data               Aux
 1 Y example.com      A     X.X.X.X            0
 0 N example.com      NS    ns5.kasserver.com. 0
 0 N example.com      NS    ns6.kasserver.com. 0
 0 N example.com www  CNAME example.com        0
```

A new DNS record is added with:

```console
kasserver-dns add test.example.com CNAME example.com
```

An existing DNS record is removed with:

```console
kasserver-dns remove test.example.com CNAME
```

### `kasserver-dns-*`

The following programs are designed to be used together with ACME clients to
automate DNS record creation/removal as it is required by a Let's Encryt
[ACME DNS-01 challenge] for automatic certificate renewal.

#### `kasserver-dns-certbot`

This program is designed to be used with [Certbot]:

```console
certbot certonly -d foo.exmaple.com --preferred-challenges dns \
                 --manual --manual-auth-hook kasserver-dns-certbot \
                          --manual-cleanup-hook kasserver-dns-certbot \
                 -m invalid@example.com
```

#### `kasserver-dns-lego`

This program is designed to be used with [lego]:

```console
EXEC_PATH=kasserver-dns-lego lego --dns exec \
    --domains foo.example.com --email invalid@example.com run
```

## License

This projected is licensed under the terms of the MIT license.

[acme dns-01 challenge]: https://www.eff.org/de/deeplinks/2018/02/technical-deep-dive-securing-automation-acme-dns-challenge-validation
[all-inkl.com]: https://all-inkl.com/
[certbot]: https://certbot.eff.org
[kas server api]: https://kasapi.kasserver.com/
[lego]: https://github.com/xenolf/lego
[let's encrypt]: https://letsencrypt.org/
