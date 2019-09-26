import argparse

# All valid chars of input expression
ACCEPTED_CHARS = {
    'digits': ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'],
    'point': ['.'],
    'op_unary': ['-'],
    'op_binary': ['+', '-', '*', '/'],
    'par': ['(', ')']
}

VALID_CHARS_SET = {ch for val_list in ACCEPTED_CHARS.values() for ch in val_list}


class InvalidTokenError(Exception):
    pass


def tokenize(expr):
    """
    Build a list of tokens (operators and operands) from an input expression string
    :param expr: Expression to tokenize, e.g. "5 + 1*4+(2+3)*4"
    :return: a list of tokens in the same order as the input e.g. ['5','+','1','*','4','+','(','2','+','3',')','*','4']
    """
    if not expr:
        return []
    delimiters = dict.copy(ACCEPTED_CHARS)  # a shallow copy is enough
    delimiters.pop('digits')
    delimiters.pop('point')
    delimiters_set = {ch for val_list in delimiters.values() for ch in val_list}
    result_list = []
    start = 0
    for index, char in enumerate(expr):
        if char in delimiters_set:
            curr_token = (expr[start:index]).strip()  # strip() to avoid pushing blank tokens
            if len(curr_token) > 0:
                result_list.extend(curr_token.split())  # split() because of possible "inner" blank spaces
                                                        # e.g "12 34" in expr. split() does the strip() also.
            result_list.append(char)  # push operator as it's a token
            start = index + 1
    if start == 0:  # no delimiter found in expr
        return expr.split()
    remainder_token = (expr[start:index+1]).strip()
    if len(remainder_token) > 0:
        result_list.extend(remainder_token.split())
    return result_list


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
    print(tokens)
