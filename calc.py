#!/usr/bin/env python
"""
    Calculator
    ==========

    Calculator for infixed mathematical expressions.

    :Example:
    >>> calc("2+2")
    4

    Evaluators algorithms taken from Theodore Norvell article: "Parsing Expressions by Recursive Descent"
    http///www.engr.mun.ca/~theo/Misc/exp_parsing.htm
"""
from __future__ import division
import argparse
from functools import total_ordering

__author__ = "Matthieu Grandrie"
__copyright__ = "Copyright 2019, Matthieu Grandrie"
__credits__ = ["Matthieu Grandrie", "Theodore Norvell"]
__date__ = "2019-09-28"
__maintainer__ = "Matthieu Grandrie"
__status__ = "Production"
__version__ = "1.0"


##################################
###           OPERATORS        ###
##################################
@total_ordering
class OperatorBase(object):
    """
    Operators hierarchy base class
    """

    def __init__(self, token, precedence, operands=2, associativity='left'):
        """
        Constructor
        :param token: operator token in mathematical expressions, eg '+' for Add
        :param precedence: operator relative precedence
        :param operands:  number of operands of this operator (1 : unary, 2: binary)
        :param associativity: associativity side : 'left' or 'right'
        """
        self.token = token
        self.precedence = precedence
        self.operands = operands
        self.associativy = associativity

    def is_unary(self):
        return self.operands == 1

    def is_binary(self):
        return self.operands == 2

    def is_left_assoc(self):
        return self.associativy == 'left'

    def is_right_assoc(self):
        return self.associativy == 'right'

    def eval(self, *args):
        """
        Check operands number and evaluate this operator applied to these operands
        :param args: operands
        :return: operation's result
        """
        assert len(args) == self.operands, "Bad number of operands for operator %s: expected %d, got %d" % (
            self, self.operands, len(args))
        return self.do_eval(*args)

    # Ordering of operators as defined here http://www.engr.mun.ca/~theo/Misc/exp_parsing.htm
    # This ordering is used by the Shunting Yard algorithm
    # __eq__, __ne__ and __lt__ are the 3 required methods for custom ordering definition to be compatible with Python 2
    # and Python 3
    def __eq__(self, other):
        if other is None:
            return False
        return self.precedence == other.precedence

    def __ne__(self, other):  # for python2 compatibility
        return not self == other

    def __lt__(self, other):
        if other is None:  # None act as "sentinel"
            return False
        if self.is_unary():
            return other.precedence >= self.precedence
        # from here, self is binary
        if other.is_binary():
            if other.precedence > self.precedence:
                return True
            if other.precedence == self.precedence and other.is_left_assoc():
                return True
            return False
        if other.is_unary():
            return True

    def do_eval(self, *args):
        """ Override this in Operator subclasses"""
        raise NotImplementedError()


class Plus(OperatorBase):
    """Addition"""

    def __init__(self):
        super(Plus, self).__init__('+', 3)

    def do_eval(self, *args):
        return args[0] + args[1]


class Minus(OperatorBase):
    """Subtraction"""

    def __init__(self):
        super(Minus, self).__init__('-', 3)

    def do_eval(self, *args):
        return args[0] - args[1]


class Multiply(OperatorBase):
    """Multiplication"""

    def __init__(self):
        super(Multiply, self).__init__('*', 5)

    def do_eval(self, *args):
        return args[0] * args[1]


class Divide(OperatorBase):
    """Division"""

    def __init__(self):
        super(Divide, self).__init__('/', 5)

    def do_eval(self, *args):
        return args[0] / args[1]


class Pow(OperatorBase):
    """Power elevation"""

    def __init__(self):
        super(Pow, self).__init__('^', 6, associativity='right')

    def do_eval(self, *args):
        return args[0] ** args[1]


class UnaryMinus(OperatorBase):
    """Minus sign, unary operator"""

    def __init__(self):
        super(UnaryMinus, self).__init__('-', 4, operands=1)

    def do_eval(self, *args):
        return args[0] * (-1)


##################################
###    CALC IMPLEMENTATION     ###
##################################

# Recognized operators
OPERATORS = [
    Plus(), Minus(), Multiply(), Divide(), UnaryMinus(), Pow()
]
# Organized in dicts
BINARY_OPS = {op.token: op for op in OPERATORS if op.is_binary()}
UNARY_OPS = {op.token: op for op in OPERATORS if op.is_unary()}

# Tokens delimiters are operators'tokens and parenthesis
VALID_TOKENS_SET = {op.token for op in OPERATORS}
VALID_TOKENS_SET.add('(')
VALID_TOKENS_SET.add(')')


class InvalidTokenError(Exception):
    """Exception raised in case of bad input"""
    pass


class MalformedExpressionError(Exception):
    """Exception raised in case of malformed expression"""
    pass


def remove_quotes(expr):
    """If single or double quotes in expression, remove them"""
    return expr.replace('\'', '').replace('\"', '')


def tokenize(expr):
    """
    Build a list of tokens (operators and operands) from an input expression string
    :param expr: Expression to tokenize, e.g. "5 + 1*4+(2+3)*4"
    :return: a list of tokens in the same order as the input e.g. ['5','+','1','*','4','+','(','2','+','3',')','*','4']
    """
    if not expr:
        return []
    result_list = []
    start = 0
    for index, char in enumerate(expr):
        if char in VALID_TOKENS_SET:
            curr_token = (expr[start:index]).strip()  # strip() to avoid pushing blank tokens
            if len(curr_token) > 0:
                result_list.extend(curr_token.split())  # split() because of possible "inner" blank spaces
                # e.g "12 34" in expr. split() does the strip() also.
            result_list.append(char)  # push operator as it's a token
            start = index + 1
    if start == 0:  # no delimiter found in expr
        return expr.split()
    remainder_token = (expr[start:index + 1]).strip()
    if len(remainder_token) > 0:
        result_list.extend(remainder_token.split())
    return result_list


def is_value(token):
    """
    check if a token is a value, ie a stringified number
    :param token: token to test
    :return: True if value, false otherwise
    """
    if token is None:
        return False
    try:
        float(token)
        return True
    except ValueError:
        return False


def validate_token(token):
    """
    Check if token is valid. Valid token are stringified numbers, operators'tokens and parenthesis
    :param token: token to check
    :return: the same token if valid
    :raise: InvalidTokenError if not valid
    """
    if is_value(token) or token in VALID_TOKENS_SET:
        return token
    raise InvalidTokenError(token)


class EvaluatorBase(object):
    """
    Base class of evaluator algorithms.

    Defines common methods of both algorithms from http://www.engr.mun.ca/~theo/Misc/exp_parsing.htm
    Theses methods have the same name as in this article.
    - _next
    - _consume
    - _error
    - _expect
    - _binary
    - _unary
    - _eval_leaf
    - _eval_node
    Methods docstring are taken from the article.
    """

    def __init__(self, tokexpr):
        """
        Builder
        :param tokexpr: Tokenize expression to be evaluated
        """
        assert tokexpr is not None, "Expression to recognize cannot be None, should at least be []"
        self.tokens = tokexpr
        self.cursor = 0

    def _next(self):
        """
        :return: the next token of input or None to represent that there are no more input tokens. \
        Does not alter the input tokens.
        """
        if self.cursor < len(self.tokens):
            return self.tokens[self.cursor]
        return None  # all tokens consumed

    def _consume(self):
        """
        Consume one token. When "_next() == None", _consume is still allowed, but has no effect.
        :return: None
        """
        self.cursor += 1  # move cursor up

    def _error(self, msg=None):
        """
        Stops the parsing process and reports an error.
        """
        raise MalformedExpressionError(msg)

    def _expect(self, token):
        """
        Check if _next() is expected. Call _error if not.
        :param token: Expected token
        :return: None
        """
        try:
            assert self._next() == token
            self._consume()
        except AssertionError:
            self._error("Expected %s, got %s" % (token, self._next()))

    @staticmethod
    def _binary(token):
        """
        converts a binary operator's token to its operator
        """
        return BINARY_OPS.get(token)

    @staticmethod
    def _unary(token):
        """
        converts an unary operator's token to its operator
        """
        return UNARY_OPS.get(token)

    def _eval_leaf(self, token):
        """
        Convert a "value" token to its numerical value. Call _error() if casting fails
        :param token: stringified value
        :return: int or float depending on the token
        """
        try:
            return int(token)
        except ValueError:
            try:
                return float(token)
            except ValueError:
                self._error("'%s' cannot be cast to a number" % token)

    def _eval_node(self, operator, *args):
        """
        Compute the operation (operator, operands)
        :param operator: operator
        :param args: operands
        :return: result
        """
        return operator.eval(*args)

    def evaluate(self):
        """Override in subclasses"""
        raise NotImplementedError()


class ShuntingYardEvaluator(EvaluatorBase):
    """
    "The shunting yard algorithm" implementation, See article.
    Article's methods name are kept:
    - Eparser => evaluate
    - E => _e
    - P => _p
    - popOperator => _popoperator
    - pushOperator => _pushoperator
    """

    def evaluate(self):
        operators = []
        operands = []
        operators.append(None)
        self._e(operators, operands)
        self._expect(None)
        return operands[-1]

    def _e(self, operators, operands):
        self._p(operators, operands)
        while self._next() in BINARY_OPS:
            self._pushoperator(self._binary(self._next()), operators, operands)
            self._consume()
            self._p(operators, operands)
        while operators[-1] is not None:
            self._popoperator(operators, operands)

    def _p(self, operators, operands):
        if self._next() and self._next() not in VALID_TOKENS_SET:
            operands.append(self._eval_leaf(self._next()))
            self._consume()
        elif self._next() == '(':
            self._consume()
            operators.append(None)
            self._e(operators, operands)
            self._expect(')')
            operators.pop()
        elif self._next() in UNARY_OPS:
            self._pushoperator(self._unary(self._next()), operators, operands)
            self._consume()
            self._p(operators, operands)
        else:
            self._error()

    def _popoperator(self, operators, operands):
        if operators[-1] is not None and operators[-1].is_binary():
            second = operands.pop()
            first = operands.pop()
            operands.append(self._eval_node(operators.pop(), first, second))
        else:  # unary
            operands.append(self._eval_node(operators.pop(), operands.pop()))

    def _pushoperator(self, op, operators, operands):
        while operators[-1] > op:
            self._popoperator(operators, operands)
        operators.append(op)


class PrecedenceClimbingEvaluator(EvaluatorBase):
    """
    "Precedence climbing" implementation, See article.
    Article's methods name are kept:
    - Eparser => evaluate
    - Exp => _exp
    - P => _p
    """

    def evaluate(self):
        val = self._exp(0)
        self._expect(None)
        return val

    def _exp(self, precedence):
        t = self._p()
        while self._next() in BINARY_OPS and EvaluatorBase._binary(self._next()).precedence >= precedence:
            op = EvaluatorBase._binary(self._next())
            self._consume()
            if op.is_right_assoc():
                q = op.precedence
            else:
                q = op.precedence + 1
            t1 = self._exp(q)
            t = self._eval_node(op, t, t1)
        return t

    def _p(self):
        if self._next() in UNARY_OPS:
            op = EvaluatorBase._unary(self._next())
            self._consume()
            q = op.precedence
            t = self._exp(q)
            return self._eval_node(op, t)
        elif self._next() == '(':
            self._consume()
            t = self._exp(0)
            self._expect(')')
            return t
        elif self._next() and self._next() not in VALID_TOKENS_SET:
            t = self._eval_leaf(self._next())
            self._consume()
            return t
        else:
            self._error()


def calc(expr, evaluator_class=PrecedenceClimbingEvaluator):
    """
    Do the whole work
    :param expr: String expression
    :param evaluator_class: class name of the evaluator to use for computation
    :return: Evaluation result
    """
    tokens = tokenize(remove_quotes(expr))
    for t in tokens:
        validate_token(t)
    return evaluator_class(tokens).evaluate()


if __name__ == "__main__":  # pragma: no cover
    parser = argparse.ArgumentParser(
        description="A simple calculator for infixed mathematical expressions. Supports operators +-/*^")
    parser.add_argument('expression', nargs='+', help="Expression to evaluate")
    parser.add_argument('-a', '--algo',
                        help="Choose evaluator algorithm: pc for Precedence Climbing (default) or sh for Shunting Yard",
                        choices=['pc', 'sh'], default='pc')
    expression = ''.join(parser.parse_args().expression)
    if parser.parse_args().algo == 'sh':
        res = calc(expression, ShuntingYardEvaluator)
    else:
        res = calc(expression)
    print(res)
