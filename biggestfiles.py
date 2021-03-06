#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""List the biggest files.

:Copyright: 2008-2014 Jochen Kupperschmidt
:Date: 10-Jul-2014 (original release: 20-Apr-2008)
:License: MIT
"""

from __future__ import print_function
from argparse import ArgumentParser
from collections import namedtuple
try:
    reduce  # Python 2
except NameError:
    from functools import reduce  # Python 3
from pathlib import Path
from operator import attrgetter
import os


FileInfo = namedtuple('FileInfo', ['path', 'size'])


def parse_args():
    """Parse command line arguments."""
    parser = ArgumentParser(description='List the biggest files.')

    parser.add_argument(
        'path',
        metavar='PATH')

    parser.add_argument(
        '-m', '--max-files',
        dest='max_files',
        type=int,
        default=10,
        help='maximum number of files to show (default: 10)')

    parser.add_argument(
        '-p', '--pattern',
        dest='pattern',
        default='*',
        help='a pattern to narrow down the search, e.g. "*.txt"\n'
             ' NOTE: The pattern might need to be escaped, possibly '
             'using quotes or backslashes, depending on your shell.')

    return parser.parse_args()


def collect_file_infos(search_path, pattern):
    """Yield information on each file along the path."""
    file_paths = collect_file_paths(search_path, pattern)
    return map(create_file_info, file_paths)


def collect_file_paths(search_path, pattern):
    """List all files along the path."""
    for directory, subdirectories, files in os.walk(search_path):
        for file_path in Path(directory).glob(pattern):
            yield file_path


def create_file_info(file_path):
    """Collect information on a file (i.e. its size)."""
    size = file_path.stat().st_size
    return FileInfo(file_path, size)


def collect_biggest_files(file_infos, limit):
    """Determine the biggest files."""
    return collect_highest(file_infos, attrgetter('size'), limit)


def collect_highest(iterable, sort_key, limit):
    """Return the highest elements from the iterable, considering the
    value returned by the sort key function ``sort_key``, but no more
    than ``limit``.
    """
    def update_with_item(items, item):
        return sorted(items + [item], key=sort_key, reverse=True)[:limit]

    return reduce(update_with_item, iterable, [])


def format_results(file_infos):
    """Format the file information objects."""
    if file_infos:
        highest_size_digits = len(str(file_infos[0].size))
        tmpl = ' {{0.size:>{}d}}  {{0.path}}'.format(highest_size_digits)
        for file_info in file_infos:
            yield tmpl.format(file_info)
    else:
        yield 'No files were found.'


def main():
    args = parse_args()

    file_infos = collect_file_infos(args.path, args.pattern)
    biggest_files = collect_biggest_files(file_infos, args.max_files)

    for line in format_results(biggest_files):
        print(line)


if __name__ == '__main__':
    main()
