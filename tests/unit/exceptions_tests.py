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
