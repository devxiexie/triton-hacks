from sys import exit

TOKENS = {
    "LeftParen": "LeftParen",
    "RightParen": "RightParen",
    "LeftBrace": "LeftBrace",
    "RightBrace": "RightBrace",
    "LeftBracket": "LeftBracket",
    "RightBracket": "RightBracket",
    "Comma": "Comma",
    "Word": "Word",
    "Number": "Number",
    "String": "String",
    "Array": "Array",
    "Dict": "Dict",
    "Func": "Func",
    "Call": "Call",
    "Var": "Var",
    "If": "If",
    "Elif": "Elif",
    "Else": "Else",
    "While": "While",
    "For": "For",
    "True": "True",
    "False": "False",
    "And": "And",
    "Or": "Or",
    "Not": "Not",
    "Return": "Return",
    "Modulo": "Modulo",
    "Equal": "Equal",
    "Equality": "Equality",
    "LessThan": "LessThan",
    "LessThanOrEqual": "LessThanOrEqual",
    "GreaterThan": "GreaterThan",
    "GreaterThanOrEqual": "GreaterThanOrEqual",
    "NotEquality": "NotEquality",
    "Class": "Class",
    "New": "New",
    "Range": "Range",
    "Colon": "Colon",
    "Period": "Period",
    "Plus": "Plus",
    "Minus": "Minus",
    "Times": "Times",
    "Divide": "Divide",
    "Eof": "Eof",
}

KEYWORDS = {
    "giveback": TOKENS["Return"],
    "life": TOKENS["Var"],
    "grow": TOKENS["For"],
    "range": TOKENS["Range"],
    "birth": TOKENS["Func"],
    "cycle": TOKENS["While"],
    "flora": TOKENS["Class"],
    "new": TOKENS["New"],
    "leaf": TOKENS["If"],
    "stem": TOKENS["Elif"],
    "root": TOKENS["Else"],
    "Nature": TOKENS["True"],
    "Technology": TOKENS["False"],
    "and": TOKENS["And"],
    "or": TOKENS["Or"],
}


def new_token(kind, value, content):
    return {"type": kind, "value": value, "content": content}


class Lexer:
    def __init__(this, source="", current=0, tokens=[], line=0):
        this.current = current
        this.source = source
        this.tokens = tokens
        this.line = line

    def peek(this):
        if this.current >= len(this.source):
            return "\0"
        return this.source[this.current]

    def peek_next(this):
        if this.current >= len(this.source):
            return "\0"
        return this.source[this.current + 1]

    def advance(this):
        if this.current >= len(this.source):
            return "\0"
        ret = this.peek()
        this.current += 1
        return ret

    # def match(this, char):
    #     if this.peek() == char:
    #         this.advance()
    #         return True
    #     return False

    def add_token(this, kind, value, content):
        this.tokens.append(new_token(kind, value, content))


def scan_token(lexer):
    char = lexer.advance()

    def isAlphanumeric(char):
        return char != " " and (char.isalpha() or char.isnumeric() or char == "_")

    def string(char):
        text = ""
        while lexer.peek() != char and lexer.peek() != "\0":
            if lexer.peek() == "\n":
                lexer.line += 1
            text += lexer.advance()
        # can have error if there isnt a closing quote
        lexer.advance()
        lexer.add_token(TOKENS["String"], text, text)

    def number():
        text = ""
        while lexer.peek().isnumeric():
            text += lexer.advance()
        if lexer.peek() == "." and lexer.peek_next().isnumeric():
            text += lexer.advance()
            while lexer.peek().isnumeric():
                text += lexer.advance()
        lexer.add_token(TOKENS["Number"], float(text), text)

    def identifier():
        text = ""
        while isAlphanumeric(lexer.peek()):
            text += lexer.advance()
        this = KEYWORDS.get(text)
        if this is None:
            this = TOKENS["Word"]
        lexer.add_token(this, text, text)

    match char:
        case "(":
            lexer.add_token(TOKENS["LeftParen"], "(", "(")
        case ")":
            lexer.add_token(TOKENS["RightParen"], ")", ")")
        case "{":
            lexer.add_token(TOKENS["LeftBrace"], "{", "{")
        case "}":
            lexer.add_token(TOKENS["RightBrace"], "}", "}")
        case "[":
            lexer.add_token(TOKENS["LeftBracket"], "[", "[")
        case "]":
            lexer.add_token(TOKENS["RightBracket"], "]", "]")
        case ",":
            lexer.add_token(TOKENS["Comma"], ",", ",")
        case "+":
            lexer.add_token(TOKENS["Plus"], "+", "+")
        case "-":
            lexer.add_token(TOKENS["Minus"], "-", "-")
        case "*":
            lexer.add_token(TOKENS["Times"], "*", "*")
        case "/":
            lexer.add_token(TOKENS["Divide"], "/", "/")
        case "%":
            lexer.add_token(TOKENS["Modulo"], "%", "%")
        case "=":
            if lexer.peek() == "=":
                lexer.advance()
                lexer.add_token(TOKENS["Equality"], "==", "==")
            else:
                lexer.add_token(TOKENS["Equal"], "=", "=")
        case '"':
            string('"')
        case "'":
            string("'")
        case "|":
            lexer.add_token(TOKENS["Or"], "|", "|")
        case "&":
            lexer.add_token(TOKENS["And"], "&", "&")
        case "<":
            if lexer.peek() == "=":
                lexer.advance()
                lexer.add_token(TOKENS["LessThanOrEqual"], "<=", "<=")
            else:
                lexer.add_token(TOKENS["LessThan"], "<", "<")
        case ">":
            if lexer.peek() == "=":
                lexer.advance()
                lexer.add_token(TOKENS["GreaterThanOrEqual"], ">=", ">=")
            else:
                lexer.add_token(TOKENS["GreaterThan"], ">", ">")
        case "!":
            if lexer.peek() == "=":
                lexer.advance()
                lexer.add_token(TOKENS["NotEquality"], "!=", "!=")
            else:
                lexer.add_token(TOKENS["Not"], "!", "!")
        case ":":
            lexer.add_token(TOKENS["Colon"], ":", ":")
        case ".":
            lexer.add_token(TOKENS["Period"], ".", ".")
        case "#":
            while lexer.peek() != "\n" and lexer.peek() != "\0":
                lexer.advance()
            lexer.line += 1
        case "\n":
            lexer.line += 1
        case " ":
            return
        case "\t":
            return
        case _:
            if char.isalpha():
                lexer.current -= 1
                identifier()
            elif char.isnumeric():
                lexer.current -= 1
                number()
            else:
                raise Exception(
                    f"Unexpected character: {char} at line {lexer.line + 1}"
                )


def scan_tokens(lexer):
    # while lexer.current < len(lexer.source):
    while lexer.peek() != "\0":
        scan_token(lexer)
    lexer.add_token(TOKENS["Eof"], "", "")
    return lexer.tokens
