#
# Copyright
#


def qname(*parts):
  result = ''
  for part in parts:
    if result:
      result += '.' + part
    else:
      result = part
  return result


def safe_cast(value, to_type, default = None):
    try:
        return to_type(value)
    except ValueError:
        return default


def as_ordinal(x, default = None):
  if hasattr(x, 'toordinal'):
    return x.toordinal()
  else:
    return default


def is_numeric(x):
  return reduce(
    lambda r, t: r or isinstance(x, t), (int, long, float),
      False)
