import os
import argparse
import json
import datetime

import sys

VERSION = 1.0


def error(*args, **kwargs):
    print("Error:", *args, file=sys.stderr, **kwargs)
    sys.exit(1)


def snap(args):

    if not os.path.exists(args.path):
        error('"{}" does not exists'.format(args.path))

    if not os.path.isdir(args.path):
        error('"{}" is not a directory'.format(args.path))

    abs_path = os.path.abspath(args.path)
    today = datetime.datetime.now()

    if args.filename:
        filename = args.filename
    else:
        filename = today.strftime("%Y%m%dT%H%M%S") + ".json"

    dir_dic = {
        "path": abs_path,
        "datetime": today.isoformat(),
        "scheme-version": 1,
        "entries": {}
    }

    entry_path = abs_path

    try:
        for root, dirs, files in os.walk(abs_path):
            for name in files:
                entry_path = os.path.join(root, name)
                dir_dic["entries"][entry_path] = {'mtime': os.stat(entry_path).st_mtime, 'type': 'file'}

            for name in dirs:
                entry_path = os.path.join(root, name)
                dir_dic["entries"][entry_path] = {'mtime': os.stat(entry_path).st_mtime, 'type': 'directory'}

    except PermissionError:
        print('"{}" - permission denied'.format(entry_path))
    except FileNotFoundError:
        print('"{}" - not found (broken link?)'.format(entry_path))

    with open(filename, 'w') as outfile:
        json.dump(dir_dic, outfile, indent=4)

    print("Snapshot was saved to \"{}\"".format(filename))


def diff(args):
    if not os.path.exists(args.snap1):
        error('"{}" does not exist'.format(args.snap1))

    if not os.path.exists(args.snap2):
        error('"{}" does not exist'.format(args.snap2))

    try:
        with open(args.snap1, "r") as snap1_file:
            snap1_json = json.load(snap1_file)
    except ValueError:
        error("\"{}\" is not a valid json".format(args.snap1))
    except:
        error("Failed to read snapshot file \"{}\"", args.snap1)

    try:
        with open(args.snap2, "r") as snap2_file:
            snap2_json = json.load(snap2_file)
    except ValueError:
        error("\"{}\" is not a valid json".format(args.snap2))
    except:
        error("Failed to read snapshot file \"{}\"", args.snap2)

    if snap1_json['path'] != snap2_json['path']:
        error("Files paths do not match: \"{}\" and \"{}\"".format(snap1_json['path'], snap2_json['path']))

    if snap1_json['scheme-version'] != snap2_json['scheme-version']:
        error("Scheme versions do not match: \"{}\" and \"{}\"".format(snap1_json['scheme-version'],
                                                                       snap2_json['scheme-version']))

    results = []
    for entry in snap1_json['entries']:
        if entry not in snap2_json['entries']:
            results.append('Element {} was removed'.format(entry))

        elif snap1_json['entries'][entry] != snap2_json['entries'][entry]:
            results.append('Element {} was changed'.format(entry))

    for entry in snap2_json['entries']:
        if entry not in snap1_json['entries']:
            results.append('Element {} was added'.format(entry))

    results.sort()

    if not results:
        print("No changes")
    else:
        for line in results:
            print(line)


def main():
    parser = argparse.ArgumentParser(description='When called with snap argument, saves the state of the file system '
                                                 'PATH as a json SNAP file which contains a list of named entries '
                                                 'with a metadata for each file entry')
    parser.add_argument('-v', '--version', action='version', version=str(VERSION))
    subparsers = parser.add_subparsers(dest='action')
    subparsers.required = True

    parser_snap = subparsers.add_parser('snap', help='saves the state of the file system PATH as a json SNAP file')
    parser_snap.add_argument('path', help='positional argument for snap. Path to directory which should be analyzed')
    parser_snap.add_argument('-f', '--filename', help="optional snapshot file name")
    parser_snap.set_defaults(func=snap)

    parser_diff = subparsers.add_parser('diff', help='compares two SNAP files and reports the changes')
    parser_diff.add_argument('snap1', help='positional argument for diff. Path to the first snapshot '
                                           'which was created using the snap command')
    parser_diff.add_argument('snap2', help='positional argument for diff. Path to the second snapshot '
                                           'which was created using the snap command')
    parser_diff.set_defaults(func=diff)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
