from repex.repex import import_config
from repex.repex import RepexError
from repex.repex import handle_file
from repex.repex import get_all_files
import os
import re
import sys
# from dsl_parser.parser import parse_from_path
# from dsl_parser.parser import DSLParsingException


class Validate():
    def blueprintyaml(self, blueprint_path):
        # try:
        #     parse_from_path(blueprint_path)
        # except DSLParsingException as ex:
        #     raise Exception('validation failed: {0}'.format(str(ex)))
        pass

    def setuppy(self, setuppy_path):
        # maybe use the file to install the module
        pass

    def devreqs(self, devreqs_path):
        # run pip install -r dev-requirements.txt
        pass

    def ver(self, version_path):
        # check that at least version and build are not None
        pass

    def pluginyaml(self, pluginyaml_path):
        # check... something
        pass


def do_validate(p):
    validate = Validate()
    if p['type'] == 'blueprint.yaml':
        validate.blueprintyaml(p['path'])
    elif p['type'] == 'setup.py':
        validate.setuppy(p['path'])
    elif p['type'] == 'VERSION':
        validate.ver(p['path'])
    elif p['type'] == 'plugin.yaml':
        validate.pluginyaml(p['path'])


def _validate_version(version):
    """
    Validates Cloudify and plugins versions.
    Supported formats:
    3.0-m1
    3.0.1-m1
    3.1-rc1
    3.1
    3.1-b1
    3.0.1
    """
    pattern = '\d\.\d(\.\d)?(-)?((rc|m|b|c|a)\d+)?$'
    m = re.match(pattern, version)
    if not m:
        sys.exit('illegal version: {0}'.format(version))


def execute(plugins_version, core_version,
            configf, base_dir, prerelease=None,
            validate=True, verbose=False):
    config = import_config(os.path.expanduser(configf))
    variables = config.get('variables', {})

    # if it's a prerelease, restructure the version pattern
    if prerelease:
        version_version = '{0}-{1}'.format(
            core_version, prerelease)
        python_plugins_version = '{0}{1}'.format(
            plugins_version, prerelease).replace('m', 'a').replace('rc', 'c')
        python_core_version = '{0}{1}'.format(
            core_version, prerelease).replace('m', 'a').replace('rc', 'c')
        yaml_version = '{0}{1}'.format(
            plugins_version, prerelease)
    else:
        version_version = core_version
        python_plugins_version = plugins_version
        python_core_version = core_version
        yaml_version = plugins_version

    # validate that the versions are matching the allowed pattern
    _validate_version(version_version)
    _validate_version(python_plugins_version)
    _validate_version(python_core_version)
    _validate_version(yaml_version)

    versions = {}

    # create variables for the different types of files
    versions['version_version'] = version_version
    versions['python_plugins_version'] = python_plugins_version
    versions['python_core_version'] = python_core_version
    versions['yaml_version'] = yaml_version
    variables.update(versions)

    print 'version_version:' + variables['version_version']
    print 'python_plugins_version:' + variables['python_plugins_version']
    print 'python_core_version:' + variables['python_core_version']
    print 'yaml_version:' + variables['yaml_version']

    paths = config.get('paths')
    if not paths:
        raise RepexError('no paths configured in config yaml')
    for p in paths:
        if os.path.isfile(p['path']):
            handle_file(p, variables, verbose=verbose)
            if validate:
                do_validate(p)
        else:
            files = get_all_files(p['type'], p['path'], base_dir)
            for f in files:
                # apply a version changes according to the type of
                # repo we're dealing with.
                if re.search('cloudify.*plugin', f):
                    versions['python_version'] = python_plugins_version
                elif re.search('cloudify-.*', f):
                    versions['python_version'] = python_core_version
                variables.update(versions)
                p['path'] = f
                handle_file(p, variables, verbose=verbose)
                if validate:
                    do_validate(p)
