from naturelexer import TOKENS
from natureast import (
    ast_var,
    ast_func,
    ast_class,
    ast_dict,
    ast_array,
    ast_return,
    ast_if,
    ast_else,
    ast_while,
    ast_for,
    ast_number,
    ast_string,
    ast_bool,
    ast_binary,
    ast_call,
    ast_attr,
    ast_chain,
)


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    def peek_token(self):
        if self.current >= len(self.tokens):
            return None
        return self.tokens[self.current]

    def peek_TOKENS(self):
        if self.current >= len(self.tokens):
            return None
        return self.tokens[self.current].get("type")

    def eat(self, type):
        if self.peek_TOKENS() == type:
            res = self.tokens[self.current]
            self.current += 1
            return res
        token = self.peek_token()
        raise Exception(f"Expected {type} but got {token.get('TYPE')}")


def stmt(parser):
    cur = parser.peek_TOKENS()
    if cur == TOKENS["Var"]:
        return varStmt(parser)
    elif cur == TOKENS["Call"]:
        return call(parser)
    elif cur == TOKENS["Func"]:
        return funcStmt(parser)
    elif cur == TOKENS["Class"]:
        return classStmt(parser)
    elif cur == TOKENS["Return"]:
        return returnStmt(parser)
    elif cur == TOKENS["For"]:
        return forStmt(parser)
    elif cur == TOKENS["While"]:
        return whilteStmt(parser)
    elif cur == TOKENS["If"]:
        return ifStmt(parser)
    else:
        return expr(parser)


def simple(parser):
    token = parser.eat(parser.peek_TOKENS())
    self = token["type"]
    if self == TOKENS["Word"]:
        return ast_var(token["value"])
    elif self == TOKENS["Number"]:
        return ast_number(token["value"])
    elif self == TOKENS["Minus"]:
        return ast_number(-simple(parser)["value"])
    elif self == TOKENS["String"]:
        return ast_string(token["value"])
    elif self == TOKENS["True"]:
        return ast_bool(True)
    elif self == TOKENS["False"]:
        return ast_bool(False)
    elif self == TOKENS["New"]:
        id = parser.eat(TOKENS["Word"])
    elif self == TOKENS["LeftParen"]:
        left = expr(parser, True)
        parser.eat(TOKENS["RightParen"])
        return left
    elif self == TOKENS["LeftBracket"]:
        items = []
        if parser.peek_TOKENS() != TOKENS["RightBracket"]:
            items.append(expr(parser))
            while parser.peek_TOKENS() == TOKENS["Comma"]:
                parser.eat(TOKENS["Comma"])
                items.append(expr(parser))
        parser.eat(TOKENS["RightBracket"])
        return ast_array(items)
    elif self == TOKENS["LeftBrace"]:
        obj = {}
        while parser.peek_TOKENS() != TOKENS["RightBrace"]:
            key = parser.eat(TOKENS["String"])
            parser.eat(TOKENS["Colon"])
            obj[key["value"]] = expr(parser)
            if parser.peek_TOKENS() != TOKENS["RightBrace"]:
                parser.eat(TOKENS["Comma"])
        parser.eat(TOKENS["RightBrace"])
        return ast_dict(obj)
    # else:
    #     raise Exception("Expected expression but got " + self)


def is_op(token):
    return token["type"] in [
        TOKENS["And"],
        TOKENS["Or"],
        TOKENS["Equality"],
        TOKENS["Equal"],
        TOKENS["Plus"],
        TOKENS["Minus"],
        TOKENS["Times"],
        TOKENS["Divide"],
        TOKENS["Modulo"],
        TOKENS["GreaterThan"],
        TOKENS["GreaterThanOrEqual"],
        TOKENS["LessThan"],
        TOKENS["LessThanOrEqual"],
    ]


def call(parser):
    expr = simple(parser)
    if (
        parser.peek_TOKENS() == TOKENS["LeftParen"]
        or parser.peek_TOKENS() == TOKENS["LeftBracket"]
    ):
        chain = []
        while (
            parser.peek_TOKENS() == TOKENS["LeftParen"]
            or parser.peek_TOKENS() == TOKENS["LeftBracket"]
        ):
            if parser.peek_TOKENS() == TOKENS["LeftParen"]:
                parser.eat(TOKENS["LeftParen"])
                args = exprList(parser)
                parser.eat(TOKENS["RightParen"])
                chain.append(ast_call(args))
            else:
                parser.eat(TOKENS["LeftBracket"])
                if parser.peek_TOKENS() == TOKENS["Period"]:
                    parser.eat(TOKENS["Period"])
                    id = parser.eat(parser.peek_TOKENS())
                    chain.append(ast_attr(id["value"]))
                else:
                    chain.append(expr(parser))
                parser.eat(TOKENS["RightBracket"])
        return ast_chain(expr, chain)
    return expr


def expr(this, wrapped=False):
    left = call(this)
    if is_op(this.peek_token()):
        op = this.eat(this.peek_TOKENS())["value"]
        right = expr(this)
        return ast_binary(left, op, right, wrapped)
    return left


def exprList(parser):
    exprs = []
    if parser.peek_TOKENS() != TOKENS["RightParen"]:
        exprs.append(expr(parser))
        while parser.peek_TOKENS() == TOKENS["Comma"]:
            parser.eat(TOKENS["Comma"])
            exprs.append(expr(parser))
    return exprs


def idList(this):
    ids = []
    if this.peek_TOKENS() == TOKENS["Word"]:
        ids.append(this.eat(TOKENS["Word"])["value"])
        while this.peek_TOKENS() == TOKENS["Comma"]:
            this.eat(TOKENS["Comma"])
            ids.append(this.eat(TOKENS["Word"])["value"])
    return ids


def varStmt(parser):
    parser.eat(TOKENS["Var"])
    id = parser.eat(TOKENS["Word"])["value"]
    parser.eat(TOKENS["Equal"])
    value = expr(parser)
    return ast_var(id, value)


def funcStmt(parser):
    parser.eat(TOKENS["Func"])
    id = parser.eat(TOKENS["Word"])["value"]
    parser.eat(TOKENS["LeftParen"])
    params = idList(parser)
    parser.eat(TOKENS["RightParen"])
    parser.eat(TOKENS["LeftBrace"])
    body = []
    while parser.peek_TOKENS() != TOKENS["RightBrace"]:
        body.append(stmt(parser))
    parser.eat(TOKENS["RightBrace"])
    return ast_func(id, params, body)


def classStmt(parser):
    parser.eat(TOKENS["Class"])
    id = parser.eat(TOKENS["Word"])["value"]
    parser.eat(TOKENS["LeftBrace"])
    methods = []
    while parser.peek_TOKENS() == TOKENS["Func"]:
        methods.append(funcStmt(parser))
    parser.eat(TOKENS["RightBrace"])
    return ast_class(id, methods)


def returnStmt(parser):
    parser.eat(TOKENS["Return"])
    value = expr(parser)
    return ast_return(value)


def ifStmt(parser):
    parser.eat(TOKENS["If"])
    parser.eat(TOKENS["LeftParen"])
    condition = stmt(parser)
    parser.eat(TOKENS["RightParen"])
    parser.eat(TOKENS["LeftBrace"])
    body = []
    while parser.peek_TOKENS() != TOKENS["RightBrace"]:
        body.append(stmt(parser))
    parser.eat(TOKENS["RightBrace"])
    otherwise = []
    if parser.peek_TOKENS() == TOKENS["Else"]:
        otherwise.append(elseStmt(parser))
    while parser.peek_TOKENS() == TOKENS["Elif"]:
        otherwise.append(elifStmt(parser))
    if parser.peek_TOKENS() == TOKENS["Else"]:
        otherwise.append(elseStmt(parser))
    return ast_if(condition, body, otherwise)


def elifStmt(parser):
    parser.eat(TOKENS["Elif"])
    parser.eat(TOKENS["LeftParen"])
    condition = stmt(parser)
    parser.eat(TOKENS["RightParen"])
    parser.eat(TOKENS["LeftBrace"])
    body = []
    while parser.peek_TOKENS() != TOKENS["RightBrace"]:
        body.append(stmt(parser))
    parser.eat(TOKENS["RightBrace"])
    return ast_if(condition, body)


def elseStmt(parser):
    parser.eat(TOKENS["Else"])
    parser.eat(TOKENS["LeftBrace"])
    body = []
    while parser.peek_TOKENS() != TOKENS["RightBrace"]:
        body.append(stmt(parser))
    parser.eat(TOKENS["RightBrace"])
    return ast_else(body)


def forStmt(parser):
    parser.eat(TOKENS["For"])
    id = parser.eat(TOKENS["Word"])
    parser.eat(TOKENS["Range"])
    parser.eat(TOKENS["LeftParen"])
    through = exprList(parser)
    parser.eat(TOKENS["RightParen"])
    parser.eat(TOKENS["LeftBrace"])
    body = []
    while parser.peek_TOKENS() != TOKENS["RightBrace"]:
        body.append(stmt(parser))
    parser.eat(TOKENS["RightBrace"])
    return ast_for(id, through, body)


def whilteStmt(parser):
    parser.eat(TOKENS["While"])
    parser.eat(TOKENS["LeftParen"])
    condition = expr(parser)
    parser.eat(TOKENS["RightParen"])
    parser.eat(TOKENS["LeftBrace"])
    body = []
    while parser.peek_TOKENS() != TOKENS["RightBrace"]:
        body.append(stmt(parser))
    parser.eat(TOKENS["RightBrace"])
    return ast_while(condition, body)


def program(parser):
    parsed = []
    while parser.peek_TOKENS() != TOKENS["Eof"]:
        parsed.append(stmt(parser))
    return parsed
