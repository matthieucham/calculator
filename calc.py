from __future__ import division
import argparse
from functools import total_ordering


@total_ordering
class OperatorBase(object):
    def __init__(self, token, precedence, operands=2, associativity='left'):
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
        assert len(args) == self.operands, "Bad number of operands for operator %s: expected %d, got %d" % (
            self, self.operands, len(args))
        return self.do_eval(*args)

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
            # return False
        # self is binary
        if other.is_binary():
            if other.precedence > self.precedence:
                return True
            if other.precedence == self.precedence and other.is_left_assoc():
                return True
            return False
        if other.is_unary():
            # return other.precedence >= self.precedence
            return True

    def do_eval(self, *args):
        """ Override this in Operator subclasses"""
        raise NotImplementedError()


class Plus(OperatorBase):
    def __init__(self):
        super(Plus, self).__init__('+', 3)

    def do_eval(self, *args):
        return args[0] + args[1]


class Minus(OperatorBase):
    def __init__(self):
        super(Minus, self).__init__('-', 3)

    def do_eval(self, *args):
        return args[0] - args[1]


class Multiply(OperatorBase):
    def __init__(self):
        super(Multiply, self).__init__('*', 5)

    def do_eval(self, *args):
        return args[0] * args[1]


class Divide(OperatorBase):
    def __init__(self):
        super(Divide, self).__init__('/', 5)

    def do_eval(self, *args):
        return args[0] / args[1]


class Pow(OperatorBase):
    def __init__(self):
        super(Pow, self).__init__('^', 6, associativity='right')

    def do_eval(self, *args):
        return args[0] ** args[1]


class UnaryMinus(OperatorBase):
    def __init__(self):
        super(UnaryMinus, self).__init__('-', 4, operands=1)

    def do_eval(self, *args):
        return args[0] * (-1)


OPERATORS = [
    Plus(), Minus(), Multiply(), Divide(), UnaryMinus(), Pow()
]

BINARY_OPS = {op.token: op for op in OPERATORS if op.is_binary()}
UNARY_OPS = {op.token: op for op in OPERATORS if op.is_unary()}

VALID_TOKENS_SET = {op.token for op in OPERATORS}
VALID_TOKENS_SET.add('(')
VALID_TOKENS_SET.add(')')


class InvalidTokenError(Exception):
    pass


class InvalidExpressionError(Exception):
    pass


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
    if is_value(token) or token in VALID_TOKENS_SET:
        return token
    raise InvalidTokenError(token)


class Recognizer(object):
    """
    Implementation of  Recursive-descent recognition algorithm from http://www.engr.mun.ca/~theo/Misc/exp_parsing.htm
    """

    def __init__(self, tokexpr):
        assert tokexpr is not None, "Expression to recognize cannot be None, should at least be []"
        self.tokens = tokexpr
        self.cursor = 0

    def _next(self):
        if self.cursor < len(self.tokens):
            return self.tokens[self.cursor]
        return None  # all tokens consumed

    def _consume(self):
        self.cursor += 1  # move cursor up

    def _error(self, msg=None):
        raise InvalidExpressionError(msg)

    def _expect(self, token):
        try:
            assert self._next() == token
            self._consume()
        except AssertionError:
            self._error("Expected %s, got %s" % (token, self._next()))

    def recognize(self):
        self._e()
        self._expect(None)

    def _e(self):
        self._p()
        while self._next() in BINARY_OPS:
            self._consume()
            self._p()

    def _p(self):
        if is_value(self._next()):
            self._consume()
        elif self._next() == '(':
            self._consume()
            self._e()
            self._expect(')')
        elif self._next() in UNARY_OPS:
            self._consume()
            self._p()
        else:
            self._error()


class EvaluatorBase(object):
    """
    Implementation of  Recursive-descent recognition algorithm from http://www.engr.mun.ca/~theo/Misc/exp_parsing.htm
    """

    def __init__(self, tokexpr):
        assert tokexpr is not None, "Expression to recognize cannot be None, should at least be []"
        self.tokens = tokexpr
        self.cursor = 0

    def _next(self):
        if self.cursor < len(self.tokens):
            return self.tokens[self.cursor]
        return None  # all tokens consumed

    def _consume(self):
        self.cursor += 1  # move cursor up

    def _error(self, msg=None):
        raise InvalidExpressionError(msg)

    def _expect(self, token):
        try:
            assert self._next() == token
            self._consume()
        except AssertionError:
            self._error("Expected %s, got %s" % (token, self._next()))

    @staticmethod
    def _binary(token):
        return BINARY_OPS.get(token)

    @staticmethod
    def _unary(token):
        return UNARY_OPS.get(token)

    def _mkleaf(self, token):
        try:
            return int(token)
        except ValueError:
            try:
                return float(token)
            except ValueError:
                self._error("'%s' cannot be cast to a number" % token)

    def _mknode(self, operator, *args):
        return operator.eval(*args)

    def evaluate(self):
        raise NotImplementedError()


class ShuntingYardEvaluator(EvaluatorBase):
    """
    Shunting yard algo implementation adapted from http://www.engr.mun.ca/~theo/Misc/exp_parsing.htm
    "The shunting yard algorithm"
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
            operands.append(self._mkleaf(self._next()))
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
            operands.append(self._mknode(operators.pop(), first, second))
        else:  # unary
            operands.append(self._mknode(operators.pop(), operands.pop()))

    def _pushoperator(self, op, operators, operands):
        while operators[-1] > op:
            self._popoperator(operators, operands)
        operators.append(op)


def calc(expr):
    tokens = tokenize(expr)
    for t in tokens:
        validate_token(t)
    return ShuntingYardEvaluator(tokens).evaluate()


if __name__ == "__main__":  # pragma: no cover
    parser = argparse.ArgumentParser(
        prefix_chars='$',  # redefine prefix_chars because the default "-" is a valid operand
        description="A simple calculator for infixed mathematical expressions")
    parser.add_argument('expression', nargs='+', help="Expression to evaluate")
    expression = ''.join(parser.parse_args().expression)
    result = calc()
    print(result)
