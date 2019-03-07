# SRV resolver

[![PyPI version](https://badge.fury.io/py/srvresolver.svg)](https://pypi.python.org/pypi/srvresolver/) [![PyPI license](https://img.shields.io/pypi/l/srvresolver.svg)](https://pypi.python.org/pypi/srvresolver/) [![PyPI format](https://img.shields.io/pypi/format/srvresolver.svg)](https://pypi.python.org/pypi/srvresolver/)

Helper to get record from SRV address according to [RFC2782](https://tools.ietf.org/html/rfc2782).

## Features

* support of record weights and priorities
* check service availability at specific port
* random record selector
* cache with ttl support

## Install

The package can be installed simply by using `pip`:

```sh
pip install srvresolver
```

## Example

```python
from srvresolver.srv_resolver import SRVResolver

# get all records
SRVResolver.resolve('_service._tcp.example.com')

# get one random record with working connection 
SRVResolver.resolve_random('_service._tcp.example.com')

# get first available server
SRVResolver.resolve_first('_service._tcp.example.com')
```

## Adds

### Resolver with DNS cache

This one uses cache implemented in dnspython module.

```python
from srvresolver.srv_resolver_cached import SRVResolverCached

# get all records
SRVResolverCached.resolve('_service._tcp.example.com')
# same but don't do dns request, load from cache if not expired
SRVResolverCached.resolve('_service._tcp.example.com')
```

### Postgres SRV record resolver

Extract postgres records from SRV and check whether master or slave. Requires `psycopg2`

```python
from srvresolver.postgres_resolver import PostgresResolver

# get random working slave record
PostgresResolver.get_slave('_postgresql._tcp.example.com', username, password)

# get random working master record
PostgresResolver.get_master('_postgresql._tcp.example.com', username, password)
```
