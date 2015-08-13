#!/usr/bin/env python2
import argparse
import os
import re


"""
We use semantic versioning

X.X.X.X product version is
| | | |
| | | ^----------- build number
| | ^------------- bug fix
| ^--------------- features that not breaks API (minor)
^----------------- features that breaks API (major)

vX.X.X tag is
 | | |
 | | ^------------ bug fix
 | ^-------------- features that not breaks API (minor)
 ^---------------- features that breaks API (major)

We develop standalone application, so our API is:
 - command line interface of application;
 - communication protocol;
 - expected behavior.

So if feature breaks backward compatibility then new major version should be
released.
"""

TAG_VERSION = "v1.0.0"

BASEDIR = os.path.dirname(__file__)

FILES = [
    (os.path.join(BASEDIR, "agent", "comnsense_agent", "version.py"),
     re.compile(r'__version__\s*=\s*"(.+?)"', re.S | re.U)),
    (os.path.join(BASEDIR, "comnsense", "comnsense", "Properties", "AssemblyInfo.cs"),
     re.compile(r'AssemblyVersion\("(.+?)"\)', re.S | re.U)),
    (os.path.join(BASEDIR, "comnsense", "comnsense", "Properties", "AssemblyInfo.cs"),
     re.compile(r'AssemblyFileVersion\("(.+?)"\)', re.S | re.U)),
]

SELF_PATTERN = re.compile(r'TAG_VERSION\s*=\s*"(.+?)"', re.S | re.U)


def parse_args(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dry-run", action="store_true",
                        help="do not change files, just print version")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-t", "--tag", type=str, help="new tag version")
    group.add_argument("-b", "--build", type=int, help="build number id")
    return parser.parse_args(args)


def update_file(filename, pattern, version):
    print "updating ", filename
    with open(filename) as h:
        content = h.read()
    match = pattern.search(content)
    if not match:
        raise RuntimeError(
            "could not find version %s in %s" % (match.re, filename))
    start, end = match.span(1)
    content = content[:start] + version + content[end:]
    with open(filename, 'w') as h:
        h.write(content)


def get_version(tag, build):
    if tag is None:
        tag = TAG_VERSION
    if build is None:
        build = 0
    return "%s.%d" % (tag.lstrip("v"), build)


def main(args):
    version = get_version(args.tag, args.build)
    print version
    if args.dry_run:
        return
    for filename, pattern in FILES:
        update_file(filename, pattern, version)
    if args.tag:
        update_file(__file__, SELF_PATTERN, args.tag.lstrip("v"))


if __name__ == '__main__':
    main(parse_args())
