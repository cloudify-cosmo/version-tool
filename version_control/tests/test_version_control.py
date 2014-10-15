########
# Copyright (c) 2014 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#    * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the License.

__author__ = 'anna'

import testtools
import os
import shutil
import version_control.version_control as vc
import filecmp

TEST_DIR = 'version_control/tests'
TEST_RESOURCES_DIR = os.path.join(TEST_DIR, 'resources')
DEF_CONFIG_YAML = os.path.join(TEST_RESOURCES_DIR, 'config.yaml')
EMPTY_CONFIG = os.path.join(TEST_RESOURCES_DIR, 'no_paths_config.yaml')
SINGLE_FILE_CONFIG = os.path.join(
    TEST_RESOURCES_DIR, 'single_file_config.yaml')


class TestBase(testtools.TestCase):

    def test_version(self):

        test_dirs = os.listdir(TEST_RESOURCES_DIR)

        for test_file in test_dirs:
            if os.path.isdir(os.path.join(TEST_RESOURCES_DIR, test_file)) \
                    and test_file.startswith('cloudify-'):
                print test_file

                input_dir = TEST_RESOURCES_DIR + test_file + '/input'
                working_dir = TEST_RESOURCES_DIR + test_file + '/work-copy'
                expected_output = \
                    TEST_RESOURCES_DIR + test_file + '/expected-output'

                if not os.path.exists(input_dir):
                    continue

                shutil.rmtree(working_dir, ignore_errors=True)

                # Copy the input because the files will be changed in place
                shutil.copytree(input_dir, working_dir)
                vc.execute("1.1", "3.1", DEF_CONFIG_YAML,
                           working_dir, 'm6', verbose=True)
                res = filecmp.dircmp(working_dir, expected_output)

                try:
                    self.assertEquals(0, len(res.diff_files))

                    for sd in res.subdirs.itervalues():
                        print sd.diff_files
                        self.assertEquals(0, len(sd.diff_files))
                except AssertionError:
                    filecmp.dircmp(working_dir, expected_output)\
                        .report_full_closure()
                    raise

    def test_illegal_versions(self):
        ex = self.assertRaises(
            SystemExit, vc.execute, '1.1', '3.11',
            DEF_CONFIG_YAML, '', 'm6', verbose=True)
        self.assertIn('illegal version', str(ex))
        ex = self.assertRaises(
            SystemExit, vc.execute, '1', '3.1',
            DEF_CONFIG_YAML, '', 'm6', verbose=True)
        self.assertIn('illegal version', str(ex))
        ex = self.assertRaises(
            SystemExit, vc.execute, '1.1', '3.1',
            DEF_CONFIG_YAML, '', 'd6', verbose=True)
        self.assertIn('illegal version', str(ex))
        ex = self.assertRaises(
            SystemExit, vc.execute, '1.1', '3.1',
            DEF_CONFIG_YAML, '', '6', verbose=True)
        self.assertIn('illegal version', str(ex))
        ex = self.assertRaises(
            SystemExit, vc.execute, '1.1', '3.1.1.1',
            DEF_CONFIG_YAML, '', 'm6', verbose=True)
        self.assertIn('illegal version', str(ex))

    def test_single_file(self):
        working_dir = os.path.join(TEST_RESOURCES_DIR, 'single-file')
        vc.execute("1.1", "3.1", SINGLE_FILE_CONFIG,
                   'version_control/tests/resources', 'm6', verbose=True)
        with open(os.path.join(working_dir + '/check_changed/VERSION')) as f:
            self.assertIn('3.1.0-m6', f.read())
            self.assertNotIn('3.1.0-m5', f.read())
        with open(os.path.join(working_dir + '/check_unchanged/VERSION')) as f:
            self.assertIn('3.1.0-m5', f.read())
            self.assertNotIn('3.1.0-m6', f.read())

    def test_no_paths_key_in_config(self):
        ex = self.assertRaises(
            Exception, vc.execute, "1.1", "3.1", EMPTY_CONFIG, '')
        self.assertIn('no paths configured in config yaml', str(ex))
