# # # # # # # # # # # # # # # # # # #
# Stefan Agapie                     #
# Final Project -- Toy Interpreter  #
# # # # # # # # # # # # # # # # # # #
import re

# Defines colors that may be used for pretty print output.
class BCOLORS:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# Defines Syntax Error Interpreter Exception
class InterpreterSyntaxError(Exception):
    def __init__(self):
        Exception.__init__(self,"Syntax Error.")


# Defines Uninitialized Variable Interpreter Exception
class InterpreterUninitializedVariableError(Exception):
    def __init__(self, dErrorArguments):
        Exception.__init__(self,"{0} is undefined.".format(dErrorArguments))
        self.dErrorArguments = dErrorArguments


# The base class of an Abstract Syntax Tree (AST)
class AST(object):
    def __repr__(self):
        return self.__str__()


# The AST root class is the input program that is
# defined as a collection of assignments or statements.
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


# The AST variable that corresponds to some variable
# in a program statement, is defined by a token that is
# extracted by the lexical analyzer from some program.
class Id(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

    def __str__(self):
        return 'Id({value})'.format(value=repr(self.token.value))


# The AST number that corresponds to some number in
# a program statement, is defined by a token that is extracted
# by the lexical analyzer from some program.
class Num(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

    def __str__(self):
        return 'Num({value})'.format(value=repr(self.value))


# The AST assignment operator that corresponds to some assignment
# operator in a program statement, is defined by a variable to the
# left of the assignment operator, followed by the assignment token
# that is extracted by the lexical analyzer from some program,
# followed by some expression that is to the right of the assignment
# operator. Note that the left and right properties are AST objects.
class Assign(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right

    def __str__(self):
        return 'Assign({value})'.format(value=repr(self.token.value))


# An AST binary operator that corresponds to some binary operator in
# a program statement, is defined by an operand to the left of the
# binary operator, followed by the operator token that is extracted
# by the lexical analyzer from some program, followed by some operand
# that is to the right of the binary operator. Note that the left and
# right properties are AST objects.
class BinOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right

    def __str__(self):
        return 'BinOp({value})'.format(value=repr(self.token.value))


# An AST unary operator that corresponds to some unary operator in a
# program statement, is defined by the operator token that is extracted
# by the lexical analyzer from some program, followed by some operand
# that is to the right of unary operator, that is labeled as 'expr'
# (expression). Note that the expr property is an AST objects.
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
    ('INTEGER', 'ID', 'ASSIGN', 'PLUS', 'MINUS', 'MUL', 'DIV', 'LPAREN', 'RPAREN', 'SEMI', 'EOF')


# The token that contains a single lexeme extracted from a given program,
# is defined as a type from a finite domain of types, a value, along with
# the its line and starting column position within a given program.
class Token(object):
    def __init__(self, type, value=None, line=None, column=None):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    def __str__(self):
        return 'Token({type},{value})'.format(type=self.type, value=repr(self.value))

    def __repr__(self):
        return self.__str__()


# This is the Lexical Analyzer.
# The job of the lexer is to generate tokens from a given
# program as defined by the Toy Grammar (see below).
class Lexer(object):
    def __init__(self):
        self.current_token_index = None
        self.tokens = []
        self.token_specification = [
            ('INTEGER', r'([0]|[1-9]\d*)'),                 # Integer or decimal number
            ('ASSIGN',  r'='),                              # Assignment operator
            ('SEMI',    r';'),                              # Statement terminator
            ('LPAREN',  r'\('),                             # Open Parenthesis
            ('RPAREN',  r'\)'),                             # Close Parenthesis
            ('ID',      r'[A-Za-z]([0-9]|[A-Za-z]|\_)*'),   # Identifier
            ('PLUS',    r'[+]'),                            # Arithmetic operators
            ('MINUS',   r'[\-]'),                           # Arithmetic operators
            ('MUL',     r'[*]'),                            # Arithmetic operators
            ('DIV',     r'[\/]'),                           # Arithmetic operators
            ('NEWLINE', r'\n'),                             # Line endings
            ('SKIP',    r'[ \t]'),                          # Skip over spaces and tabs
        ]
        self.tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in self.token_specification)
        self.get_token = re.compile(self.tok_regex).match

    # Resets this lexer's state to its initial state.
    def reset(self):
        self.current_token_index = None
        self.tokens = []

    # Given an entire program, it is scanned from end to end and tokens
    # are generated from each discovered lexeme. Note that piecewise program
    # inputs are not supported since on each call of this method the lexer's
    # internal state is reset to its initial state.
    #
    # To access the generated tokens call get_next_token().
    def scanner_input(self, input_program):

        self.reset()
        pos = 0
        line = 1
        line_start = 0

        mo = self.get_token(input_program)
        while mo is not None:
            type = mo.lastgroup
            if type == 'NEWLINE':
                line_start = pos
                line += 1
            elif type != 'SKIP':
                val = mo.group(type)
                self.tokens.append(Token(type, val, line, mo.start() - line_start))

            pos = mo.end()
            mo = self.get_token(input_program, pos)
        if pos != len(input_program):
            self._error()

        if len(self.tokens) > 0:
            self.current_token_index = 0

    def _error(self):
        raise InterpreterSyntaxError()

    # Returns the next available token from a previously scanned program.
    # Once all the tokens of a program have been requested a End of File
    # token is returned on subsequent calls.
    def get_next_token(self):

        while self.current_token_index is not None and self.current_token_index < len(self.tokens):

            token = self.tokens[self.current_token_index]
            self.current_token_index += 1
            return token

        return Token(EOF)


# This is the Syntax Analyzer.
# The job of the parser to build an in memory Parser Tree, via recursive
# calls, that checks for syntax error and build an Abstract Syntax Tree
# (AST) as the Parser Tree frontier is expanded.
class Parser(object):
    def __init__(self, lexer):
        self.lexer = lexer
        # set current token to the first token taken from the input
        self.current_token = self.lexer.get_next_token()

    # Resets this parser's state to its initial state.
    def reset(self):
        self.current_token = self.lexer.get_next_token()

    # Initiates a series of call procedures as defined by the Toy Grammar
    # that results in the generation of an in memory Parser Tree and the
    # creation of an Abstract Syntax Tree that is returned.
    def program(self):

        program = Program()

        while self.current_token.type != EOF:
            program.addStatement(self._statement())

        return program

    def _error_syntax(self):
        raise InterpreterSyntaxError()

    def _match(self, token_type):

        token = self.current_token
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
            return token
        else:
            self._error_syntax()

    def _statement(self):

        left_node = self._identifier()
        assign_token = self._match(ASSIGN)
        right_node = self._expression()
        self._match(SEMI)

        return Assign(left_node, assign_token, right_node)

    def _identifier(self):

        token = self._match(ID)
        node = Id(token)

        return node

    def _factor(self):

        token = self.current_token

        if token.type == PLUS:
            self._match(PLUS)
            return UnaryOp(token, self._factor())

        elif token.type == MINUS:
            self._match(MINUS)
            return UnaryOp(token, self._factor())

        elif token.type == INTEGER:
            self._match(INTEGER)
            return Num(token)

        elif token.type == LPAREN:
            self._match(LPAREN)
            node = self._expression()
            self._match(RPAREN)
            return node

        elif token.type == ID:
            return self._identifier()

        else:
            self._error_syntax()

    def _term(self):

        node = self._factor()
        node = self._term_prime(node)

        return node

    def _term_prime(self, node):

        token = self.current_token

        if token.type == MUL:
            self._match(MUL)
            node = BinOp(left=node, op=token, right=self._factor())
            node = self._term_prime(node)

        elif token.type == DIV:
            self._match(DIV)
            node = BinOp(left=node, op=token, right=self._factor())
            node = self._term_prime(node)

        return node

    def _expression(self):

        node = self._term()
        node = self._expression_prime(node)

        return node

    def _expression_prime(self, node):

        token = self.current_token

        if token.type == PLUS:
            self._match(PLUS)
            node = BinOp(left=node, op=token, right=self._term())
            node = self._expression_prime(node)

        elif token.type == MINUS:
            self._match(MINUS)
            node = BinOp(left=node, op=token, right=self._term())
            node = self._expression_prime(node)

        return node


# This is the Toy Interpreter.
# The job of the interpreter is to facilitate the communication between
# an instantiated Lexer and Parser, manage a global Symbol Table, evaluate
# a Parser generated Abstract Syntax Tree (AST), and report any detected
# errors during the evaluation of an AST.
class Interpreter(object):

    def __init__(self):
        self.lexer = Lexer()
        self.parser = Parser(self.lexer)
        self.symbol_table = {}

    # Resets this interpreter's state to its initial state.
    def reset(self):
        self.lexer.reset()
        self.parser.reset()
        self.symbol_table = {}

    # Evaluates a given program by:
    #   1. Generating a stream of tokens from the program -- Lexer's Job.
    #   2. Generating a Abstract Syntax Tree (AST) from the stream of tokens -- Parser's Job.
    #   3. Evaluating the AST provided by the parser -- Interpreter's Job.
    #   4. Update the symbol table with the evaluated AST values.
    # This method also returns a reference to the AST generated by the Parser.
    def evaluate_input(self, input_string):
        self.lexer.scanner_input(input_string)
        self.parser.reset()
        prog = self.parser.program()
        self._evaluate_program(prog)

        return prog

    def _error_undefined_variable(self, data):
        raise InterpreterUninitializedVariableError(data)

    def _evaluate_program(self, root):

        if isinstance(root, Program):
            for assignment in root.assignments:
                self._evaluate_program(assignment)

        if isinstance(root, Assign):
            variable_name = root.left.value
            self.symbol_table[variable_name] = int(self._compute_AST(root.right))

    def _compute_AST(self, root):

        if isinstance(root, Id):
            variable_name = root.value
            identifier_value = self.symbol_table.get(variable_name)
            if identifier_value is None:
                self._error_undefined_variable(repr(variable_name))
            else:
                return identifier_value

        elif isinstance(root, Num):
            return int(root.value)

        elif isinstance(root, BinOp):

            if root.token.type == PLUS:
                return self._compute_AST(root.left) + self._compute_AST(root.right)

            elif root.token.type == MINUS:
                return self._compute_AST(root.left) - self._compute_AST(root.right)

            elif root.token.type == MUL:
                return self._compute_AST(root.left) * self._compute_AST(root.right)

            # Supports Integer Division Only: 2/3 returns 0 and 3/2 returns 1
            elif root.token.type == DIV:
                return self._compute_AST(root.left) / self._compute_AST(root.right)

        elif isinstance(root, UnaryOp):

            if root.token.type == PLUS:
                return +self._compute_AST(root.expr)

            elif root.token.type == MINUS:
                return -self._compute_AST(root.expr)

    # Evaluation output is formatted to a single line.
    def stringed_output(self):

        output = ""
        for (key, value) in self.symbol_table.items():
            output += "{key} = {value}, ".format(key=key, value=value)
        output = output[:-2]
        return output

    # Evaluation output is formatted to multi-line--one assignment per line.
    def normal_output(self):
        output = ""
        for (key, value) in self.symbol_table.items():
            output += "{key} = {value}\n".format(key=key, value=value)
        output = output[:-1]
        return output

    # Shows the AST hierarchy by indenting nodes according ot their level in the tree.
    def show_tree_heirarchy(self, root):

        def show_tree(root, level):

            padding = ""
            if level > 0:
                padding = " " * level * 4
                # padding += "\u2514"
                # padding += "\u2500\u2500"
            print(padding + root.__str__())

            if isinstance(root, Program):
                for assignment in root.assignments:
                    show_tree(assignment, level + 1)

            if isinstance(root, BinOp):
                show_tree(root.left, level + 1)
                show_tree(root.right, level + 1)

            if isinstance(root, Assign):
                show_tree(root.left, level + 1)
                show_tree(root.right, level + 1)

            elif isinstance(root, UnaryOp):
                show_tree(root.expr, level + 1)

        show_tree(root, 0)

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
        {program: "rate = 4 + 5; kite = 5; flight = rate + kite;",  expected: "rate = 9, kite = 5, flight = 14"},
        {program: "x = 1; y = 2; z = ---(x+y)*(x+-y);", expected: "x = 1, y = 2, z = 3"},
        {program: "x = 0 y = x; z = ---(x+y);",     expected: "syntax error"},
        {program: "x = 0; y = x; z = ---(x+y));",   expected: "syntax error"},
        {program: "x_2 = 0;",       expected: "x_2 = 0"},
        {program: "x = 001;",       expected: "syntax error"},
        {program: "_2 = 0;",        expected: "syntax error"},
        {program: "0x = 11;",       expected: "syntax error"},
        {program: "3 = 11;",        expected: "syntax error"},
        {program: "_ = 11;",        expected: "syntax error"},
        {program: "x123a = 21;",    expected: "x123a = 21"},
        {program: "x = y;",         expected: "uninitialized variable error: 'y' is undefined."},
        {program: "x = x;",         expected: "uninitialized variable error: 'x' is undefined."},
        {program: "x = y;",         expected: "uninitialized variable error: 'y' is undefined."},
        {program: "x = 56; y = x + z;",             expected: "uninitialized variable error: 'z' is undefined."},
        {program: "x = 56; y = t + v;",             expected: "uninitialized variable error: 't' is undefined."},
        {program: "x = 56; y = (x + (z));",         expected: "uninitialized variable error: 'z' is undefined."},
        {program: "rate = 4; time = rate + speed;", expected: "uninitialized variable error: 'speed' is undefined."},
        {program: "\n rate = 4 + 5; \n kite = 5; \n flight = rate + kite; \n", expected: "rate = 9, kite = 5, flight = 14"},
    ]

    failed_tests = 0
    passed_tests = 0
    print(BCOLORS.OKBLUE, "\n:: BEGIN TESTS ::\n", BCOLORS.ENDC)

    interpreter = Interpreter()
    for program_pkg in programs:

        interpreter.reset()

        output = ""
        prog = None

        try:
            prog = interpreter.evaluate_input(program_pkg[program])
            output = interpreter.stringed_output()
        except InterpreterSyntaxError:
            output = "syntax error"
        except InterpreterUninitializedVariableError as err:
            output = "uninitialized variable error: {0}".format(err)
        except:
            output = "unknown error"

        if str(output) != str(program_pkg[expected]):
            print(BCOLORS.FAIL, "Test: <Failed> Input:", program_pkg[program],
                  "\n\t:: Expected:", program_pkg[expected], "\n\t::   Actual:", output, BCOLORS.ENDC)
            failed_tests += 1
            print(interpreter.lexer.tokens)
            interpreter.show_tree_heirarchy(prog)
        else:
            print(BCOLORS.OKGREEN, "Test: <Passed> Input:", program_pkg[program], ":: Output:", output, BCOLORS.ENDC)
            passed_tests += 1

    print(BCOLORS.HEADER, "\n\tSTATISTICS: Failed = "+str(failed_tests)+", Passed = "+str(passed_tests), BCOLORS.ENDC)
    print(BCOLORS.OKBLUE, "\n:: END TESTS ::", BCOLORS.ENDC)


# Main defines an terminal based interface for the Toy Interpreter.
def main():

    interpreter = Interpreter()

    while True:
        try:
            terminal = input('uNiCoRn> ')
        except EOFError:
            break
        if not terminal:
            print("Accpeted Format:[0..9][+,-][0..9]")
            continue

        output = ""

        if terminal == "exit":
            break

        elif terminal == "reset":
            try:
                interpreter.reset()
            except:
                output = "error -- could not reset"

        elif terminal == "symbols":
            try:
                output = interpreter.normal_output()
            except:
                output = "error -- could not get symbols"

        elif terminal == "test":
            test_driver()

        else:
            try:
                interpreter.evaluate_input(terminal)
                output = interpreter.normal_output()
            except InterpreterSyntaxError:
                output = "syntax error"
            except InterpreterUninitializedVariableError as err:
                output = "uninitialized variable error: {0}".format(err)
            except:
                output = "unknown error"

        print(output)

if __name__ == '__main__':
    main()


"""
TOY GRAMMAR:

Program:
    Assignment*

Assignment:
    Identifier = Exp;

Exp: 
    Exp + Term | Exp - Term | Term

Term:
    Term * Fact | Term / Fact | Fact

Fact:
    ( Exp ) | - Fact | + Fact | Literal | Identifier

Identifier:
    Letter [Letter | Digit]*

Letter:
    a|...|z|A|...|Z|_

Literal:
    0 | NonZeroDigit Digit*

NonZeroDigit:
    1|...|9

Digit:
    0|1|...|9
"""