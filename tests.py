import unittest
import calc
import os


class TokenizeTest(unittest.TestCase):
    """
    Unit tests for calc.tokenize()
    """

    def test_empty(self):
        self.assertEqual([], calc.tokenize(''))

    def test_remove_quotes(self):
        self.assertEqual('2+2', calc.remove_quotes('\'2+2\''))
        self.assertEqual('2+2', calc.remove_quotes('\"2+2\"'))
        self.assertEqual('2+2', calc.remove_quotes('2+2'))

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
        self.assertEqual(['-', '1', '+', '2', '*', '3'], calc.tokenize('-1+2*3'))
        self.assertEqual(['-', '1.5', '+', '2', '*', '3'], calc.tokenize('-1.5+2*3'))
        self.assertEqual(['-', '1.5', '+', '2', '*', '3'], calc.tokenize('- 1.5+2*3'))
        self.assertEqual(['1', '+', '2', '*', '3', '/', '4'], calc.tokenize('1+2*3/4'))
        self.assertEqual(['1', '+', '-', '2', '*', '-', '3', '/', '4'], calc.tokenize('1+-2*-3/4'))
        self.assertEqual(['1', '+', '2', '*', '3', '/', '4', '-', '5'], calc.tokenize('1+2*3/4-5'))
        self.assertEqual(['10', '+', '20', '*', '30', '/', '40', '-', '50'], calc.tokenize('10+20*30/40-50'))
        self.assertEqual(['11.0', '+', '22.0', '*', '33.0', '/', '44.0', '-', '55.0'],
                         calc.tokenize('11.0+22.0*33.0/44.0-55.0'))
        self.assertEqual(['10', '+', '20', '*', '30', '/', '40', '-', '50'], calc.tokenize(' 10 + 20 * 30 / 40 - 50 '))


class ValidateTokenTest(unittest.TestCase):
    def test_none(self):
        with self.assertRaises(calc.InvalidTokenError):
            calc.validate_token(None)

    def test_operators(self):
        for op in "+-*/":
            calc.validate_token(op)

    def test_numbers(self):
        calc.validate_token('0')
        calc.validate_token('5')
        calc.validate_token('5.5')
        calc.validate_token('00.000')
        calc.validate_token('10e2')
        calc.validate_token('   45')

    def test_pars(self):
        calc.validate_token('(')
        calc.validate_token(')')

    def test_text(self):
        with self.assertRaises(calc.InvalidTokenError):
            calc.validate_token('a')
        with self.assertRaises(calc.InvalidTokenError):
            calc.validate_token('azerty')


class OperatorTest(unittest.TestCase):
    def test_compare(self):
        self.assertTrue(calc.Divide() > calc.Plus())
        self.assertTrue(calc.Multiply() > calc.Plus())
        self.assertTrue(calc.Multiply() > calc.Minus())
        self.assertTrue(calc.Divide() > calc.Minus())
        self.assertFalse(calc.Divide() < calc.Plus())
        self.assertFalse(calc.Multiply() < calc.Plus())
        self.assertFalse(calc.Multiply() < calc.Minus())
        self.assertFalse(calc.Divide() < calc.Minus())
        self.assertTrue(calc.Minus() == calc.Plus())
        self.assertFalse(calc.Multiply() == calc.Plus())
        self.assertTrue(calc.UnaryMinus() < calc.Multiply())
        self.assertTrue(calc.UnaryMinus() < calc.Divide())
        self.assertTrue(calc.UnaryMinus() > calc.Plus())
        self.assertTrue(calc.UnaryMinus() > calc.Minus())
        self.assertTrue(calc.Minus() < calc.UnaryMinus())

    def test_compare_with_sentinel(self):
        self.assertTrue(None < calc.UnaryMinus())
        self.assertFalse(calc.UnaryMinus() < None)
        self.assertFalse(calc.Plus() < None)
        self.assertFalse(calc.Minus() < None)
        self.assertFalse(calc.Multiply() < None)
        self.assertFalse(calc.Divide() < None)

    def test_base(self):
        with self.assertRaises(NotImplementedError):
            calc.OperatorBase('', 0, operands=0).eval()


class SYEvaluatorTest(unittest.TestCase):
    def test_base(self):
        with self.assertRaises(NotImplementedError):
            calc.EvaluatorBase([]).evaluate()

    def test_evaluate_unary(self):
        self.assertEqual(1, calc.ShuntingYardEvaluator(['1']).evaluate())
        self.assertEqual(1.9, calc.ShuntingYardEvaluator(['1.9']).evaluate())
        self.assertEqual(-1, calc.ShuntingYardEvaluator(['-', '1']).evaluate())
        self.assertEqual(-1.5, calc.ShuntingYardEvaluator(['-', '1.5']).evaluate())

    def test_evaluate_binary(self):
        self.assertEqual(5, calc.ShuntingYardEvaluator(['2', '+', '3']).evaluate())
        self.assertEqual(1, calc.ShuntingYardEvaluator(['-', '2', '+', '3']).evaluate())
        self.assertEqual(6, calc.ShuntingYardEvaluator(['2', '*', '3']).evaluate())
        self.assertEqual(5, calc.ShuntingYardEvaluator(['2', '*', '3', '-', '1']).evaluate())
        self.assertEqual(-7, calc.ShuntingYardEvaluator(['2', '-', '3', '*', '3']).evaluate())

    def test_evaluate_minus_minus(self):
        self.assertEqual(9, calc.ShuntingYardEvaluator(['-', '3', '*', '(', '-', '3', ')']).evaluate())
        self.assertEqual(9, calc.ShuntingYardEvaluator(['-', '3', '*', '-', '3']).evaluate())

    def test_evaluate_par(self):
        self.assertEqual(14, calc.ShuntingYardEvaluator(['2', '*', '(', '7', ')']).evaluate())
        self.assertEqual(-3, calc.ShuntingYardEvaluator(['9', '/', '(', '-', '3', ')']).evaluate())
        self.assertEqual(-3, calc.ShuntingYardEvaluator(['9', '/', '(', '-', '3', ')']).evaluate())
        self.assertEqual(6, calc.ShuntingYardEvaluator(['2', '*', '(', '7', '-', '4', ')']).evaluate())
        self.assertEqual(1.5, calc.ShuntingYardEvaluator(['(', '7', '-', '4', ')', '/', '2']).evaluate())

    def test_assoc(self):
        self.assertEqual(6, calc.ShuntingYardEvaluator(['1', '+', '2', '+', '3', '+', '0']).evaluate())
        self.assertEqual(8, calc.ShuntingYardEvaluator(['2', '*', '2', '*', '2', '*', '1']).evaluate())
        self.assertEqual(256, calc.ShuntingYardEvaluator(['2', '^', '2', '^', '3']).evaluate())

    def test_invalid(self):
        with self.assertRaises(calc.MalformedExpressionError):
            calc.ShuntingYardEvaluator(['1', '+']).evaluate()
        with self.assertRaises(calc.MalformedExpressionError):
            calc.ShuntingYardEvaluator(['(', '6']).evaluate()
        with self.assertRaises(calc.MalformedExpressionError):
            calc.ShuntingYardEvaluator(['abc']).evaluate()


class PCEvaluatorTest(unittest.TestCase):

    def test_evaluate_unary(self):
        self.assertEqual(1, calc.PrecedenceClimbingEvaluator(['1']).evaluate())
        self.assertEqual(1.9, calc.PrecedenceClimbingEvaluator(['1.9']).evaluate())
        self.assertEqual(-1, calc.PrecedenceClimbingEvaluator(['-', '1']).evaluate())
        self.assertEqual(-1.5, calc.PrecedenceClimbingEvaluator(['-', '1.5']).evaluate())

    def test_evaluate_binary(self):
        self.assertEqual(5, calc.PrecedenceClimbingEvaluator(['2', '+', '3']).evaluate())
        self.assertEqual(1, calc.PrecedenceClimbingEvaluator(['-', '2', '+', '3']).evaluate())
        self.assertEqual(6, calc.PrecedenceClimbingEvaluator(['2', '*', '3']).evaluate())
        self.assertEqual(5, calc.PrecedenceClimbingEvaluator(['2', '*', '3', '-', '1']).evaluate())
        self.assertEqual(-7, calc.PrecedenceClimbingEvaluator(['2', '-', '3', '*', '3']).evaluate())

    def test_evaluate_minus_minus(self):
        self.assertEqual(9, calc.PrecedenceClimbingEvaluator(['-', '3', '*', '(', '-', '3', ')']).evaluate())
        self.assertEqual(9, calc.PrecedenceClimbingEvaluator(['-', '3', '*', '-', '3']).evaluate())

    def test_evaluate_par(self):
        self.assertEqual(14, calc.PrecedenceClimbingEvaluator(['2', '*', '(', '7', ')']).evaluate())
        self.assertEqual(-3, calc.PrecedenceClimbingEvaluator(['9', '/', '(', '-', '3', ')']).evaluate())
        self.assertEqual(-3, calc.PrecedenceClimbingEvaluator(['9', '/', '(', '-', '3', ')']).evaluate())
        self.assertEqual(6, calc.PrecedenceClimbingEvaluator(['2', '*', '(', '7', '-', '4', ')']).evaluate())
        self.assertEqual(1.5, calc.PrecedenceClimbingEvaluator(['(', '7', '-', '4', ')', '/', '2']).evaluate())

    def test_assoc(self):
        self.assertEqual(6, calc.PrecedenceClimbingEvaluator(['1', '+', '2', '+', '3', '+', '0']).evaluate())
        self.assertEqual(8, calc.PrecedenceClimbingEvaluator(['2', '*', '2', '*', '2', '*', '1']).evaluate())
        self.assertEqual(256, calc.PrecedenceClimbingEvaluator(['2', '^', '2', '^', '3']).evaluate())

    def test_invalid(self):
        with self.assertRaises(calc.MalformedExpressionError):
            calc.PrecedenceClimbingEvaluator(['1', '+']).evaluate()
        with self.assertRaises(calc.MalformedExpressionError):
            calc.PrecedenceClimbingEvaluator(['(', '6']).evaluate()
        with self.assertRaises(calc.MalformedExpressionError):
            calc.PrecedenceClimbingEvaluator(['abc']).evaluate()



class MainTest(unittest.TestCase):

    def test_calc_sye(self):
        self.assertEqual(4, calc.calc('2+2'))

    def test_calc_pce(self):
        self.assertEqual(4, calc.calc('2+2', calc.PrecedenceClimbingEvaluator))

if __name__ == "__main__":
    unittest.main()
