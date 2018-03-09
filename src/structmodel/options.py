#
# Copyright
#


class Options(dict):

  defaults = {}

  def __getitem__(self, key):
    if key in self:
      return super(Options, self).__getitem__(key)
    else:
      default = self.__class__.defaults
      return default[key] if default and key in default else None

  def __getattr__(self, key):
    return self.__getitem__(key)

  def __setattr__(self, key, value):
    self.__setitem__(key, value)

  def __delattr__(self, key):
    self.__delitem__(key)

  @classmethod
  def filter_internals(cls, opts):
    return {key: opts[key] for key in opts if key not in cls.internals}


class StructOptions(Options):

  defaults = {
    'open': False,
    'lenient': False,
    'json_indent': 2,
    'json_item_sep': ', ',
    'json_dict_sep': ': '
  }

  internals = ('name', 'cache')

  def __init__(self, name, **opts):
    self.update(opts)
    self.name = name
    self.cache = Options()


class AttributeOptions(Options):

  defaults = {
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

  internals = ('namespace', 'name', 'cache')

  def __init__(self, namespace, name, **opts):
    self.update(opts)
    self.name = name
    self.namespace = namespace
    self.cache = Options()
