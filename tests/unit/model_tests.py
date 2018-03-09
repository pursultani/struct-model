#
# Copyright
#


import unittest
import datetime

from structmodel.model import *
from structmodel.options import *
from structmodel.types import *


class InvalidStruct:

  pass


class ValidStruct(Struct):

  pass


class ModelRegistryTests(unittest.TestCase):

  def tearDown(self):
    try:
      del ValidStruct.__internal_name__
      del Model.registry['MyStruct']
      del Model.registry['ValidStruct']
    except Exception, e:
      pass

  def test_invalid_declare(self):
    try:
      Model.declare()(InvalidStruct)
      self.assertFalse(True)
    except InvalidStructType, e:
      self.assertEquals(e.parameters, {'struct_type': InvalidStruct})

  def test_simple_declare(self):
    Model.declare()(ValidStruct)
    overlay = Model.overlay('ValidStruct')
    self.assertEquals(overlay.name, 'ValidStruct')
    self.assertEquals(overlay.opts.name, 'ValidStruct')
    self.assertEquals(StructOptions.filter_internals(overlay.opts), {})
    self.assertEquals(overlay.attrs, {})

  def test_comprehensive_declare(self):
    Model.declare('MyStruct',
      open = True,
      lenient = True)(ValidStruct)
    overlay = Model.overlay('MyStruct')
    self.assertEquals(overlay.name, 'MyStruct')
    self.assertEquals(overlay.opts.name, 'MyStruct')
    self.assertEquals(StructOptions.filter_internals(overlay.opts),
      {'open': True, 'lenient': True})
    self.assertEquals(overlay.attrs, {})

  def test_invalid_define_1(self):
    try:
      Model.define('foo')(InvalidStruct)
      self.assertFalse(True)
    except InvalidStructType, e:
      self.assertEquals(e.parameters, {'struct_type': InvalidStruct})

  def test_invalid_define_2(self):
    try:
      Model.define('foo')(ValidStruct)
      self.assertFalse(True)
    except UndeclaredStructError, e:
      self.assertEquals(e.parameters, {'struct_type': ValidStruct})

  def test_invalid_define_3(self):
    try:
      ValidStruct.__internal_name__ = 'MyStruct'
      Model.define('foo')(ValidStruct)
      self.assertFalse(True)
    except UnknownStructError, e:
      self.assertEquals(e.parameters, {'name': 'MyStruct'})

  def test_invalid_overlay(self):
    try:
      Model.overlay('UnknowStruct')
      self.assertFalse(True)
    except UnknownStructError, e:
      self.assertEquals(e.parameters, {'name': 'UnknowStruct'})

  def test_simple_define(self):
    Model.declare('MyStruct')(ValidStruct)
    Model.define('foo')(ValidStruct)
    overlay = Model.overlay('MyStruct')
    attr_opts = overlay.attrs['foo']
    self.assertEquals(attr_opts.namespace, 'MyStruct')
    self.assertEquals(attr_opts.name, 'foo')
    self.assertEquals(attr_opts.type, str)
    self.assertEquals(AttributeOptions.filter_internals(attr_opts), {})

  def test_comprehensive_define(self):
    Model.declare('MyStruct')(ValidStruct)
    Model.define('foo', type = list, required = True,
      item_type = str, item_pattern = r'^[ab]$')(ValidStruct)
    overlay = Model.overlay('MyStruct')
    attr_opts = overlay.attrs['foo']
    self.assertEquals(attr_opts.namespace, 'MyStruct')
    self.assertEquals(attr_opts.name, 'foo')
    self.assertEquals(attr_opts.type, list)
    self.assertEquals(attr_opts.item_type, str)
    self.assertEquals(attr_opts.item_pattern, r'^[ab]$')

  def test_invalid_validator_function(self):
    Model.declare('MyStruct')(ValidStruct)
    Model.define('foo')(ValidStruct)
    try:
      Model.validate(None)(ValidStruct)
      self.assertFalse(True)
    except UnexpectedError, e:
      pass

  def test_simple_validator_function(self):
    Model.declare('MyStruct')(ValidStruct)
    overlay = Model.overlay('MyStruct')
    Model.validate(lambda o: o)(ValidStruct)
    self.assertTrue(overlay.validators)
    self.assertEquals(len(overlay.validators), 1)

  def test_comprehensive_validator_function(self):
    Model.declare('MyStruct')(ValidStruct)
    Model.validate(lambda o: o, message = 'Oops!')(ValidStruct)
    overlay = Model.overlay('MyStruct')
    self.assertTrue(overlay.validators)
    self.assertEquals(len(overlay.validators), 1)
    self.assertTrue(hasattr(overlay.validators[0][0], '__call__'))
    self.assertEquals(overlay.validators[0][1]['message'], 'Oops!')


class StructOverlayTests(unittest.TestCase):

  def setUp(self):
    Model.declare('MyStruct')(ValidStruct)

  def tearDown(self):
    del ValidStruct.__internal_name__
    del Model.registry['MyStruct']


  def test_options_lifecycle(self):
    overlay = Model.overlay('MyStruct')
    overlay.set_options(name = 'AnotherStruct', opt1 = 1, opt2 = 'Two')
    self.assertEquals(overlay.name, 'MyStruct')
    self.assertEquals(overlay.opts.opt1, 1)
    self.assertEquals(overlay.opts.opt2, 'Two')
    overlay.unset_options('name', 'opt1', 'opt2')
    self.assertEquals(overlay.name, 'MyStruct')
    self.assertFalse(overlay.opts.opt1)
    self.assertFalse(overlay.opts.opt2)

  def test_attribute_lifecycle(self):
      overlay = Model.overlay('MyStruct')
      overlay.add_attribute('foo', attr1 = 1, attr2= 'Two')
      self.assertEquals(overlay.attrs['foo'].namespace, 'MyStruct')
      self.assertEquals(overlay.attrs['foo'].name, 'foo')
      self.assertEquals(overlay.attrs['foo'].attr1, 1)
      self.assertEquals(overlay.attrs['foo'].attr2, 'Two')
      overlay.set_attribute_options('foo',
        namespace = 'AnotherStruct', name = 'bar', attr1 = 'One', attr2 = 2)
      self.assertEquals(overlay.attrs['foo'].namespace, 'MyStruct')
      self.assertEquals(overlay.attrs['foo'].name, 'foo')
      self.assertEquals(overlay.attrs['foo'].attr1, 'One')
      self.assertEquals(overlay.attrs['foo'].attr2, 2)
      overlay.unset_attribute_options('foo', 'namespace', 'name', 'attr1', 'attr2')
      self.assertEquals(overlay.attrs['foo'].namespace, 'MyStruct')
      self.assertEquals(overlay.attrs['foo'].name, 'foo')
      self.assertFalse(overlay.attrs['foo'].attr1)
      self.assertFalse(overlay.attrs['foo'].attr2)
      overlay.del_attribute('foo')
      self.assertFalse('foo' in overlay.attrs)

  def test_hidden_attributes(self):
      overlay = Model.overlay('MyStruct')
      self.assertEquals(overlay.process_set_value('_foo', 'Foo'), 'Foo')
      overlay.add_attribute('_foo', required = True)
      overlay.process_del_value('_foo')

  def test_additional_attribute(self):
    overlay = Model.overlay('MyStruct')
    try:
      overlay.process_set_value('foo', 'Foo')
      self.assertFalse(True)
    except UndefinedAttributeError, e:
      pass
    overlay.set_options(open = True)
    self.assertEquals(overlay.process_set_value('_foo', 'Foo'), 'Foo')

  def test_del_required_attribute(self):
    overlay = Model.overlay('MyStruct')
    overlay.add_attribute('foo', required = True)
    try:
      overlay.process_del_value('foo')
      self.assertFalse(True)
    except MissingRequireAttributeError, e:
      pass
    overlay.set_options(lenient = True)
    overlay.process_del_value('foo')

  def test_invalid_struct_assetion(self):
    overlay = Model.overlay('MyStruct')
    try:
      overlay.process_validate({})
      self.assertFalse(True)
    except InvalidStructType, e:
      pass

  def test_hidden_attribute_assertion(self):
    overlay = Model.overlay('MyStruct')
    overlay.add_attribute('foo')
    overlay.add_attribute('_bar', required = True)
    struct = ValidStruct()
    overlay.process_validate(struct)

  def test_default_attribute_values(self):
    overlay = Model.overlay('MyStruct')
    overlay.add_attribute('foo')
    overlay.add_attribute('bar', default = 'Bar')
    overlay.add_attribute('baz', default = 'Baz')
    overlay.add_attribute('foobar',
      default = lambda s, t: s + t, default_args = ('Foo', 'Bar'))
    struct = ValidStruct()
    overlay.process_validate(struct)
    self.assertEquals(struct.bar, 'Bar')
    self.assertEquals(struct.baz, 'Baz')
    self.assertEquals(struct.foobar, 'FooBar')
    self.assertFalse('foo' in struct)

  def test_required_attribute_assertion(self):
    overlay = Model.overlay('MyStruct')
    overlay.add_attribute('foo', required = True)
    struct = ValidStruct()
    try:
      overlay.process_validate(struct)
      self.assertFalse(True)
    except MissingRequireAttributeError, e:
      pass

  def test_nested_attribute_assertion(self):
    overlay = Model.overlay('MyStruct')
    overlay.add_attribute('foo', required = True)
    overlay.add_attribute('nested', type = ValidStruct)
    struct = ValidStruct()
    struct.foo = 'Foo'
    struct.nested = ValidStruct()
    struct.nested.foo = 'Bar'
    overlay.process_validate(struct)
    try:
      del struct.nested.foo
      overlay.process_validate(struct)
      self.assertFalse(True)
    except MissingRequireAttributeError, e:
      pass

  def test_list_attribute_assertion(self):
    overlay = Model.overlay('MyStruct')
    overlay.add_attribute('foo', type = list, item_required = True)
    struct = ValidStruct()
    overlay.process_validate(struct)
    overlay.set_attribute_options('foo', min_length = 1)
    try:
      overlay.process_validate(struct)
      self.assertFalse(True)
    except MissingRequiredValueError, e:
      pass

  def test_nested_list_attribute_assertion(self):
    overlay = Model.overlay('MyStruct')
    overlay.add_attribute('foo', required = True)
    overlay.add_attribute('bar', type = list, item_type = ValidStruct)
    struct = ValidStruct()
    struct.foo = 'Foo'
    struct.bar = [ValidStruct(foo = 'Foo#1')]
    overlay.process_validate(struct)
    try:
      struct.bar += [ValidStruct()]
      overlay.process_validate(struct)
      self.assertFalse(True)
    except MissingRequireAttributeError, e:
      pass

  def test_validators_assertion(self):
    overlay = Model.overlay('MyStruct')
    overlay.add_validator(lambda o: True)
    struct = ValidStruct()
    overlay.process_validate(struct)
    try:
      overlay.add_validator(lambda o: False, message = 'Ouch!')
      overlay.process_validate(struct)
      self.assertFalse(True)
    except StructValidationError, e:
      self.assertEquals(e.parameters, {'name': 'MyStruct', 'explanation': 'Ouch!'})

  def test_empty_json(self):
    overlay = Model.overlay('MyStruct')
    struct = ValidStruct()
    self.assertEquals(overlay.to_json(struct), '{}')

  def test_hidden_attribute_json(self):
    overlay = Model.overlay('MyStruct')
    overlay.set_options(open = True, json_indent = None)
    struct = ValidStruct()
    struct._foo = 'Foo'
    struct.bar = 'Bar'
    self.assertEquals(overlay.to_json(struct), '{"bar": "Bar"}')

  def test_comprehensive_model_with_json(self):
    overlay = Model.overlay('MyStruct')
    overlay.set_options(open = True, json_indent = 1, json_item_sep = ',', json_dict_sep = ':')
    overlay.add_attribute('strValue', type = str)
    overlay.add_attribute('intValue', type = int)
    overlay.add_attribute('floatValue', type = float)
    overlay.add_attribute('listValue', type = list)
    overlay.add_attribute('dateValue', type = datetime.date)
    overlay.add_attribute('timeValue', type = datetime.time)
    overlay.add_attribute('datetimeValue', type = datetime.datetime)
    overlay.add_attribute('nestedValue', type = ValidStruct)
    overlay.add_attribute('nestedListValue', type = list, item_type = ValidStruct)
    struct = ValidStruct()
    struct.strValue = 'X'
    struct.intValue = 1
    struct.floatValue = 1.0
    struct.listValue = ['A', 'B']
    struct.dateValue = datetime.date(2000, 1, 1)
    struct.timeValue = datetime.time(10, 15, 20)
    struct.datetimeValue = datetime.datetime(2015, 12, 1, 10, 15, 20)
    struct.nestedValue = {'foo': 'Foo'}
    struct.nestedListValue = [{'bar': 'Bar'}, {'baz': 'Baz'}]
    self.assertEquals(overlay.to_json(struct),
'''{
 "floatValue":1.0,
 "nestedValue":{
  "foo":"Foo"
 },
 "timeValue":"10:15:20",
 "intValue":1,
 "datetimeValue":"2015-12-01T10:15:20",
 "strValue":"X",
 "dateValue":"2000-01-01",
 "listValue":[
  "A",
  "B"
 ],
 "nestedListValue":[
  {
   "bar":"Bar"
  },
  {
   "baz":"Baz"
  }
 ]
}''')
