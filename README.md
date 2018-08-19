# CartoSQL.py

Simple utility library for interacting with the [CARTO SQL API](http://carto.com/docs/carto-engine/sql-api/making-calls/).

Example:

```
import cartosql

# CARTO_USER and CARTO_KEY read from environment if not specified
r = cartosql.get('select * from mytable', user=CARTO_USER, key=CARTO_KEY)

data = r.json()
```

__Install__

`pip install -e git+https://github.com/fgassert/cartosql.py.git#egg=cartosql`

__Develop__

```
git clone https://github.com/fgassert/cartosql.py.git
cd cartosql
pip install -e .
```

### CLI

```
Usage:
 csql (post|get) [options] <sql>
 csql select [options] <fields> <table> [-w <where>] [-o <order>] [-l <limit>]
 csql ls [options]
 csql exists [options] <table>
 csql drop [options] [--confirm] <table>
 csql getacl <table>
 csql setacl (--public|--link|--private) <table>

Options:
 -h --help    Print this text
 -u <user>    Carto user (default: read from env CARTO_USER)
 -k <key>     Carto API key (default: read from env CARTO_KEY)
 -s           Silence output
 -v           Increase verbosity
 -f <format>  Response format (default: json)
Other:
 -w <where>   Adds 'WHERE <where>' clause
 -o <order>   Adds 'ORDER BY <order>' clause
 -l <limit>   Adds 'LIMIT <limit>' clause
```
