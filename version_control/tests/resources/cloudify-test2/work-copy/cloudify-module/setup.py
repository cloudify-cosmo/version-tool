#########
# Copyright (c) 2013 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#  * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  * See the License for the specific language governing permissions and
#  * limitations under the License.

from setuptools import setup


setup(
    name='cloudify-agent-installer-plugin',
    version='3.1a6',
    author='elip',
    author_email='elip@gigaspaces.com',
    packages=['worker_installer'],
    license='LICENSE',
    description='Plugin for installing a Cloudify agent on a machine',
    install_requires=[
        'cloudify-plugins-common==3.1a6',
        'cloudify-script-plugin==1.1a6',
        'cloudify-openstack-provider==1.1a6',
        'cloudify-dsl-parser>=3.1a6',
        'fabric==1.8.3',
        'jinja2==2.11.3'
    ],
    tests_require=[
        "nose",
        "python-vagrant"
    ]
)
