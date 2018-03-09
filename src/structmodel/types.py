#
# Copyright
#


import collections
import datetime
import re

from structmodel.utils import *
from structmodel.exceptions import *
from structmodel.options import AttributeOptions


def comparable_dict(rhs, *args):
  if rhs == None:
    return None
  if isinstance(rhs, dict):
    return rhs
  if hasattr(rhs, '__dict__'):
    return rhs.__dict__
  if args:
    return args[0]
  raise TypeError('incomparable type')


class AbstractStruct(collections.MutableMapping):

  def __init__(self, **source):
    super(AbstractStruct, self).__init__()
    self.assign(**source)

  def __iter__(self):
    return self.__dict__.__iter__()

  def __getitem__(self, key):
    raise NotImplementedError()

  def __setitem__(self, key, value):
    raise NotImplementedError()

  def __delitem__(self, key):
    raise NotImplementedError()

  def __getattr__(self, key):
    return self.__getitem__(key)

  def __setattr__(self, key, value):
    self.__setitem__(key, value)

  def __delattr__(self, key):
    self.__delitem__(key)

  def __len__(self):
    return len(self.__dict__)

  def __cmp__(self, rhs):
    return self.__dict__.__cmp__(
      comparable_dict(rhs))

  def __lt__(self, rhs):
    return self.__dict__.__lt__(
      comparable_dict(rhs))

  def __gt__(self, rhs):
    return self.__dict__.__gt__(
      comparable_dict(rhs))

  def __le__(self, rhs):
    return self.__dict__.__le__(
      comparable_dict(rhs))

  def __ge__(self, rhs):
    return self.__dict__.__ge__(
      comparable_dict(rhs))

  def __eq__(self, rhs):
    return False if rhs == None \
       else self.__dict__.__eq__(
        comparable_dict(rhs, rhs))

  def __ne__(self, rhs):
    return not self.__eq__(rhs)

  def __str__(self):
    return str(self.__dict__)

  def __repr__(self):
    return str(self.__dict__)

  def assign(self, **source):
    for item in source.iteritems():
      self.__setitem__(item[0], item[1])
    return self

  def validate(self):
    raise NotImplementedError()

  def json(self):
    raise NotImplementedError()


class DataType(object):

  registry = {}

  @classmethod
  def register(cls, type_cls):
    if not issubclass(type_cls, DataType):
      raise UnexpectedError(
        '%s is not a valid type subclass.' % type_cls)
    if not hasattr(type_cls, '__type__'):
      raise UnexpectedError(
        '%s does not have type declaration.' % type_cls)
    if not hasattr(type_cls, '__builders__'):
      raise UnexpectedError(
        '%s does not have builders declaration.' % type_cls)
    cls.registry[type_cls.__type__] = type_cls.__builders__
    return type_cls

  @classmethod
  def process_value(cls, opts, value):
    if opts.required and value == None:
      raise MissingRequiredValueError(opts.namespace, opts.name)
    next_value = value
    filters = opts.cache.filters
    if not filters:
      _ = opts.type
      if issubclass(_, AbstractStruct):
        _ = object
      elif _ not in cls.registry:
        raise UnrecognizedTypeError(opts.namespace, opts.name, _)
      filters = []
      for builder_func in cls.registry[_]:
        filter_func =  builder_func(opts)
        if filter_func:
          filters.append(filter_func)
      opts.cache.filters = filters
    for filter_func in filters:
      next_value = filter_func(next_value, opts)
    return next_value


class GenericType(DataType):

  @classmethod
  def required(cls, x, opts):
    if opts.required and not x:
      raise MissingRequiredValueError(opts.namespace, opts.name)
    return x


@DataType.register
class ObjectType(GenericType):

  __type__ = object
  __builders__ = [
    lambda opts: ObjectType.value_of,
    lambda opts: ObjectType.required \
      if opts.required else None
  ]

  @classmethod
  def value_of(cls, x, opts):
    if x == None:
      return None
    _ = opts.type
    if not issubclass(_, AbstractStruct):
      raise UnrecognizedTypeError(opts.namespace, opts.name, _)
    if isinstance(x, _):
      return x
    if isinstance(x, dict):
      return _().assign(**x)
    if hasattr(x, '__dict__'):
      return _().assign(**x.__dict__)
    raise IncompatibleTypeError(opts.namespace, opts.name, _, type(x))


@DataType.register
class StringType(GenericType):

  __type__ = str
  __builders__ = [
    lambda opts: StringType.value_of,
    lambda opts: StringType.required \
      if opts.required else None,
    lambda opts: StringType.match \
      if opts.pattern else None,
    lambda opts: StringType.strip \
      if opts.strip else None,
    lambda opts: StringType.cleanse \
      if opts.cleanse else None,
    lambda opts: StringType.normalize \
      if opts.normalize else None
  ]

  @classmethod
  def value_of(cls, x, opts):
    return unicode(x)

  @classmethod
  def match(cls, s, opts):
    pattern = opts.pattern
    if pattern and not re.match(pattern, s):
      raise PatternMismatchError(
        opts.namespace, opts.name, pattern, s)
    return s

  @classmethod
  def strip(cls, s, opts):
    if hasattr(s, 'strip'):
      return s.strip()

  @classmethod
  def cleanse(cls, s, opts):
    return cleanse_str(s)

  @classmethod
  def normalize(cls, s, opts):
    return normalize_str(s)



@DataType.register
class BooleanType(DataType):

  __type__ = bool
  __builders__ = [
    lambda opts: BooleanType.value_of
  ]

  @classmethod
  def value_of(cls, x, opts):
    if isinstance(x, bool):
      return x
    if str(x).lower() == 'true':
      return True
    if str(x).lower() == 'false':
      return False
    return bool(x)


class NumericType(DataType):

  @classmethod
  def value_of(cls, x, opts):
    if isinstance(x, cls.__type__):
      return x
    if is_numeric(x):
      return cls.__type__(x)
    ordinal = as_ordinal(x)
    return cls.__type__(ordinal if ordinal else str(x))

  @classmethod
  def required(cls, n, opts):
    if opts.required and n == None:
      raise InvalidValueError(
        opts.namespace, opts.name, 'required', n)
    return n


@DataType.register
class IntegerType(NumericType):

  __type__ = int
  __builders__ = [
    lambda opts: IntegerType.value_of,
    lambda opts: IntegerType.required \
      if opts.required else None
  ]


@DataType.register
class LongType(NumericType):

  __type__ = long
  __builders__ = [
    lambda opts: LongType.value_of,
    lambda opts: LongType.required \
      if opts.required else None
  ]


@DataType.register
class FloatType(NumericType):

  __type__ = float
  __builders__ = [
    lambda opts: FloatType.value_of,
    lambda opts: FloatType.required \
      if opts.required else None
  ]


class TemporalType(GenericType):

  @classmethod
  def parse(cls, x, opts):
    return datetime.datetime.strptime(str(x),
      opts.format if opts.format else cls.DEFAULT_FORMAT) \
        if x else None


@DataType.register
class DateType(TemporalType):

  __type__ = datetime.date
  __builders__ = [
    lambda opts: DateType.value_of,
    lambda opts: DateType.required \
      if opts.required else None
  ]

  DEFAULT_FORMAT = '%Y-%m-%d'

  @classmethod
  def value_of(cls, x, opts):
    if isinstance(x, datetime.date):
      return x
    if isinstance(x, datetime.datetime):
      return x.date()
    if is_numeric(x):
      return datetime.date.fromtimestamp(x)
    return cls.parse(x, opts).date()


@DataType.register
class TimeType(TemporalType):

  __type__ = datetime.time
  __builders__ = [
    lambda opts: TimeType.value_of,
    lambda opts: TimeType.required \
      if opts.required else None
  ]

  DEFAULT_FORMAT = '%H:%M:%S'

  @classmethod
  def value_of(cls, x, opts):
    if isinstance(x, datetime.time):
      return x
    if isinstance(x, datetime.datetime):
      return x.time()
    return cls.parse(x, opts).time()


@DataType.register
class DateTimeType(TemporalType):

  __type__ = datetime.datetime
  __builders__ = [
    lambda opts: DateTimeType.value_of,
    lambda opts: DateTimeType.required \
      if opts.required else None
  ]

  DEFAULT_FORMAT = '%Y-%m-%dT%H:%M:%S'

  @classmethod
  def value_of(cls, x, opts):
    if isinstance(x, datetime.datetime):
      return x
    if isinstance(x, datetime.date):
      return datetime.datetime.combine(x, datetime.time())
    if isinstance(x, datetime.time):
      return datetime.datetime.combine(datetime.date.today(), x)
    if is_numeric(x):
      return datetime.datetime.fromtimestamp(x)
    return cls.parse(x, opts)


class CustomList(list):

  def __init__(self, opts):
    self.opts = opts

  def check_length(self, delta):
    _est = self.__len__() + delta
    _min = self.opts.min_length
    _max = self.opts.max_length
    if _min and _est < _min:
      raise ListBoundaryViolationError(self.opts.namespace,
        self.opts.name, _est, min_length = _min,
          max_length = _max if _max else None)
    if _max and _est > _max:
      raise ListBoundaryViolationError(self.opts.namespace,
        self.opts.name, _est, max_length = _max,
          min_length = _min if _min else None)

  def process_value(self, value):
    item_opts = self.opts.cache.item
    if not item_opts:
      raise UnexpectedError(
        '%s: invalid list setup' % qname(
          self.opts.namespace, self.opts.name))
    return DataType.process_value(item_opts, value)


  def __add__(self, x):
    return super(CustomList, self). \
      __add__(map(self.process_value, x))

  def __iadd__(self, x):
    self.check_length(len(x))
    return super(CustomList, self). \
      __iadd__(map(self.process_value, x))

  def __imul__(self, n):
    self.check_length(len(self) * (n - 1))
    return super(CustomList, self).__imul__(n)

  def __setitem__(self, i, y):
    return super(CustomList, self). \
      __setitem__(i, self.process_value(y))

  def __setslice__(self, i, j, x):
    self.check_length(i - min(len(self), j) + len(x))
    return super(CustomList, self). \
      __setslice__(i, j, map(self.process_value, x))

  def __delitem__(self, i):
    self.check_length(-1)
    super(CustomList, self).__delitem__(i)

  def __delslice__(self, i, j):
    self.check_length(i - j)
    super(CustomList, self).__delslice__(i, j)

  def append(self, x):
    self.check_length(1)
    super(CustomList, self). \
      append(self.process_value(x))

  def extend(self, x):
    self.check_length(len(x))
    super(CustomList, self). \
      extend(map(self.process_value, x))

  def insert(self, i, x):
    self.check_length(1)
    super(CustomList, self). \
      insert(i, self.process_value(x))

  def pop(self, *args):
    self.check_length(-1)
    return super(CustomList, self).pop(*args)

  def remove(self, x):
    if x in self:
      self.check_length(-1)
    super(CustomList, self).remove(x)


@DataType.register
class ListType(GenericType):

  __type__ = list
  __builders__ = [
    lambda opts: ListType.value_of,
    lambda opts: ListType.required \
      if opts.required else None
  ]

  @classmethod
  def value_of(cls, x, opts):
    if not opts.cache.item:
      opts.cache.item = AttributeOptions(opts.namespace,
        opts.name + '[*]', **{key[5:]: opts[key]  \
          for key in opts if key.startswith('item_')})
    value = CustomList(opts)
    if not hasattr(x, '__iter__') or not hasattr(x, '__len__'):
      raise NonIterableTypeError(opts.namespace, opts.name, type(x))
    value.extend(x)
    return value
