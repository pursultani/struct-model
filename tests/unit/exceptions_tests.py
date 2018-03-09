#
# Copyright
#


import unittest

from structmodel.exceptions import *


class TestExceptions(unittest.TestCase):

  @unittest.expectedFailure
  def test_empty_ApplicationException(self):
    raise ApplicationException()

  def test_plain_ApplicationException(self):
    try:
      raise ApplicationException('Ouch!')
    except ApplicationException, e:
      self.assertFalse(e.parameters)
      self.assertEquals(e.message, 'Ouch!')
      self.assertEquals(str(e), 'Ouch!')

  def test_parameterized_ApplicationException(self):
    try:
      raise ApplicationException('Ouch!',
        foo = 'FOO', bar = 'BAR')
    except ApplicationException, e:
      self.assertTrue(e.parameters)
      self.assertEquals(e.message, 'Ouch!')
      self.assertEquals(e.parameters, {'foo': 'FOO', 'bar': 'BAR'})
      self.assertEquals(str(e),
        "Ouch!{'foo': 'FOO', 'bar': 'BAR'}")

  @unittest.expectedFailure
  def test_empty_FrameworkException(self):
    raise FrameworkException()

  def test_plain_FrameworkException(self):
    try:
      raise FrameworkException('Ouch!')
    except FrameworkException, e:
      self.assertFalse(e.parameters)
      self.assertEquals(e.message, 'Ouch!')
      self.assertEquals(str(e), 'Ouch!')

  def test_parameterized_FrameworkException(self):
    try:
      raise FrameworkException('Ouch!',
        foo = 'FOO', bar = 'BAR')
    except FrameworkException, e:
      self.assertTrue(e.parameters)
      self.assertEquals(e.message, 'Ouch!')
      self.assertEquals(e.parameters, {'foo': 'FOO', 'bar': 'BAR'})
      self.assertEquals(str(e),
        "Ouch!{'foo': 'FOO', 'bar': 'BAR'}")

  @unittest.expectedFailure
  def test_empty_SystemException(self):
    raise SystemException()

  def test_plain_SystemException(self):
    try:
      raise SystemException('Ouch!')
    except SystemException, e:
      self.assertFalse(e.parameters)
      self.assertFalse(e.reason)
      self.assertEquals(e.message, 'Ouch!')
      self.assertEquals(str(e), 'Ouch!')

  def test_parameterized_SystemException(self):
    try:
      raise SystemException('Ouch!',
        foo = 'FOO', bar = 'BAR')
    except SystemException, e:
      self.assertTrue(e.parameters)
      self.assertFalse(e.reason)
      self.assertEquals(e.message, 'Ouch!')
      self.assertEquals(e.parameters, {'foo': 'FOO', 'bar': 'BAR'})
      self.assertEquals(str(e),
        "Ouch!{'foo': 'FOO', 'bar': 'BAR'}")

  def test_plain_SystemException_with_RuntimeError_reason(self):
    try:
      raise SystemException('Ouch!', RuntimeError('Oops!'))
    except SystemException, e:
      self.assertFalse(e.parameters)
      self.assertTrue(e.reason)
      self.assertEquals(e.message, 'Ouch!')
      self.assertIsInstance(e.reason, RuntimeError)
      self.assertEquals(str(e.reason), 'Oops!')
      self.assertEquals(str(e),
        'Ouch!\n\tRuntimeError: Oops!')

  def test_plain_SystemException_with_ApplicationException_reason(self):
    try:
      raise SystemException('Ouch!', ApplicationException('Oops!'))
    except SystemException, e:
      self.assertFalse(e.parameters)
      self.assertTrue(e.reason)
      self.assertEquals(e.message, 'Ouch!')
      self.assertIsInstance(e.reason, ApplicationException)
      self.assertEquals(str(e.reason), 'Oops!')
      self.assertEquals(str(e),
        'Ouch!\n\tstructmodel.exceptions.ApplicationException: Oops!')

  def test_parameterized_SystemException_with_RuntimeError_reason(self):
    try:
      raise SystemException('Ouch!', RuntimeError('Oops!'),
        foo = 'FOO', bar = 'BAR')
    except SystemException, e:
      self.assertTrue(e.parameters)
      self.assertTrue(e.reason)
      self.assertEquals(e.message, 'Ouch!')
      self.assertIsInstance(e.reason, RuntimeError)
      self.assertEquals(str(e.reason), 'Oops!')
      self.assertEquals(e.parameters, {'foo': 'FOO', 'bar': 'BAR'})
      self.assertEquals(str(e),
        "Ouch!{'foo': 'FOO', 'bar': 'BAR'}\n\tRuntimeError: Oops!")

  def test_nested_SystemException(self):
    try:
      raise SystemException(
        'Ouch!', SystemException(
          'Oops!', FrameworkException('Oy Vey!')
        )
      )
    except SystemException, e:
      self.assertFalse(e.parameters)
      self.assertTrue(e.reason)
      self.assertTrue(e.reason.reason)
      self.assertEquals(e.message, 'Ouch!')
      self.assertIsInstance(e.reason, SystemException)
      self.assertIsInstance(e.reason.reason, FrameworkException)
      self.assertEquals(e.reason.message, 'Oops!')
      self.assertEquals(e.reason.reason.message, 'Oy Vey!')
      self.assertEquals(str(e),
        "Ouch!\n\tstructmodel.exceptions.SystemException: Oops!\n\tstructmodel.exceptions.FrameworkException: Oy Vey!")


class FooStruct:

  pass


class ExceptionsTests(unittest.TestCase):

  def test_UnknownStructError(self):
    try:
      raise UnknownStructError('Foo')
    except UnknownStructError, e:
      self.assertEquals(e.parameters,
        {'name': 'Foo'})


  def test_UndeclaredStructError(self):
    try:
      raise UndeclaredStructError(FooStruct)
    except UndeclaredStructError, e:
      self.assertEquals(e.parameters,
        {'struct_type': FooStruct})

  def test_InvalidStructType(self):
    try:
      raise InvalidStructType(FooStruct)
    except InvalidStructType, e:
      self.assertEquals(e.parameters,
        {'struct_type': FooStruct})

  def test_UndefinedAttributeError(self):
    try:
      raise UndefinedAttributeError('Foo', 'bar')
    except UndefinedAttributeError, e:
      self.assertEquals(e.parameters,
        {'attribute': 'Foo.bar'})

  def test_MissingRequireAttributeError(self):
    try:
      raise MissingRequireAttributeError('Foo', 'bar')
    except MissingRequireAttributeError, e:
      self.assertEquals(e.parameters,
        {'attribute': 'Foo.bar'})

  def test_UnrecognizedTypeError(self):
    try:
      raise UnrecognizedTypeError('Foo', 'bar', FooStruct)
    except UnrecognizedTypeError, e:
      self.assertEquals(e.parameters,
        {'attribute': 'Foo.bar', 'type': FooStruct})

  def test_IncompatibleTypeError(self):
    try:
      raise IncompatibleTypeError('Foo', 'bar', str, int)
    except IncompatibleTypeError, e:
      self.assertEquals(e.parameters,
        {'attribute': 'Foo.bar', 'expected_type': str, 'found_type': int})

  def test_NonIterableTypeError(self):
    try:
      raise NonIterableTypeError('Foo', 'bar', FooStruct)
    except NonIterableTypeError, e:
      self.assertEquals(e.parameters,
        {'attribute': 'Foo.bar', 'found_type': FooStruct})

  def test_MissingRequiredValueError(self):
    try:
      raise MissingRequiredValueError('Foo', 'bar')
    except MissingRequiredValueError, e:
      self.assertEquals(e.parameters,
        {'attribute': 'Foo.bar'})

  def test_PatternMismatchError(self):
    try:
      raise PatternMismatchError('Foo', 'bar', r'^1\.0$', '2.0')
    except PatternMismatchError, e:
      self.assertEquals(e.parameters,
        {'attribute': 'Foo.bar', 'pattern': r'^1\.0$', 'value': '2.0'})

  def test_ListBoundaryViolationError_1(self):
    try:
      raise ListBoundaryViolationError('Foo', 'bar', 1, min_length = 2)
    except ListBoundaryViolationError, e:
      self.assertEquals(e.parameters,
        {'attribute': 'Foo.bar', 'estimated_length': 1, 'min_length': 2, 'max_length': None})

  def test_ListBoundaryViolationError_2(self):
    try:
      raise ListBoundaryViolationError('Foo', 'bar', 2, max_length = 1)
    except ListBoundaryViolationError, e:
      self.assertEquals(e.parameters,
        {'attribute': 'Foo.bar', 'estimated_length': 2, 'min_length': None, 'max_length': 1})

  def test_ListBoundaryViolationError_3(self):
    try:
      raise ListBoundaryViolationError('Foo', 'bar', 0, min_length = 1, max_length = 2)
    except ListBoundaryViolationError, e:
      self.assertEquals(e.parameters,
        {'attribute': 'Foo.bar', 'estimated_length': 0, 'min_length': 1, 'max_length': 2})

  def test_InvalidValueError(self):
    try:
      raise InvalidValueError('Foo', 'bar', 'custom', 0)
    except InvalidValueError, e:
      self.assertEquals(e.parameters,
        {'attribute': 'Foo.bar', 'validation': 'custom', 'value': 0})

  def test_StructValidationError(self):
    try:
      raise StructValidationError('Foo', 'Oops!')
    except StructValidationError, e:
      self.assertEquals(e.parameters,
        {'name': 'Foo', 'explanation': 'Oops!'})

  def test_UnexpectedError(self):
    try:
      raise UnexpectedError('Ouch!')
    except UnexpectedError, e:
      self.assertFalse(e.parameters)
      self.assertEquals(e.message, 'Ouch!')
