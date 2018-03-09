#
# Copyright
#


import collections
import json

from structmodel.exceptions import *
from structmodel.options import StructOptions, AttributeOptions
from structmodel.types import AbstractStruct, DataType, CustomList


class StructOverlay(object):

  def __init__(self, struct_name, **struct_opts):
    self.name = struct_name
    self.opts = StructOptions(struct_name, **struct_opts)
    self.validators = []
    self.attrs = {}

  def add_attribute(self, attr_name, **attr_opts):
    opts = AttributeOptions(self.name, attr_name, **attr_opts)
    self.attrs[attr_name] = opts
    return opts

  def del_attribute(self, attr_name):
    return self.attrs.pop(attr_name, None)

  def set_options(self, **struct_opts):
    self.opts.update(
      StructOptions.filter_internals(struct_opts))

  def set_attribute_options(self, attr_name, **attr_opts):
    if attr_name in self.attrs:
      self.attrs[attr_name].update(
        AttributeOptions.filter_internals(attr_opts))

  def unset_options(self, *struct_opts):
    for key in struct_opts:
      if key not in StructOptions.internals:
        self.opts.pop(key, None)

  def unset_attribute_options(self, attr_name, *attr_opts):
    if attr_name in self.attrs:
      for key in attr_opts:
        if key not in AttributeOptions.internals:
          self.attrs[attr_name].pop(key, None)

  def add_validator(self, validator, **validator_opts):
    self.validators.append((validator, validator_opts))

  def process_set_value(self, attr_name, value):
    if attr_name.startswith('_'):
      return value
    attr_opts = self.attrs.get(attr_name, None)
    if not attr_opts:
      if self.opts.open:
        attr_opts = self.add_attribute(attr_name)
      else:
        raise UndefinedAttributeError(self.name, attr_name)
    return DataType.process_value(attr_opts, value)

  def process_del_value(self, attr_name):
    if attr_name.startswith('_'):
      return
    if self.opts.lenient:
      return
    attr_opts = self.attrs.get(attr_name, None)
    if attr_opts and attr_opts.required:
      raise MissingRequireAttributeError(
        attr_opts.namespace, attr_opts.name)

  def process_validate(self, struct):
    if not isinstance(struct, AbstractStruct):
      raise InvalidStructType(struct.__class__)
    for attr_opts in self.attrs.values():
      attr_name = attr_opts.name
      attr_type = attr_opts.type
      if attr_name.startswith('_'):
        continue
      _ = attr_opts.default
      if _ and hasattr(_, '__call__'):
        def_args = attr_opts.default_args
        _ = _.__call__(*def_args) if def_args else _.__call__()
      if _ != None:
        struct[attr_name] = self.process_set_value(attr_name, _)
      if attr_opts.required:
        if attr_name not in struct:
          raise MissingRequireAttributeError(
            attr_opts.namespace, attr_opts.name)
        if struct.get(attr_name, None) == None:
          raise MissingRequiredValueError(
            attr_opts.namespace, attr_opts.name)
      if issubclass(attr_type, AbstractStruct):
        nested_struct = struct.get(attr_name, None)
        if nested_struct != None:
          nested_struct.validate()
      elif attr_type == list:
        _ = struct.get(attr_name, None)
        if _ == None:
          if attr_opts.min_length > 0:
            raise MissingRequiredValueError(
              attr_opts.namespace, attr_opts.name)
        else:
          if isinstance(_, CustomList):
            _.check_length(0)
          else:
            raise UnexpectedError(
              'unsupported list type: %s' % type(_))
          if _ and issubclass(attr_opts.cache.item.type,
            AbstractStruct):
            for nested_struct in _:
              if nested_struct != None:
                nested_struct.validate()
    if self.validators:
      for validator in self.validators:
        if not validator[0].__call__(struct):
          raise StructValidationError(
            self.name, validator[1].get('message', None))

  def to_json(self, struct):
    def __json__(x):
      if hasattr(x, '__dict__'):
        return {k: v for k, v in x.__dict__.items() if not k.startswith('_')}
      if hasattr(x, 'isoformat'):
        return x.isoformat()
      return str(x)
    if not isinstance(struct, AbstractStruct):
      raise InvalidStructType(struct.__class__)
    return json.dumps(struct,
        default = __json__,
        indent = self.opts.json_indent,
        separators = (
          self.opts.json_item_sep,
          self.opts.json_dict_sep
        )
      )


class Model(object):

  registry = {}

  @classmethod
  def overlay(cls, struct_name):
    if struct_name in cls.registry:
      return cls.registry[struct_name]
    else:
      raise UnknownStructError(struct_name)

  @classmethod
  def declare(cls, struct_name = None, **struct_opts):
    def decorator(struct_cls):
      if not issubclass(struct_cls, AbstractStruct):
        raise InvalidStructType(struct_cls)
      _ = struct_name if struct_name else struct_cls.__name__
      setattr(struct_cls, '__internal_name__', _)
      cls.registry[_] = StructOverlay(_, **struct_opts)
      return struct_cls
    return decorator

  @classmethod
  def define(cls, attr_name, **attr_opts):
    def decorator(struct_cls):
      cls.overlay_of(struct_cls).\
        add_attribute(attr_name, **attr_opts)
      return struct_cls
    return decorator

  @classmethod
  def validate(cls, validator_func, **validator_opts):
    def decorator(struct_cls):
      if not hasattr(validator_func, '__call__'):
        raise UnexpectedError(
          'invalid validator function (%s)' % validator_func)
      cls.overlay_of(struct_cls).add_validator(
        validator_func, **validator_opts)
      return struct_cls
    return decorator

  @classmethod
  def overlay_of(cls, struct_cls):
    if not issubclass(struct_cls, AbstractStruct):
      raise InvalidStructType(struct_cls)
    if not hasattr(struct_cls, '__internal_name__'):
      raise UndeclaredStructError(struct_cls)
    _ = cls.registry.get(struct_cls.__internal_name__, None)
    if not _:
      raise UnknownStructError(struct_cls.__internal_name__)
    return _


class Struct(AbstractStruct):

  def __getitem__(self, key):
    return self.__dict__.__getitem__(key)

  def __setitem__(self, key, value):
    final_value = Model.overlay_of(
      self.__class__).process_set_value(
        key, value)
    self.__dict__.__setitem__(key, final_value)

  def __delitem__(self, key):
    Model.overlay_of(
      self.__class__).process_del_value(
        key)
    self.__dict__.__delitem__(key)

  def validate(self):
    Model.overlay_of(
      self.__class__).process_validate(
        self)
    return self

  def json(self):
    return Model.overlay_of(
      self.__class__).to_json(
        self)
