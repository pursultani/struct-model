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
