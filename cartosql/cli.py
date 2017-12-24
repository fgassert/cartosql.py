'''
Utility library for interacting with CARTO via the SQL API

Usage:
 csql post <sql> [options]
 csql get <sql> [options]
 csql get <fields> <table> [-w <where>] [-o <order>] [options]
 csql ls [options]
 csql exists <table> [options]
 csql drop <table> [options]

Options:
 -h --help   Print this text
 -u <user>   Carto user (default: read from env CARTO_USER)
 -k <key>    Carto API key (default: read from env CARTO_KEY)
 -s          Silence output
 -v          Increase verbosity
 -f <format> Response format (default: json)
Other:
 -w <where>  Adds WHERE clause
 -o <order>  Adds ORDER BY clause

'''
import cartosql
import logging
from docopt import docopt
import json


def prettyJson(obj):
    return json.dumps(obj, sort_keys=True, indent=4)


def returnFormat(response, f=None):
    if f == 'json' or f is None:
        return prettyJson(response.json())
    else:
        return response.text


def processArgs(args):
    opts = {}
    if args['-u']:
        opts['user'] = args['-u']
    if args['-k']:
        opts['key'] = args['-k']
    f = args['-f']
    if f:
        opts['f'] = f
    if args['--help']:
        return __doc__
    elif args['post'] and args['<sql>']:
        r = cartosql.post(args['<sql>'], **opts)
        return returnFormat(r, f)
    elif args['get']:
        if args['<sql>']:
            r = cartosql.get(args['<sql>'], **opts)
            return returnFormat(r, f)
        if args['<fields>'] and args['<table>']:
            if args['-w']:
                opts['where'] = args['-w']
            if args['-o']:
                opts['order'] = args['-o']
            r = cartosql.getFields(args['<fields>'], args['<table>'], **opts)
            return returnFormat(r, f)
    elif args['ls']:
        r = cartosql.getTables(**opts)
        if f is None or f == 'csv':
            return prettyJson(r)
        return returnFormat(r, f)
    elif args['exists'] and args['<table>']:
        r = cartosql.tableExists(args['<table>'], **opts)
        return returnFormat(r, f)
    elif args['drop'] and args['<table>']:
        r = cartosql.dropTable(args['<table>'], **opts)
        return returnFormat(r, f)
    return __doc__


def main(args=None):
    args = docopt(__doc__, args)
    if args['-v']:
        logging.getLogger().setLevel(logging.DEBUG)
    if args['-s']:
        logging.getLogger().setLevel(logging.WARNING)
    r = processArgs(args)
    if not args['-s']:
        print(r)


if __name__ == "__main__":
    main()
