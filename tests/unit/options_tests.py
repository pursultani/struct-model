#
# Copyright
#


import unittest

from structmodel.options import *


class OptionsTests(unittest.TestCase):

  def setUp(self):
    self.options = Options()

  def test_Options_assignment(self):
    self.options['foo'] = 'FOO'
    self.options.bar = 'BAR'
    self.assertEquals(self.options.foo, 'FOO')
    self.assertEquals(self.options['bar'], 'BAR')
    self.assertEquals(self.options, {'foo': 'FOO', 'bar': 'BAR'})

  def test_Options_del(self):
    self.options['foo'] = 'FOO'
    self.options.bar = 'BAR'
    del self.options.foo
    del self.options['bar']
    self.assertFalse(self.options.foo)
    self.assertFalse(self.options['bar'])
    self.assertFalse(self.options)


class GenericOptionsTests(unittest.TestCase):

  def setUp(self):
    self.options = Options()
    self.defaults = {}

  def test_defaults(self):
    for pair in self.defaults.items():
      self.assertEquals(self.options[pair[0]], pair[1])


class StructOptionsTests(GenericOptionsTests):

  def setUp(self):
    self.options = StructOptions('Foo')
    self.defaults = {
      'open': False,
      'lenient': False,
      'json_indent': 2,
      'json_item_sep': ', ',
      'json_dict_sep': ': '
    }

  def test_internals(self):
    self.assertEquals(self.options.name, 'Foo')
    self.assertEquals(self.options.cache, {})

  def test_filter_internals(self):
    self.assertEquals(
      StructOptions.filter_internals({'name': '', 'cache': {}}), {})


class AttributeOptionsTests(GenericOptionsTests):

  def setUp(self):
    self.options = AttributeOptions('Foo', 'bar')
    self.defaults = {
      'type': str,
      'required': False,
      'pattern': None,
      'strip': False,
      'cleanse': False,
      'normalize': False,
      'min_length': None,
      'max_length': None,
      'format': None
    }

  def test_internals(self):
    self.assertEquals(self.options.namespace, 'Foo')
    self.assertEquals(self.options.name, 'bar')
    self.assertEquals(self.options.cache, {})

  def test_filter_internals(self):
    self.assertEquals(
      AttributeOptions.filter_internals(
        {'namespace': '', 'name': '', 'cache': {}}), {})
