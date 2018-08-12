'''
Utility library for interacting with CARTO via the SQL API

Example:
```
import cartosql

# CARTO_USER and CARTO_KEY read from environment if not specified
r = cartosql.get('select * from mytable', user=CARTO_USER, key=CARTO_KEY)

data = r.json()
```

Read more at:
http://carto.com/docs/carto-engine/sql-api/making-calls/
'''
from __future__ import unicode_literals
try: from builtins import str
except: from __builtin__ import str
try: string_types = (str, basestring)
except: string_types = str

import requests
import os
import logging
import json

CARTO_URL = 'https://{}.carto.com/api/v2/sql'
CARTO_USER = os.environ.get('CARTO_USER')
CARTO_KEY = os.environ.get('CARTO_KEY')

def init(user=None, key=None):
    '''Set user and key'''
    global CARTO_USER, CARTO_KEY
    CARTO_USER = user or os.environ.get('CARTO_USER')
    CARTO_KEY = key or os.enviorn.get('CARTO_KEY')

def sendSql(sql, user=None, key=None, f='', post=True):
    '''Send arbitrary sql and return response object or False'''
    user = user or CARTO_USER
    key = key or CARTO_KEY
    url = CARTO_URL.format(user)
    payload = {
        'api_key': key,
        'q': sql,
    }
    if len(f):
        payload['format'] = f
    logging.debug((url, payload))
    if post:
        r = requests.post(url, json=payload)
    else:
        r = requests.get(url, params=payload)
    r.raise_for_status()
    return r


def get(sql, user=None, key=None, f=''):
    '''Send arbitrary sql and return response object or False'''
    return sendSql(sql, user, key, f, False)


def post(sql, user=None, key=None, f=''):
    '''Send arbitrary sql and return response object or False'''
    return sendSql(sql, user, key, f)


def getFields(fields, table, where='', order='', limit='', user=None,
              key=None, f='', post=True):
    '''Select fields from table'''
    fields = fields.split(',') if isinstance(fields, string_types) else fields
    where = 'WHERE {}'.format(where) if where else ''
    order = 'ORDER BY {}'.format(order) if order else ''
    limit = 'LIMIT {}'.format(limit) if limit else ''
    sql = 'SELECT {} FROM "{}" {} {} {}'.format(
        ','.join(fields), table, where, order, limit)
    return sendSql(sql, user, key, f, post)

def getTables(user=None, key=None, f='csv'):
    '''Get the list of tables'''
    r = get('SELECT * FROM CDB_UserTables()', user, key, f)
    if f == 'csv':
        return r.text.splitlines()[1:-1]
    return r


def tableExists(table, user=None, key=None):
    '''Check if table exists'''
    return table in getTables(user, key)


def createTable(table, schema, user=None, key=None):
    '''
    Create table with schema and CartoDBfy table

    `schema` should be a dict or list of tuple pairs with
     - keys as field names and
     - values as field types
    '''
    items = schema.items() if isinstance(schema, dict) else schema
    defslist = ['{} {}'.format(k, v) for k, v in items]
    sql = 'CREATE TABLE "{}" ({})'.format(table, ','.join(defslist))
    if post(sql, user, key):
        return _cdbfyTable(table, user, key)
    return False

def createTableFromQuery(table, query, user=None, key=None):
    '''
    Create table with from query and CartoDBfy table
    '''
    sql = 'CREATE TABLE "{}" AS {}'.format(table, query)
    if post(sql, user, key):
        return _cdbfyTable(table, user, key)
    return False


def _cdbfyTable(table, user=None, key=None):
    '''CartoDBfy table so that it appears in Carto UI'''
    sql = "SELECT cdb_cartodbfytable('{}','\"{}\"')".format(user, table)
    return post(sql, user, key)


def createIndex(table, fields, unique='', using='', user=None,
                key=None):
    '''Create index on table on field(s)'''
    fields = (fields,) if isinstance(fields, string_types) else fields
    f_underscore = '_'.join(fields)
    f_comma = ','.join(fields)
    unique = 'UNIQUE' if unique else ''
    using = 'USING {}'.format(using) if using else ''
    sql = 'CREATE {} INDEX idx_{}_{} ON {} {} ({})'.format(
        unique, table, f_underscore, table, using, f_comma)
    return post(sql, user, key)


def _escapeValue(value, dtype):
    '''
    Escape value for SQL based on field type

    TYPE         Escaped
    None      -> NULL
    geometry  -> string as is; obj dumped as GeoJSON
    text      -> single quote escaped
    timestamp -> single quote escaped
    varchar   -> single quote escaped
    else      -> as is
    '''
    if value is None:
        return "NULL"
    if dtype == 'geometry':
        # if not string assume GeoJSON and assert WKID
        if isinstance(value, string_types):
            return value
        else:
            value = json.dumps(value)
            return "ST_SetSRID(ST_GeomFromGeoJSON('{}'),4326)".format(value)
    elif dtype in ('text', 'timestamp', 'varchar'):
        # quote strings, escape quotes, and drop nbsp
        return "'{}'".format(
            str(value).replace("'", "''"))
    else:
        return str(value)


def _dumpRows(rows, dtypes):
    '''Escapes rows of data to SQL strings'''
    dumpedRows = []
    for row in rows:
        escaped = [
            _escapeValue(row[i], dtypes[i])
            for i in range(len(dtypes))
        ]
        dumpedRows.append('({})'.format(','.join(escaped)))
    return ','.join(dumpedRows)


def _insertRows(table, fields, dtypes, rows, user=None, key=None):
    values = _dumpRows(rows, tuple(dtypes))
    sql = 'INSERT INTO "{}" ({}) VALUES {}'.format(
        table, ', '.join(fields), values)
    return post(sql, user, key)


def insertRows(table, fields, dtypes, rows, user=None,
               key=None, blocksize=1000):
    '''
    Insert rows into table

    `rows` must be a list of lists containing the data to be inserted
    `fields` field names for the columns in `rows`
    `dtypes` field types for the columns in `rows`

    Automatically breaks into multiple requests at `blocksize` rows
    '''
    # iterate in blocks
    while len(rows):
        if not _insertRows(table, fields, dtypes, rows[:blocksize], user, key):
            return False
        rows = rows[blocksize:]
    return True

# Alias insertRows
blockInsertRows = insertRows


def deleteRows(table, where, user=None, key=None):
    '''Delete rows from table'''
    sql = 'DELETE FROM "{}" WHERE {}'.format(table, where)
    return post(sql,user, key)


def deleteRowsByIDs(table, ids, id_field='cartodb_id', dtype='',
                    user=None, key=None):
    '''Delete rows from table by IDs'''
    if dtype:
        ids = [_escapeValue(i, dtype) for i in ids]
    where = '{} in ({})'.format(id_field, ','.join(ids))
    return deleteRows(table, where, user, key)


def dropTable(table, user=None, key=None):
    '''Delete table'''
    sql = 'DROP TABLE "{}"'.format(table)
    return post(sql, user, key)

def truncateTable(table, user=None, key=None):
    '''Delete table'''
    sql = 'TRUNCATE TABLE "{}"'.format(table)
    return post(sql,user, key)

if __name__ == '__main__':
    from . import cli
    cli.main()
