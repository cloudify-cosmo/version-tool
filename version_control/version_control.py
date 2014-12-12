import repex.repex as rpx
import os
import re
import sys
import logger
# from dsl_parser.parser import parse_from_path
# from dsl_parser.parser import DSLParsingException

lgr = logger.init()


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
        pattern = '\d\.\d(\.\d)?((rc|b|c|a)(\d+)?)?$'
        self.validate(pattern, version, 'python')

    def validate_version_file_version(self, version):
        pattern = '\d\.\d\.\d(-(m|rc)(\d+)?)?$'
        self.validate(pattern, version, 'VERSION')

    def validate_yaml_version(self, version):
        pattern = '\d\.\d(\.\d)?((m|rc)(\d+)?)?$'
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
            else core_version + '.0'
        python_plugins_version = plugins_version
        python_core_version = core_version
        yaml_plugins_version = plugins_version
        yaml_core_version = core_version

    lgr.info('version_version:' + version_version)
    lgr.info('python_plugins_version:' + python_plugins_version)
    lgr.info('python_core_version:' + python_core_version)
    lgr.info('yaml_plugins_version:' + yaml_plugins_version)
    lgr.info('yaml_core_version:' + yaml_core_version)

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

    # the reason for using the handle_file method instead of handle_path is
    # that we want to be able to run the do_validate function on every file
    # after it is processed.
    for p in paths:
        variables = variables if variables else {}
        if type(variables) is not dict:
            raise RuntimeError('variables must be of type dict')
        var_expander = rpx.VarHandler(p)
        p = var_expander.expand(variables)

        p['base_directory'] = base_dir
        if os.path.isfile(os.path.join(p['base_directory'], p['path'])):
            p['path'] = os.path.join(p['base_directory'], p['path'])
            rpx.handle_file(p, variables, verbose=verbose)
            if validate:
                do_validate_files(p['type'], p['path'])
        # elif os.path.isdir(os.path.join(p['base_directory'], p['path'])):
        elif any(re.search(
                p['path'], obj) for obj in os.listdir(p['base_directory'])):
            files = rpx.get_all_files(
                p['type'], p['path'], base_dir, p.get('excluded', []), verbose)
            for f in files:
                p['path'] = f
                rpx.handle_file(p, variables, verbose=verbose)
                if validate:
                    do_validate_files(p['type'], f)
        else:
            lgr.error('path does not exist: {0}'.format(p['path']))


class VCError(Exception):
    pass
