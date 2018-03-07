#
# Copyright
#


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
