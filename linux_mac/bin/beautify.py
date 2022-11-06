#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json
import os

class Beautify:

    def __init__(self) -> None:
        pass

    def beautify(self, args):
        ''' Reformats a JSON string and makes it nicer and easier to read

            Options:
            * File: <path to file> - The file to be beautified
            * Output: <file> - The file to output to
            * Indent: <int>, default: 4
            * sort_keys: <bool>, default: False
        '''
        obj = None
        try:
            with open(args.file, 'r') as f:
                obj = json.load(f)
        except Exception as e:
            print(e)
            return
        
        try:
            with open(args.output, 'w') as f:
                json.dump(obj, f, indent=args.indent, sort_keys=args.sort_keys)
        except Exception as e:
            print(e)
            return
        



def main():
    beautify = Beautify()

    parser = argparse.ArgumentParser(description='Beautify JSON files')
    subparsers = parser.add_subparsers(help='sub-command help')

    client = subparsers.add_parser('beautify', help='Beautify JSON files')
    client.add_argument('file', help='File to beautify')
    client.add_argument('-i', '--indent', help='Indentation', default=4)
    client.add_argument('-s', '--sort-keys', help='Sort keys', action='store_true')
    client.set_defaults(func=beautify.beautify)

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()