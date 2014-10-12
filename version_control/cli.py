# flake8: NOQA

"""Script to run cloudify-version-control via command line

Usage:
    version-control (--plugins-version=<string> --core-version=<string>) [--prerelease=<string>]
                    (--base-dir=<path> --config=<path>) [--validate -v]
    version-control --version

Options:
    -h --help                       Show this screen.
    -p --plugins-version=<string>   Plugins version to update to
    -c --core-version=<string>      Plugins version to update to
    -r --prerelease=<string>        Release (i.e rc1, m3, )
    -b --base-dir=<path>            Base directory to look in
    -f --config=<path>              Config file path
    --validate                      Validate after replacement (defaults to true)
    -v --verbose                    verbose mode
    --version                       Display current version of version-control and exit
"""

from __future__ import absolute_import
from docopt import docopt
from version_control.version_control import execute


def ver_check():
    import pkg_resources
    version = None
    try:
        version = pkg_resources.get_distribution('version-control').version
    except Exception as e:
        print(e)
    finally:
        del pkg_resources
    return version


def version_run(o):
    execute(o['--plugins-version'],
            o['--core-version'],
            o['--config'],
            o['--base-dir'],
            o['--prerelease'],
            o['--validate'],
            o['--verbose'])


def vercont(test_options=None):
    """Main entry point for script."""
    version = ver_check()
    options = test_options or docopt(__doc__, version=version)
    print options
    version_run(options)


def main():
    vercont()


if __name__ == '__main__':
    main()
