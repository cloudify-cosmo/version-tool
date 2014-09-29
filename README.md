Cloudify Version Control - Internal

NOTE: To work with this tool, you'll have to manually install https://github.com/cloudify-cosmo/repex into your virtualenv.
Please read the `repex` documentation before working with this tool.

### Overview

This is an internal tool for Cloudify to update versions in different files.

Currently, it will be used to update the following:

- setup.py files
    - versions of the modules
    - versions of core dependencies
    - versions of plugin dependencies
- dev-requirements files
- blueprint.yaml files
- plugin.yaml files
- VERSION files
- Documentation

### Usage

```shell
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
```

Example:

```
version-control -p 1.1 -c 3.1 -r m1 -b ~/repos -f config.yaml
```

### Logic

We have several version formats we need to update in different files. For instance, these 3 examples represent the same version in different formats:
- VERSION: 3.1.0-m2
- setup.py: 3.1a2
- blueprint.yaml: 3.1m2

Since we currently provide 2 different versions for each release - one for the core and one for plugins, it is required that these 2 are supplied separately.
This will probably changed in the near future.

Consequently, the tool receives a plugin version, a core version and a prerelease (if applicable) and performs the necessary crunching to supply the correct version format to the corresponding file type.

After the crunching is complete, the tool will test that the resulting formats are allowed.

If the tests pass, the formats will be appended to the `variables` dict used by `repex`.

Then, the tool will run and replace whatever is needed.

If validation is requested, specific validations will run for each type of file. So, for instance, when a blueprint.yaml file is handled, the dsl parser will run and verify that the blueprint is valid.

NOTE: since we DO want to validate, it's required for the `type` key to be passed in the config.yaml even if we're only using a single file - in contrast to what's stated in `repex` regarding single files not requiring the `type` key.

### Using the tool from python rather than from the cli

To use the tool from a python script and possibly use environment variables from QuickBuild:

```python
from version_control.version_control import execute
import os

PLUGINS_VERSION = os.environ['PLUGINS_VERSION']
CORE_VERSION = os.environ['CORE_VERSION']
PRERELEASE = None if not os.environ['PRERELEASE_VERSION'] else os.environ['PRERELEASE_VERSION']

execute(plugins_version=PLUGINS_VERSION, core_version=CORE_VERSION,
        configf, base_dir, prerelease=PRERELEASE,
        validate=True, verbose=False)
```