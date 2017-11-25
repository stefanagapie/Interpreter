class BCOLORS:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class AST(object):
    pass


class BinOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right

    def __str__(self):
        return 'BinOp({value})'.format(value=repr(self.token.value))

    def __repr__(self):
        return self.__str__()


class Num(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

    def __str__(self):
        return 'Num({value})'.format(value=repr(self.value))

    def __repr__(self):
        return self.__str__()


class UnaryOp(AST):
    def __init__(self, op, expr):
        self.token = self.op = op
        self.expr = expr

    def __str__(self):
        return 'UnaryOp({value})'.format(value=repr(self.token.value))

    def __repr__(self):
        return self.__str__()

# Token types
#
# EOF (end-of-file) token is used to indicate that
# there is no more input left for lexical analysis
INTEGER, PLUS, MINUS, MUL, DIV, LPAREN, RPAREN, EOF = ('INTEGER', 'PLUS', 'MINUS', 'MUL', 'DIV', '(', ')', 'EOF')


class Token(object):
    def __init__(self, type, value=None):
        # token type: INTEGER, PLUS, MINUS, MUL, DIV, or EOF
        self.type = type
        # token value: non-negative integer value, '+', '-', '*', '/', or None
        self.value = value

    def __str__(self):
        return 'Token({type},{value})'.format(type=self.type, value=repr(self.value))

    def __repr__(self):
        return self.__str__()


class Lexer(object):

    def __init__(self, text):
        # client string input, e.g. "3+5"
        self.text = text
        # self.pos is an index into self.text
        self.pos = 0
        self.current_char = self.text[self.pos]

    def error(self):
        raise Exception('Error parsing input')

    def advance(self):
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def integer(self):
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return int(result)

    def get_next_token(self):
        while self.current_char is not None:

            if self.current_char.isspace():
                self.skip_whitespace()

            elif self.current_char.isdigit():
                return Token(INTEGER, self.integer())

            elif self.current_char == "+":
                self.advance()
                return Token(PLUS, "+")

            elif self.current_char == "-":
                self.advance()
                return Token(MINUS, "-")

            elif self.current_char == "*":
                self.advance()
                return Token(MUL, "*")

            elif self.current_char == "/":
                self.advance()
                return Token(DIV, "/")

            elif self.current_char == "(":
                self.advance()
                return Token(LPAREN, "(")

            elif self.current_char == ")":
                self.advance()
                return Token(RPAREN, ")")

            else:
                self.error()

        return Token(EOF)


class Interpreter(object):

    def __init__(self, parser):
        self.parser = parser

    def run(self):
        return self.parser.expression()

    def compute_AST(self, root):

        if isinstance(root, Num):
            return root.value

        elif isinstance(root, BinOp):

            if root.token.type == PLUS:
                return self.compute_AST(root.left) + self.compute_AST(root.right)

            elif root.token.type == MINUS:
                return self.compute_AST(root.left) - self.compute_AST(root.right)

            elif root.token.type == MUL:
                return self.compute_AST(root.left) * self.compute_AST(root.right)

            elif root.token.type == DIV:
                return self.compute_AST(root.left) / self.compute_AST(root.right)

        elif isinstance(root, UnaryOp):

            if root.token.type == PLUS:
                return +self.compute_AST(root.expr)

            elif root.token.type == MINUS:
                return -self.compute_AST(root.expr)

    def showTreeHeirarchy(self, root):

        def showTree(root, level):

            padding = ""
            if level > 0:
                padding = " " * level * 4
                # padding += "\u2514"
                # padding += "\u2500\u2500"
            print(padding + root.__str__())

            if isinstance(root, BinOp):
                showTree(root.left, level + 1)
                showTree(root.right, level + 1)

            elif isinstance(root, UnaryOp):
                showTree(root.expr, level + 1)

        showTree(root, 0)


class Parser(object):
    def __init__(self, lexer):
        self.lexer = lexer
        # set current token to the first token taken from the input
        self.current_token = self.lexer.get_next_token()

    def match(self, token_type):

        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def factor(self):

        token = self.current_token

        if token.type == PLUS:
            self.match(PLUS)
            return UnaryOp(token, self.factor())

        elif token.type == MINUS:
            self.match(MINUS)
            return UnaryOp(token, self.factor())

        elif token.type == INTEGER:
            self.match(INTEGER)
            return Num(token)

        elif token.type == LPAREN:
            self.match('(')
            node = self.expression()
            self.match(')')
            return node

        else:
            self.error()

    def term(self):

        node = self.factor()

        while self.current_token.type in (MUL, DIV):
            token = self.current_token

            if token.type == MUL:
                self.match(MUL)

            elif token.type == DIV:
                self.match(DIV)

            else:
                self.error()
                break

            node = BinOp(left=node, op=token, right=self.factor())

        return node

    def expression(self):

        node = self.term()

        while self.current_token.type in (PLUS, MINUS):
            token = self.current_token

            if token.type == PLUS:
                self.match(PLUS)

            elif token.type == MINUS:
                self.match(MINUS)

            else:
                self.error()
                break

            node = BinOp(left=node, op=token, right=self.term())

        return node


def test_driver():
    program = "program"
    expected = "expected"
    programs = [
        {program: "3",  expected: "3"},
        {program: "5 +7",   expected: "12"},
        {program: "7- 5",   expected: "2"},
        {program: "5+7",    expected: "12"},
        {program: "7-5",    expected: "2"},
        {program: "5 + 7",      expected: "12"},
        {program: "7 - 5",      expected: "2"},
        {program: "27+11",      expected: "38"},
        {program: "11+22",      expected: "33"},
        {program: "27+ 11",     expected: "38"},
        {program: "11 +22",     expected: "33"},
        {program: "27 + 11",    expected: "38"},
        {program: "11 + 22",    expected: "33"},
        {program: "22 + 1",     expected: "23"},
        {program: "1 + 22",     expected: "23"},
        {program: "1 + 2 + 3",      expected: "6"},
        {program: "11 + 2 + 30",    expected: "43"},
        {program: "11 + 2 + 30 + 4",    expected: "47"},
        {program: "11 - 2 + 30 - 4",    expected: "35"},
        {program: "11-2+30-4",          expected: "35"},
        {program: "7 * 4 / 2",          expected: "14"},
        {program: "7 * 4 / 2 * 3",      expected: "42"},
        {program: "10 * 4  * 2 * 3 / 8",    expected: "30"},
        {program: "14 + 2 * 3 - 6 / 2",     expected: "17"},
        {program: "2 + 7 * 4",              expected: "30"},
        {program: "7 - 8 / 4",              expected: "5"},
        {program: "(14 + 2) * (9 - 3) / 3", expected: "32"},
        {program: "(2 + 7) * 4",            expected: "36"},
        {program: "(1 - 9) / 4",            expected: "-2"},
        {program: "7 + 3 * (10 / (12 / (3 + 1) - 1))",  expected: "22"},
        {program: "7 + (((3 + 2)))",                    expected: "12"},
        {program: "7 + 3 * (10 / (12 / (3 + 1) - 1)) / (2 + 3) - 5 - 3 + (8)", expected: "10"},
        {program: "- 3",    expected: "-3"},
        {program: "+ 3",    expected: "3"},
        {program: "- - - 5 + - 3",              expected: "-8"},
        {program: "- - - - 5 + - 3",            expected: "2"},
        {program: "5 - - - + - 3",              expected: "8"},
        {program: "5 - - - + - (3 + 4) - +2",   expected: "10"},
    ]

    failed_tests = 0
    passed_tests = 0
    print(BCOLORS.OKBLUE, "\n:: BEGIN TESTS ::\n", BCOLORS.ENDC)
    for program_pkg in programs:

        lexer = Lexer(program_pkg[program])
        parser = Parser(lexer)
        interpreter = Interpreter(parser)

        # ast = abstract syntax tree
        ast = interpreter.run()
        ast_value = int(interpreter.compute_AST(ast))

        if str(ast_value) != str(program_pkg[expected]):
            print(BCOLORS.FAIL, "Test: <Failed>", program_pkg, "Actual:",ast_value, BCOLORS.ENDC)
            failed_tests += 1
            interpreter.showTreeHeirarchy(ast)
        else:
            print(BCOLORS.OKGREEN, "Test: <Passed>", program_pkg[program], "=", ast_value, BCOLORS.ENDC)
            passed_tests += 1

    print(BCOLORS.HEADER, "\n\tSTATISTICS: Failed = "+str(failed_tests)+", Passed = "+str(passed_tests), BCOLORS.ENDC)
    print(BCOLORS.OKBLUE, "\n:: END TESTS ::", BCOLORS.ENDC)


def test_driver_2():

    lexer = Lexer("2 + 7 * 4")

    interpreter = Interpreter(lexer)

    ast = interpreter.run()

    interpreter.showTreeHeirarchy(ast)

    ast_value = interpreter.compute_AST(ast)

    print(ast_value)

def main():

    test_driver()
    return

    # test_driver_2()
    # return

    while True:
        try:
            terminal = input('uNiCoRn> ')
        except EOFError:
            break
        if not terminal:
            print("Accpeted Format:[0..9][+,-][0..9]")
            continue

        lexer = Lexer(terminal)
        interpreter = Interpreter(lexer)
        result = interpreter.run()
        print(result)

if __name__ == '__main__':
    main()

# Machine = Interpreter("3+6")
#
# print(Machine.get_next_token())
