#
# Copyright
#


from structmodel.utils import qname


def fullname(x):
  return '%s%s' % (
    x.__module__ + '.' if hasattr(x, '__module__') else '',
      x.__class__.__name__)

def stringify(ex):
  return '%s%s' % (ex.message if ex.message else '',
    ex.parameters if ex.parameters else '')


class ApplicationException(Exception):

  def __init__(self, message, **parameters):
    self.message = message
    self.parameters = parameters

  def __str__(self):
    return stringify(self)


class SystemException(Exception):

  def __init__(self, message, reason = None, **parameters):
    self.message = message
    self.reason = reason
    self.parameters = parameters

  def __str__(self):
    if self.reason:
      return '%s\n\t%s: %s' % (stringify(self),
        fullname(self.reason), str(self.reason))
    else:
      return stringify(self)


class FrameworkException(Exception):

  def __init__(self, message = None, **parameters):
    self.message = message
    self.parameters = parameters

  def __str__(self):
    return stringify(self)


class ModelException(FrameworkException):

  pass


class TypeException(FrameworkException):

  pass


class ValidationException(FrameworkException):

  pass


class UnknownStructError(ModelException):

  def __init__(self, name):
    super(UnknownStructError, self).__init__(
      name = name)


class UndeclaredStructError(ModelException):

  def __init__(self, struct_type):
    super(UndeclaredStructError, self).__init__(
      struct_type = struct_type)


class InvalidStructType(ModelException):

  def __init__(self, struct_type):
    super(InvalidStructType, self).__init__(
      struct_type = struct_type)


class UndefinedAttributeError(ModelException):

  def __init__(self, namespace, name):
    super(UndefinedAttributeError, self).__init__(
      attribute = qname(namespace, name))


class MissingRequireAttributeError(ModelException):

  def __init__(self, namespace, name):
    super(MissingRequireAttributeError, self).__init__(
      attribute = qname(namespace, name))


class UnrecognizedTypeError(TypeException):

  def __init__(self, namespace, name, type):
    super(UnrecognizedTypeError, self).__init__(
      attribute = qname(namespace, name), type = type)


class IncompatibleTypeError(TypeException):

  def __init__(self, namespace, name, expected_type, found_type):
    super(IncompatibleTypeError, self).__init__(
      attribute = qname(namespace, name),
        expected_type = expected_type, found_type = found_type)


class NonIterableTypeError(TypeException):

  def __init__(self, namespace, name, found_type):
    super(NonIterableTypeError, self).__init__(
      attribute = qname(namespace, name), found_type = found_type)


class MissingRequiredValueError(ValidationException):

  def __init__(self, namespace, name):
    super(MissingRequiredValueError, self).__init__(
      attribute = qname(namespace, name))


class PatternMismatchError(ValidationException):

  def __init__(self, namespace, name, pattern, value):
    super(PatternMismatchError, self).__init__(
      attribute = qname(namespace, name), pattern = pattern,
        value = value)


class ListBoundaryViolationError(ValidationException):

  def __init__(self, namespace, name, estimated_length,
    min_length = None, max_length = None):
    super(ListBoundaryViolationError, self).__init__(
      attribute = qname(namespace, name),
        estimated_length = estimated_length, min_length = min_length,
          max_length = max_length)


class InvalidValueError(ValidationException):

  def __init__(self, namespace, name, validation, value):
    super(InvalidValueError, self).__init__(
      attribute = qname(namespace, name), validation = validation,
        value = value)


class StructValidationError(ValidationException):

  def __init__(self, name, explanation):
    super(StructValidationError, self).__init__(
      name = name, explanation = explanation)


class UnexpectedError(FrameworkException):

  def __init__(self, message):
    super(UnexpectedError, self).__init__(message)
