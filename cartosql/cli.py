'''
Utility library for interacting with CARTO via the SQL API

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

'''
# Python 2
try: input = raw_input
except: pass

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
    if args['--help'] or not cartosql.init():
        return __doc__
    if args['<sql>']:
        if args['post']:
            r = cartosql.post(args['<sql>'], **opts)
            return returnFormat(r, f)
        elif args['get']:
            r = cartosql.get(args['<sql>'], **opts)
            return returnFormat(r, f)
    elif args['select']:
        if args['<fields>'] and args['<table>']:
            if args['-w']:
                opts['where'] = args['-w']
            if args['-o']:
                opts['order'] = args['-o']
            if args['-l']:
                opts['limit'] = args['-l']
            r = cartosql.getFields(args['<fields>'], args['<table>'], **opts)
            return returnFormat(r, f)
    elif args['ls']:
        r = cartosql.getTables(**opts)
        if f is None or f == 'csv':
            return prettyJson(r)
        return returnFormat(r, f)
    elif args['exists'] and args['<table>']:
        r = cartosql.tableExists(args['<table>'], **opts)
        return r
    elif args['drop'] and args['<table>']:
        confirm = args['--confirm']
        if not confirm:
            confirm = input('Drop table {}? (y/N)'.format(args['<table>'])) == 'y'
        if confirm:
            r = cartosql.dropTable(args['<table>'], **opts)
            return returnFormat(r, f)
        else:
            print('Pass option --confirm to drop table')
    elif args['getacl'] and args['<table>']:
        from cartosql import dataset
        return dataset.getProperties(args['<table>'])['privacy']
    elif args['setacl'] and args['<table>']:
        acl = None
        if args['--public']:
            acl = 'PUBLIC'
        elif args['--private']:
            acl = 'PRIVATE'
        elif args['--link']:
            acl = 'LINK'
        if acl:
            from cartosql import dataset
            return dataset.setPrivacy(args['<table>'], acl)
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
