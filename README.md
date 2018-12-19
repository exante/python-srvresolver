# SRV resolver

Helper to get record from SRV address according to [RFC2782](https://tools.ietf.org/html/rfc2782).

## Features

* support of record weights and priorities
* check service availability at specific port
* random record selector

## TODO

* dns cache support

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

### Postgres SRV record resolver

Extract postgres records from SRV and check whether master or slave. Requires `psycopg2`

```python
from srvresolver.postgres_resolver import PostgresResolver

resolver = PostgresResolver(database, username, password)

# get random working slave record
resolver.get_slave('_postgresql._tcp.example.com')

# get random working master record
resolver.get_master('_postgresql._tcp.example.com')
```