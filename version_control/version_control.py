import repex.repex as rpx
import os
import re
import sys
# from dsl_parser.parser import parse_from_path
# from dsl_parser.parser import DSLParsingException


class ValidateFiles():
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


class ValidateVersions():

    def validate(self, pattern, version, vtype):
        m = re.match(pattern, version)
        if not m:
            sys.exit('illegal version ({0}): {1}'.format(vtype, version))

    def validate_python_version(self, version):
        pattern = '\d\.\d(\.\d)?((rc|ga|b|c|a)\d+)?$'
        self.validate(pattern, version, 'python')

    def validate_version_file_version(self, version):
        pattern = '\d\.\d\.\d(-(m|rc|ga)\d+)?$'
        self.validate(pattern, version, 'VERSION')

    def validate_yaml_version(self, version):
        pattern = '\d\.\d(\.\d)?((m|rc|ga)\d+)?$'
        self.validate(pattern, version, 'yaml')


def do_validate_files(file_type, f):
    validate = ValidateFiles()
    if file_type == 'blueprint.yaml':
        validate.blueprintyaml(f)
    elif file_type == 'setup.py':
        validate.setuppy(f)
    elif file_type == 'VERSION':
        validate.ver(f)
    elif file_type == 'plugin.yaml':
        validate.pluginyaml(f)


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
    pattern = '\d\.\d(\.\d)?(-)?((ga|rc|m|b|c|a)\d+)?$'
    m = re.match(pattern, version)
    if not m:
        sys.exit('illegal version: {0}'.format(version))


def execute(plugins_version, core_version,
            configf, base_dir, prerelease=None,
            validate=True, verbose=False):
    config = rpx.import_config(os.path.expanduser(configf))
    paths = config.get('paths')
    if not paths:
        raise VCError('no paths configured in config yaml')
    variables = config.get('variables', {})

    # if it's a prerelease, restructure the version pattern
    if prerelease:
        version_version = '{0}-{1}'.format(
            core_version if core_version.count('.') == '2'
            else core_version + '.0', prerelease)
        python_plugins_version = '{0}{1}'.format(
            plugins_version, prerelease).replace('m', 'a')
        python_core_version = '{0}{1}'.format(
            core_version, prerelease).replace('m', 'a')
        yaml_plugins_version = '{0}{1}'.format(
            plugins_version, prerelease)
        yaml_core_version = '{0}{1}'.format(
            core_version, prerelease)
    else:
        version_version = core_version if core_version.count('.') == '2' \
            else core_version + '.0',
        python_plugins_version = plugins_version
        python_core_version = core_version
        yaml_plugins_version = plugins_version
        yaml_core_version = core_version

    # validate that the versions are matching the allowed pattern
    v = ValidateVersions()
    v.validate_version_file_version(version_version)
    v.validate_python_version(python_plugins_version)
    v.validate_python_version(python_core_version)
    v.validate_yaml_version(yaml_plugins_version)
    v.validate_yaml_version(yaml_core_version)

    versions = {}

    # create variables for the different types of files
    versions['version_version'] = version_version
    versions['python_plugins_version'] = python_plugins_version
    versions['python_core_version'] = python_core_version
    versions['yaml_plugins_version'] = yaml_plugins_version
    versions['yaml_core_version'] = yaml_core_version
    variables.update(versions)

    print 'version_version:' + variables['version_version']
    print 'python_plugins_version:' + variables['python_plugins_version']
    print 'python_core_version:' + variables['python_core_version']
    print 'yaml_plugins_version:' + variables['yaml_plugins_version']
    print 'yaml_core_version:' + variables['yaml_core_version']

    for p in paths:
        p['base_directory'] = base_dir
        if os.path.isfile(os.path.join(p['base_directory'], p['path'])):
            p['path'] = os.path.join(p['base_directory'], p['path'])
            rpx.handle_file(p, variables, verbose=verbose)
            if validate:
                do_validate_files(p['type'], p['path'])
        else:
            files = rpx.get_all_files(
                p['type'], p['path'], base_dir, p.get('excluded', []), verbose)
            for f in files:
                p['path'] = f
                rpx.handle_file(p, variables, verbose=verbose)
                if validate:
                    do_validate_files(p['type'], f)


class VCError(Exception):
    pass
