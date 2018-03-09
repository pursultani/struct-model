#
# Copyright
#


import unittest
import datetime

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

  def test_valid_safe_cast(self):
    self.assertEquals(
      safe_cast('1', int),
        1)

  def test_invalid_safe_cast(self):
    self.assertEquals(
      safe_cast('?', int, 0),
        0)

  def test_valid_as_ordinal(self):
    today = datetime.datetime.now()
    self.assertEquals(
      as_ordinal(today), today.toordinal())

  def test_invalid_as_ordinal(self):
    self.assertEquals(
      as_ordinal('?', 0), 0)

  def test_is_numeric(self):
    self.assertTrue(is_numeric(0))
    self.assertTrue(is_numeric(0L))
    self.assertTrue(is_numeric(0.0))
    self.assertFalse(is_numeric('0'))
    self.assertFalse(is_numeric([]))
