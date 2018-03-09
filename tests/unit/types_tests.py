#
# Copyright
#


import unittest
import datetime

from structmodel.model import *
from structmodel.options import *
from structmodel.types import *


class InvalidTypeSubclass_1:

  pass


class InvalidTypeSubclass_2(DataType):

  pass


class InvalidTypeSubclass_3(DataType):

  __type__ = complex



class ValidTypeSubclass(DataType):

  __type__ = complex
  __builders__ = [
    lambda opts: ValidTypeSubclass.value_of,
    lambda opts: ValidTypeSubclass.filter_1 \
      if opts.filter_1 else None,
    lambda opts: ValidTypeSubclass.filter_2 \
      if opts.filter_2 else None,
    lambda opts: ValidTypeSubclass.filter_3 \
      if opts.filter_3 else None
  ]

  @classmethod
  def value_of(cls, x, opts):
    return x

  @classmethod
  def filter_1(cls, x, opts):
    return x + opts.delimiter + '1' + opts.delimiter

  @classmethod
  def filter_2(cls, x, opts):
    return x + opts.delimiter + '2' + opts.delimiter

  @classmethod
  def filter_3(cls, x, opts):
    return x + opts.delimiter + '3' + opts.delimiter


class InvalidStruct:

  pass


@Model.declare('tests.types.ValidStruct', open = True)
class ValidStruct(Struct):

  pass


@Model.declare('tests.types.AnotherValidStruct', open = True)
class AnotherValidStruct(Struct):

  pass


class TypeRegistryTests(unittest.TestCase):

  def test_initial_registry(self):
    self.assertEquals(DataType.registry, {
      object: ObjectType.__builders__,
      str: StringType.__builders__,
      bool: BooleanType.__builders__,
      int: IntegerType.__builders__,
      long: LongType.__builders__,
      float: FloatType.__builders__,
      datetime.date: DateType.__builders__,
      datetime.time: TimeType.__builders__,
      datetime.datetime: DateTimeType.__builders__,
      list: ListType.__builders__
    })

  @unittest.expectedFailure
  def test_register_1(self):
    DataType.register(InvalidTypeSubclass_1)

  @unittest.expectedFailure
  def test_register_2(self):
    DataType.register(InvalidTypeSubclass_2)

  @unittest.expectedFailure
  def test_register_3(self):
    DataType.register(InvalidTypeSubclass_3)

  def test_register_4(self):
    DataType.register(ValidTypeSubclass)
    self.assertEquals(
      DataType.registry[complex], ValidTypeSubclass.__builders__)


class ValueProcessorTests(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    DataType.register(ValidTypeSubclass)

  def test_missing_required(self):
    try:
      DataType.process_value(
        AttributeOptions('Foo', 'bar', required = True),
          None)
      self.assertFalse(True)
    except MissingRequiredValueError, e:
      self.assertEquals(e.parameters, {'attribute': 'Foo.bar'})

  def test_unrecognized_type(self):
    try:
      DataType.process_value(
        AttributeOptions('Foo', 'bar', type = InvalidStruct),
          'X')
      self.assertFalse(True)
    except UnrecognizedTypeError, e:
      self.assertEquals(e.parameters,
        {'attribute': 'Foo.bar', 'type': InvalidStruct})

  def test_plain_value(self):
    self.assertEquals(
      DataType.process_value(
        AttributeOptions('Foo', 'bar', type = complex),
          'X'), 'X')

  def test_filtered_value(self):
    self.assertEquals(
      DataType.process_value(
        AttributeOptions('Foo', 'bar', type = complex, delimiter = '/',
          filter_1 = True, filter_2 = True, filter_3 = True),
            'X'), 'X/1//2//3/')


class ObjectTypeTests(unittest.TestCase):

  def setUp(self):
    self.valid_attr_opts = AttributeOptions(
      'Foo', 'bar', type = ValidStruct, required = True)
    self.invalid_attr_opts = AttributeOptions(
      'Foo', 'baz', type = InvalidStruct)


  def test_unrecognized_type(self):
    try:
      ObjectType.value_of(
        InvalidStruct(), self.invalid_attr_opts)
      self.assertFalse(True)
    except UnrecognizedTypeError, e:
      self.assertEquals(e.parameters,
        {'attribute': 'Foo.baz', 'type': InvalidStruct})

  def test_value_of_none(self):
    self.assertEquals(
      ObjectType.value_of(None, self.valid_attr_opts),
      None)

  def test_value_of_same_type(self):
    x = ValidStruct(foo = 'FOO', bar = 'BAR')
    self.assertEquals(
      ObjectType.value_of(x, self.valid_attr_opts),
      x)

  def test_value_of_another_type(self):
    x = ValidStruct(foo = 'FOO', bar = 'BAR')
    y = AnotherValidStruct(foo = 'FOO', bar = 'BAR')
    self.assertEquals(
      ObjectType.value_of(y, self.valid_attr_opts),
      x)

  def test_value_of_dict(self):
    self.assertEquals(
      ObjectType.value_of(
        {'foo': 'FOO', 'bar': 'BAR'}, self.valid_attr_opts),
      ValidStruct(foo = 'FOO', bar = 'BAR'))

  def test_incompatible_type(self):
    try:
      _ = ObjectType.value_of(
        (), self.valid_attr_opts)
      self.assertFalse(True)
    except IncompatibleTypeError, e:
      self.assertEquals(e.parameters,
        {'attribute': 'Foo.bar', 'expected_type': ValidStruct,
          'found_type': tuple})

  def test_required_with_none(self):
    try:
      ObjectType.required(None, self.valid_attr_opts)
      self.assertFalse(True)
    except MissingRequiredValueError, e:
      pass

  def test_required_with_empty_struct(self):
    try:
      ObjectType.required(ValidStruct(), self.valid_attr_opts)
      self.assertFalse(True)
    except MissingRequiredValueError, e:
      pass

  def test_required_with_empty_dict(self):
    try:
      ObjectType.required({}, self.valid_attr_opts)
      self.assertFalse(True)
    except MissingRequiredValueError, e:
      pass


class BooleanTypeTests(unittest.TestCase):

  def setUp(self):
    self.attr_opts = AttributeOptions(
      'Foo', 'bar', type = bool)

  def test_value_of(self):
    self.assertFalse(BooleanType.value_of(None, self.attr_opts))
    self.assertFalse(BooleanType.value_of(False, self.attr_opts))
    self.assertFalse(BooleanType.value_of('False', self.attr_opts))
    self.assertFalse(BooleanType.value_of(0, self.attr_opts))
    self.assertFalse(BooleanType.value_of({}, self.attr_opts))
    self.assertFalse(BooleanType.value_of('', self.attr_opts))
    self.assertTrue(BooleanType.value_of(True, self.attr_opts))
    self.assertTrue(BooleanType.value_of('True', self.attr_opts))
    self.assertTrue(BooleanType.value_of(1, self.attr_opts))
    self.assertTrue(BooleanType.value_of('Something', self.attr_opts))


class NumericTypeTests(unittest.TestCase):

  def do_test_required(self):
    try:
      NumericType.required(None, self.attr_opts)
      self.assertFalse(True)
    except InvalidValueError, e:
      pass


class IntegerTypeTests(NumericTypeTests):

  def setUp(self):
    self.attr_opts = AttributeOptions(
      'Foo', 'bar', type = int, required = True)

  def test_value_of(self):
    self.assertEquals(IntegerType.value_of(1, self.attr_opts), 1)
    self.assertEquals(IntegerType.value_of(1L, self.attr_opts), 1)
    self.assertEquals(IntegerType.value_of(1.1, self.attr_opts), 1)
    self.assertEquals(IntegerType.value_of('1', self.attr_opts), 1)

  def test_required(self):
    self.do_test_required()


class LongTypeTests(NumericTypeTests):

  def setUp(self):
    self.attr_opts = AttributeOptions(
      'Foo', 'bar', type = long, required = True)

  def test_value_of(self):
    pass

  def test_required(self):
    self.do_test_required()


class FloatTypeTests(NumericTypeTests):

  def setUp(self):
    self.attr_opts = AttributeOptions(
      'Foo', 'bar', type = float, required = True)

  def test_value_of(self):
    pass

  def test_required(self):
    self.do_test_required()
