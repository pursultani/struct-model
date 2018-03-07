#
# Copyright
#


import unittest

from structmodel.utils import *


class UtilsTest(unittest.TestCase):

  def test_empty_qname(self):
    self.assertEquals(
      qname(),
        '')

  def test_plain_qname(self):
    self.assertEquals(
      qname('foo'),
        'foo')

  def test_more_qname(self):
    self.assertEquals(
      qname('foo', 'bar', 'baz'),
        'foo.bar.baz')
