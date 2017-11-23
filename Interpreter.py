# Token types
#
# EOF (end-of-file) token is used to indicate that
# there is no more input left for lexical analysis
INTEGER, PLUS, MINUS, EOF = 'INTEGER', 'PLUS', 'MINUS', 'EOF'

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
    def __init__(self, text):
        # client string input, e.g. "3+5"
        self.text = text
        # self.pos is an index into self.text
        self.pos = 0
        # current token instance
        self.current_token = None

    def error(self):
        raise Exception('Error parsing input')

    def get_next_token(self):
        # Lexical analyzer (also known as scanner or tokenizer)
        #
        # This method is responsible for breaking a sentence
        # apart into tokens. One token at a time.
        text = self.text

        # is self.pos index past the end of the self.text ?
        # if so, then return EOF token because there is no more
        # input left to convert into tokens
        if self.pos > len(text) - 1:
            return Token(EOF)

        # get a character at the position self.pos and decide
        # what token to create based on the single character
        current_char = text[self.pos]

        if current_char.isdigit():
            self.pos += 1
            return Token(INTEGER, int(current_char))

        elif current_char == "+":
            self.pos += 1
            return Token(PLUS, current_char)

        elif current_char == "-":
            self.pos += 1
            return Token(MINUS, current_char)
        elif current_char == " ":
            self.pos += 1
            return self.get_next_token()

        else:
            self.error()

    def match(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.get_next_token()
        else:
            self.error()

    def expression(self):
        # expression -> integer + integer

        # set current token to the first token taken from the input
        self.current_token = self.get_next_token()

        # we expect the current token to be a single-digit integer
        left = self.current_token
        self.match(INTEGER)

        # we expect the current token to be a '+' or '-' token
        op = self.operation()

        # we expect the current token to be a single-digit integer
        right = self.current_token
        self.match(INTEGER)
        # after the above call the self.current_token is set to
        # EOF token

        # at this point INTEGER PLUS INTEGER sequence of tokens
        # has been successfully found and the method can just
        # return the result of adding two integers, thus
        # effectively interpreting client input
        result = 0
        if op == PLUS:
            result = left.value + right.value
        elif op == MINUS:
            result = left.value - right.value
        return result

    def operation(self):
        if self.current_token.value == "+":
            self.match(PLUS)
            return PLUS
        else:
            self.match(MINUS)
            return MINUS



def main():
    while True:
        try:
            terminal = input('uNiCoRn> ')
        except EOFError:
            break
        if not terminal:
            print("Accpeted Format:[0..9][+,-][0..9]")
            continue

        pickle = Interpreter(terminal)
        result = pickle.expression()

        print(result)

if __name__ == '__main__':
    main()


# Machine = Interpreter("3+6")
#
# print(Machine.get_next_token())
