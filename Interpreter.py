class BCOLORS:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# Token types
#
# EOF (end-of-file) token is used to indicate that
# there is no more input left for lexical analysis
INTEGER, PLUS, MINUS, MUL, DIV, EOF = 'INTEGER', 'PLUS', 'MINUS', 'MUL', 'DIV', 'EOF'

class Token(object):
    def __init__(self, type, value=None):
        # token type: INTEGER, PLUS, MINUS, or EOF
        self.type = type
        # token value: 0, 1, 2. 3, 4, 5, 6, 7, 8, 9, '+', or None
        self.value = value

    def __str__(self):
        return 'Token({type},{value})'.format(type=self.type, value=repr(self.value))

    def __repr__(self):
        return self.__str__()

class Interpreter(object):

    def __init__(self, lexer):
        self.lexer = lexer
        # current token instance
        self.current_token = self.lexer.get_next_token()

    def run(self):
        return self.expression()

    ##########################################################
    # Lexer code                                             #
    ##########################################################

    ##########################################################
    # Parser / Interpreter code                              #
    ##########################################################

    def match(self, token_type):

        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def factor(self):

        token = self.current_token
        self.match(INTEGER)
        return token.value

    def expression(self):

        result = self.factor()

        while self.current_token.type in (MUL, DIV):
            token = self.current_token

            if token.type == MUL:
                self.match(MUL)
                result = result * self.factor()

            elif token.type == DIV:
                self.match(DIV)
                result = result / self.factor()

            else:
                self.error()
                break

        return result


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

            else:
                self.error()

        return Token(EOF)

def test_driver():
    program = "program"
    expected = "expected"
    programs = [
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
        {program: "11-2+30-4",  expected: "35"},
        {program: "7 * 4 / 2",  expected: "14"},
        {program: "7 * 4 / 2 * 3", expected: "42"},
        {program: "10 * 4  * 2 * 3 / 8", expected: "30"},
    ]

    failed_tests = 0
    passed_tests = 0
    print(BCOLORS.OKBLUE, "\n:: BEGIN TESTS ::\n", BCOLORS.ENDC)
    for program_pkg in programs:

        lexer = Lexer(program_pkg[program])
        interpreter = Interpreter(lexer)
        result = int(interpreter.run())

        if str(result) != str(program_pkg[expected]):
            print(BCOLORS.FAIL, "Test: <Failed>", program_pkg, "Actual:",result, BCOLORS.ENDC)
            failed_tests += 1
        else:
            print(BCOLORS.OKGREEN, "Test: <Passed>", program_pkg[program], "=", result, BCOLORS.ENDC)
            passed_tests += 1

    print(BCOLORS.HEADER, "\n\tSTATISTICS: Failed = "+str(failed_tests)+", Passed = "+str(passed_tests), BCOLORS.ENDC)
    print(BCOLORS.OKBLUE, "\n:: END TESTS ::", BCOLORS.ENDC)

def main():

    test_driver()
    return

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
