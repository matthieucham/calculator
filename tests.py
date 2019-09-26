import unittest
import calc


class TokenizeTest(unittest.TestCase):

    def test_empty(self):
        self.assertEqual([], calc.tokenize(''))

    def test_int_without_ops(self):
        self.assertEqual(['12'], calc.tokenize('12'))
        self.assertEqual(['12'], calc.tokenize('  12 '))
        self.assertEqual(['12'], calc.tokenize(' \t 12'))
        self.assertEqual(['12', '34'], calc.tokenize('12 34'))
        self.assertEqual(['12', '34'], calc.tokenize(' 12\n34  '))

    def test_float_without_ops(self):
        self.assertEqual(['1.2'], calc.tokenize('1.2'))
        self.assertEqual(['1.2'], calc.tokenize('  1.2 '))
        self.assertEqual(['1.2'], calc.tokenize(' \t 1.2'))
        self.assertEqual(['1.2', '34'], calc.tokenize('1.2 34'))
        self.assertEqual(['1.2', '3.4'], calc.tokenize(' 1.2\n3.4  '))

    def test_expressions(self):
        self.assertEqual(['1'], calc.tokenize('1'))
        self.assertEqual(['1', '+'], calc.tokenize('1+'))
        self.assertEqual(['1', '+', '2', '*', '3'], calc.tokenize('1+2*3'))
        self.assertEqual(['1', '+', '2', '*', '3', '/', '4'], calc.tokenize('1+2*3/4'))
        self.assertEqual(['1', '+', '2', '*', '3', '/', '4', '-', '5'], calc.tokenize('1+2*3/4-5'))
        self.assertEqual(['10', '+', '20', '*', '30', '/', '40', '-', '50'], calc.tokenize('10+20*30/40-50'))
        self.assertEqual(['10', '+', '20', '*', '30', '/', '40', '-', '50'], calc.tokenize(' 10 + 20 * 30 / 40 - 50 '))
