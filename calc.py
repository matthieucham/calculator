import argparse


class OperatorBase(object):

    def __init__(self, token, precedence, operands=2, associativity='left'):
        self.token = token
        self.precedence = precedence
        self.operands = operands
        self.associativy = associativity

    def __str__(self):
        return "%s%d" % (self.token, self.operands)

    def get_token(self):
        return self.token

    def get_precedence(self):
        return self.precedence

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
        self.do_eval(*args)

    def do_eval(self, *args):
        """ Override this in Operator subclasses"""
        raise NotImplementedError()


class Plus(OperatorBase):

    def __init__(self):
        super(Plus, self).__init__('+', 1)

    def do_eval(self, *args):
        return args[0] + args[1]


class Minus(OperatorBase):

    def __init__(self):
        super(Minus, self).__init__('-', 1)

    def do_eval(self, *args):
        return args[0] - args[1]


class Multiply(OperatorBase):

    def __init__(self):
        super(Multiply, self).__init__('*', 3)

    def do_eval(self, *args):
        return args[0] * args[1]


class Divide(OperatorBase):

    def __init__(self):
        super(Divide, self).__init__('/', 3)

    def do_eval(self, *args):
        return args[0] / args[1]


class UnaryMinus(OperatorBase):

    def __init__(self):
        super(UnaryMinus, self).__init__('-', 2, 1)

    def do_eval(self, *args):
        return args[0] * (-1)


OPERATORS = [
    Plus(), Minus(), Multiply(), Divide(), UnaryMinus()
]

BINARY_OPS = [op.get_token() for op in OPERATORS if op.is_binary()]
UNARY_OPS = [op.get_token() for op in OPERATORS if op.is_unary()]

VALID_TOKENS_SET = {op.get_token() for op in OPERATORS}
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


class ConcatArgs(argparse.Action):
    """
    Concatenate args input into one string
    """

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, ''.join(values))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prefix_chars='$',  # redefine prefix_chars because the default "-" is a valid operand
        description="A simple calculator for infixed mathematical expressions")
    parser.add_argument('expression', nargs='+', help="Expression to evaluate", action=ConcatArgs)
    expression = parser.parse_args().expression

    tokens = tokenize(expression)
    for t in tokens:
        validate_token(t)
    Recognizer(tokens).recognize()
