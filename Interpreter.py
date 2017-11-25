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
    def __repr__(self):
        return self.__str__()


class NoOp(AST):
    pass


class Program(AST):
    def __init__(self):
        self.assignments = []

    def __str__(self):
        return 'Program({value})'.format(value=repr(len(self.assignments)))

    def addStatement(self, stmt):
        self.assignments.append(stmt)

    def statementAtIndex(self, index):
        stmt = None
        if index < len(self.assignments):
            stmt = self.assignments[index]
        return stmt


class Id(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

    def __str__(self):
        return 'Id({value})'.format(value=repr(self.token.value))


class Num(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

    def __str__(self):
        return 'Num({value})'.format(value=repr(self.value))


class Assign(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right

    def __str__(self):
        return 'Assign({value})'.format(value=repr(self.token.value))


class BinOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right

    def __str__(self):
        return 'BinOp({value})'.format(value=repr(self.token.value))


class UnaryOp(AST):
    def __init__(self, op, expr):
        self.token = self.op = op
        self.expr = expr

    def __str__(self):
        return 'UnaryOp({value})'.format(value=repr(self.token.value))


# Token types
#
# EOF (end-of-file) token is used to indicate that
# there is no more input left for lexical analysis
INTEGER, ID, ASSIGN, PLUS, MINUS, MUL, DIV, LPAREN, RPAREN, SEMI, EOF = \
    ('INTEGER', 'ID', 'ASSIGN', 'PLUS', 'MINUS', 'MUL', 'DIV', '(', ')', 'SEMI', 'EOF')


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

    def identifier(self):
        """Handle identifiers and reserved keywords"""
        result = ''
        while self.current_char is not None and self.current_char.isalnum():
            result += self.current_char
            self.advance()
        return result

    def get_next_token(self):
        while self.current_char is not None:

            if self.current_char.isspace():
                self.skip_whitespace()

            elif self.current_char.isdigit():
                return Token(INTEGER, self.integer())

            elif self.current_char.isalnum():
                return Token(ID, self.identifier())

            elif self.current_char == "=":
                self.advance()
                return Token(ASSIGN, "=")

            elif self.current_char == ";":
                self.advance()
                return Token(SEMI, ";")

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


class Parser(object):
    def __init__(self, lexer):
        self.lexer = lexer
        # set current token to the first token taken from the input
        self.current_token = self.lexer.get_next_token()

    def match(self, token_type):

        token = self.current_token
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
            return token
        else:
            self.error()

    def error(self):
        raise Exception('Error parsing input')

    def program(self):

        program = Program()

        while self.current_token.type != EOF:
            program.addStatement(self.statement())

        return program

    def statement(self):

        left_node = self.identifier()
        assign_token = self.match(ASSIGN)
        right_node = self.expression()
        self.match(SEMI)

        return Assign(left_node, assign_token, right_node)

    def identifier(self):

        token = self.match(ID)
        node = Id(token)

        return node

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

        elif token.type == ID:
            return self.identifier()

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


class Interpreter(object):

    def __init__(self, parser):
        self.parser = parser
        self.symbol_table = {}

    def run(self):
        return self.parser.program()

    def evaluate_program(self, root):

        if isinstance(root, Program):
            for assignment in root.assignments:
                self.evaluate_program(assignment)

        if isinstance(root, Assign):
            variable_name = root.left.value
            self.symbol_table[variable_name] = int(self.compute_AST(root.right))

    def compute_AST(self, root):

        if isinstance(root, Id):
            variable_name = root.value
            identifier_value = self.symbol_table.get(variable_name)
            if identifier_value is None:
                raise NameError(repr(variable_name))
            else:
                return identifier_value

        elif isinstance(root, Num):
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

    def stringed_output(self):

        output = ""
        for (key, value) in self.symbol_table.items():
            output += "{key} = {value}, ".format(key=key, value=value)
        output = output[:-2]
        return output

    def normal_output(self):
        output = ""
        for (key, value) in self.symbol_table.items():
            output += "{key} = {value}\n".format(key=key, value=value)
        output = output[:-1]
        return output

    def showTreeHeirarchy(self, root):

        def showTree(root, level):

            padding = ""
            if level > 0:
                padding = " " * level * 4
                # padding += "\u2514"
                # padding += "\u2500\u2500"
            print(padding + root.__str__())

            if isinstance(root, Program):
                for assignment in root.assignments:
                    showTree(assignment, level + 1)

            if isinstance(root, BinOp):
                showTree(root.left, level + 1)
                showTree(root.right, level + 1)

            if isinstance(root, Assign):
                showTree(root.left, level + 1)
                showTree(root.right, level + 1)

            elif isinstance(root, UnaryOp):
                showTree(root.expr, level + 1)

        showTree(root, 0)


def test_driver():
    program = "program"
    expected = "expected"
    programs = [
        {program: "eval = 3;",  expected: "eval = 3"},
        {program: "eval = 5 +7;",   expected: "eval = 12"},
        {program: "eval = 7- 5;",   expected: "eval = 2"},
        {program: "eval = 5+7;",    expected: "eval = 12"},
        {program: "eval = 7-5;",    expected: "eval = 2"},
        {program: "eval = 5 + 7;",      expected: "eval = 12"},
        {program: "eval = 7 - 5;",      expected: "eval = 2"},
        {program: "eval = 27+11;",      expected: "eval = 38"},
        {program: "eval = 11+22;",      expected: "eval = 33"},
        {program: "eval = 27+ 11;",     expected: "eval = 38"},
        {program: "eval = 11 +22;",     expected: "eval = 33"},
        {program: "eval = 27 + 11;",    expected: "eval = 38"},
        {program: "eval = 11 + 22;",    expected: "eval = 33"},
        {program: "eval = 22 + 1;",     expected: "eval = 23"},
        {program: "eval = 1 + 22;",     expected: "eval = 23"},
        {program: "eval = 1 + 2 + 3;",      expected: "eval = 6"},
        {program: "eval = 11 + 2 + 30;",    expected: "eval = 43"},
        {program: "eval = 11 + 2 + 30 + 4;",    expected: "eval = 47"},
        {program: "eval = 11 - 2 + 30 - 4;",    expected: "eval = 35"},
        {program: "eval = 11-2+30-4;",          expected: "eval = 35"},
        {program: "eval = 7 * 4 / 2;",          expected: "eval = 14"},
        {program: "eval = 7 * 4 / 2 * 3;",      expected: "eval = 42"},
        {program: "eval = 10 * 4  * 2 * 3 / 8;",    expected: "eval = 30"},
        {program: "eval = 14 + 2 * 3 - 6 / 2;",     expected: "eval = 17"},
        {program: "eval = 2 + 7 * 4;",              expected: "eval = 30"},
        {program: "eval = 7 - 8 / 4;",              expected: "eval = 5"},
        {program: "eval = (14 + 2) * (9 - 3) / 3;", expected: "eval = 32"},
        {program: "eval = (2 + 7) * 4;",            expected: "eval = 36"},
        {program: "eval = (1 - 9) / 4;",            expected: "eval = -2"},
        {program: "eval = 7 + 3 * (10 / (12 / (3 + 1) - 1));",  expected: "eval = 22"},
        {program: "eval = 7 + (((3 + 2)));",                    expected: "eval = 12"},
        {program: "eval = 7 + 3 * (10 / (12 / (3 + 1) - 1)) / (2 + 3) - 5 - 3 + (8);", expected: "eval = 10"},
        {program: "eval = - 3;",    expected: "eval = -3"},
        {program: "eval = + 3;",    expected: "eval = 3"},
        {program: "eval = - - - 5 + - 3;",              expected: "eval = -8"},
        {program: "eval = - - - - 5 + - 3;",            expected: "eval = 2"},
        {program: "eval = 5 - - - + - 3;",              expected: "eval = 8"},
        {program: "eval = 5 - - - + - (3 + 4) - +2;",   expected: "eval = 10"},
    ]

    failed_tests = 0
    passed_tests = 0
    print(BCOLORS.OKBLUE, "\n:: BEGIN TESTS ::\n", BCOLORS.ENDC)
    for program_pkg in programs:

        lexer = Lexer(program_pkg[program])
        parser = Parser(lexer)
        interpreter = Interpreter(parser)

        prog = interpreter.run()
        interpreter.evaluate_program(prog)

        output = interpreter.stringed_output()
        if str(output) != str(program_pkg[expected]):
            print(BCOLORS.FAIL, "Test: <Failed> Input:", program_pkg, "Actual:", output, BCOLORS.ENDC)
            failed_tests += 1
            interpreter.showTreeHeirarchy(program)
        else:
            print(BCOLORS.OKGREEN, "Test: <Passed> Input:", program_pkg[program], "Output:", output, BCOLORS.ENDC)
            passed_tests += 1

    print(BCOLORS.HEADER, "\n\tSTATISTICS: Failed = "+str(failed_tests)+", Passed = "+str(passed_tests), BCOLORS.ENDC)
    print(BCOLORS.OKBLUE, "\n:: END TESTS ::", BCOLORS.ENDC)


def test_driver_2():

    lexer = Lexer("rate = 4 + 5; kite = 5; flight = rate + kite;")

    parser = Parser(lexer)

    interpreter = Interpreter(parser)

    program = interpreter.run()

    interpreter.showTreeHeirarchy(program)

    interpreter.evaluate_program(program)

    print(interpreter.stringed_output())

    print(interpreter.normal_output())
    # print(interpreter.symbol_table)


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
