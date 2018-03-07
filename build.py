'''
StructModel build script.
'''

#
# Imports
#

from pybuilder.core import init, use_plugin, Author


#
# Plugins
#

use_plugin('python.core')
use_plugin('python.install_dependencies')
use_plugin('python.unittest')
use_plugin('python.integrationtest')
use_plugin('python.pylint')
use_plugin('python.coverage')
use_plugin('python.distutils')


#
# Attributes
#

shortname = 'struct-model'
name = 'StructModel: Structured Data Model'
version = '1.0.1'
url = 'https://github.com/pursultani/struct-model'
summary = '''An open data structure, similar to Ruby OpenStruct, with optional type checking,
validation, and JSON mapping.'''
authors = [
  Author('Hossein Pursultani', 'hossein@freshbits.io')
]
description = open('README.adoc').read()
license = open('LICENSE').read().replace('\n', ' ')


#
# Tasks
#

default_task = ( 'install_dependencies', 'analyze', 'publish' )


#
# Initialization
#
@init
def initialize(project):


    #
    # Properties
    #

    project.set_property('name', shortname)
    project.set_property('version', version)
    project.set_property('dir_source_main_python', 'src')
    project.set_property('dir_source_main_scripts', 'bin')
    project.set_property('dir_target', 'build')
    project.set_property('dir_dist', '$dir_target/dist/%s-$version' % shortname)
    project.set_property('dir_dist_scripts', 'bin')
    project.set_property('dir_source_unittest_python', 'tests/unit')
    project.set_property('dir_source_integrationtest_python', 'tests/integration')
    project.set_property('distutils_classifiers', [])
    project.set_property('distutils_commands', [])


    #
    # Dependencies
    #

    project.build_depends_on('mockito')
    project.depends_on_requirements('requirements.txt')

