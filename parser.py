from unittest.mock import right

from parser_ast_expr_stmt import*
from Token import*
"""Precedence Table (from highest to lowest)
Parentheses: ()
Unary Operators: +, -, ~ (bitwise NOT), ! (logical NOT)
Multiplicative: *, /, %
Additive: +, -
Shift: <<, >>
Relational: <, >, <=, >=
Equality: ==, !=
Bitwise AND: &
Bitwise XOR: ^
Bitwise OR: |
Logical AND: &&
Logical OR: ||
Assignment (=) 
"""
class Parser:
    def __init__(self,tokens):
        self.curr = 0
        self.tokens = tokens
    def parse(self):
        return self.program()

    def program(self):
        return ProgramStmt(self.body())

    def body(self):
        if self.peek().type == Tokentype.INT:
            self.advance() #consume int
            if self.peek().type == Tokentype.INDENT:
                self.advance() # consume Indent
                name = self.peek_previous()
                if self.peek().type == Tokentype.OPENBRA:

                    self.advance()#consume (
                    return  self.main_fun_declaration(name)
            else:
                print("Error from parser: not a variable declaration or function dec")
                print("correct usage TYPE - IDENTIFIER ")
                exit()

    def main_fun_declaration(self,token:Token):
        name = token.lexeme
        if self.peek().type == Tokentype.CLOSEBRA:
            self.advance()#consume)
            if self.peek().type == Tokentype.OPENPARA:
                self.advance() #consume {
                return Fun_Declaration(name,self.block())
        else:
            print("Missing ) in function declaration ")
            exit()
    def stmt(self):
        if self.peek().type == Tokentype.RETURN:
            self.advance() #consume return
            val = self.expr()
            self.check_semicolon()
            return Return(val)
        elif self.peek().type == Tokentype.INT: #add more datatypes in future
            return self.Declaration()
        elif self.peek().type == Tokentype.IF:
            return self.if_else()
        elif self.peek().type == Tokentype.SEMICOLON:
            return NULL()
        elif self.peek().type == Tokentype.OPENPARA:
            self.advance() #consume {
            return Compound(self.block())
        else:
            expr = self.expr()
            self.check_semicolon()
            return Expression(expr)
    def block(self):
        statements = []
        while self.peek().type != Tokentype.CLOSEPARA and not self.IsEnd():
            statements.append(self.stmt())
        if self.peek().type == Tokentype.CLOSEPARA:
            self.advance() # consume }
            return Block(statements)
        else:
            print("missing } in block statement")
            exit()

    def if_else(self):
        self.advance() #consume if
        if self.peek().type == Tokentype.OPENBRA:
            self.advance() #consume (
            expr = self.expr()
            if_statements = []
            el_statements = []
            if self.peek().type == Tokentype.CLOSEBRA:
                self.advance() # consume )
            else:
                raise ValueError("missing ) in if-else")
            if self.peek().type == Tokentype.OPENPARA:
                self.advance() # consume {
                if_statements = Compound(self.block())
                """while self.peek().type != Tokentype.CLOSEPARA and self.peek().type != Tokentype.EOF:
                    if_statements.append(self.stmt())
                if self.peek().type == Tokentype.CLOSEPARA:
                    self.advance() #consume }
                else:
                    raise ValueError("Missing } in if statement")"""
            else:
                if_statements.append(self.stmt())

            if self.peek().type == Tokentype.ELSE:
                self.advance() #consume else
                if self.peek().type == Tokentype.OPENPARA:
                    self.advance() #consume {
                    el_statements = Compound(self.block())
                    """while self.peek().type != Tokentype.CLOSEPARA and self.peek().type != Tokentype.EOF:
                        el_statements.append(self.stmt())
                    if self.peek().type == Tokentype.CLOSEPARA:
                        self.advance() #consume }
                    else:
                        raise ValueError("Missing } in else statement")"""
                    return If_Else(expr,if_statements,el_statements)
                else:
                    el_statements.append(self.stmt())
                    return If_Else(expr,if_statements,el_statements)
            else:
                return If_Else(expr,if_statements)


        else:
            raise ValueError("missing ( in if-else")

    def Declaration(self):
        self.advance() #consume type
        if self.peek().type == Tokentype.INDENT:
            name = self.primary()
            if self.peek().type == Tokentype.EQUAL:
                self.advance() # consume =
                expr = self.expr()
                self.check_semicolon()
                return Declaration(name,expr)
            else:
                self.check_semicolon()
                return Declaration(name)
        else:
            print("No INDENT type in Declaration")
            exit()
    def expr(self):
        expr = self.assignment()
        return expr
    def ternary(self):
        condition = self.logical_or()
        if self.peek().type == Tokentype.QUESTION:
            self.advance() #consume ?
            then_part = self.expr()
            if self.peek().type == Tokentype.COLON:
                self.advance() #consume :
                else_part = self.expr()
                return Ternary(condition,then_part,else_part)
            else:
                raise ValueError("missing : in ternary operation")
        return condition

    def assignment(self):
        left = self.ternary()
        while self.peek().type == Tokentype.EQUAL:
            self.advance() #consume  =
            right = self.assignment()
            left = Assignment(left,right)
        return left
    def logical_or(self):
        left = self.logical_and()
        while self.peek().type == Tokentype.OR:
            operator = self.peek()
            self.advance()
            right = self.logical_and()
            left = Binary(operator,left,right)
        return left
    def logical_and(self):
        left = self.bit_or()
        while self.peek().type == Tokentype.AND:
            operator = self.peek()
            self.advance()
            right = self.bit_or()
            left = Binary(operator,left,right)
        return left
    def bit_or(self):
        left = self.bit_xor()
        while self.peek().type == Tokentype.BIT_OR:
            self.advance()
            operator = self.peek_previous()
            right = self.bit_xor()
            left = Binary(operator,left,right)
        return left
    def bit_xor(self):
        left = self.bit_and()
        while self.peek().type == Tokentype.BIT_XOR:
            operator = self.peek()
            self.advance() #comsume operator
            right = self.bit_and()
            left = Binary(operator, left, right)
        return left
    def bit_and(self):
        left = self.equality()
        while self.peek().type == Tokentype.BIT_AND:
            self.advance()
            operator = self.peek_previous()
            right = self.equality()
            left = Binary(operator, left, right)
        return left
    def equality(self):
        left = self.relational()
        while self.peek().type == Tokentype.BANG_EQUAL or self.peek().type == Tokentype.EQUAL_EQUAL:
            self.advance()
            operator = self.peek_previous()
            right = self.relational()
            left = Binary(operator, left, right)
        return left
    def relational(self):
        left = self.bit_shift()
        while self.peek().type == Tokentype.LESS_EQUAL or self.peek().type == Tokentype.LESS or self.peek().type == Tokentype.GREATER_EQUAL or self.peek().type == Tokentype.GREATER:
            self.advance()
            operator = self.peek_previous()
            right = self.bit_shift()
            left = Binary(operator, left, right)
        return left
    def bit_shift(self):
        left = self.factor()
        while self.peek().type == Tokentype.LEFT_SWIFT or self.peek().type == Tokentype.RIGHT_SWIFT:
            operator = self.peek()
            self.advance()
            right = self.factor()
            left = Binary(operator,left,right)
        return left
    def factor(self):
        left = self.term()
        while self.peek().type == Tokentype.PLUS or self.peek().type == Tokentype.MINUS:

            operator = self.peek()
            self.advance() #consume + or -
            right = self.term()
            left = Binary(operator,left,right)
        return left
    def term(self):
        left = self.unary()
        while self.peek().type == Tokentype.MULTIPLY or self.peek().type == Tokentype.DIVIDE or self.peek().type == Tokentype.REMAINDER:
            operator = self.peek()
            self.advance() #consume * /
            right = self.unary()
            left = Binary(operator,left,right)
        return left

    def unary(self):
        if self.peek().type == Tokentype.MINUS or self.peek().type == Tokentype.B_NOT or self.peek().type == Tokentype.BANG:
            operator = self.peek()
            self.advance() # consume ~/-
            expr = self.unary()
            return Unary(operator,expr)
        else:
            return self.primary()
    def primary(self):
        token = self.peek()
        if token.type == Tokentype.NUMBER:
            self.advance()
            return Literal(token.lexeme,Tokentype.INT)
        if token.type == Tokentype.STRING:
            self.advance()
            return Literal(token.lexeme,Tokentype.STRING)
        if token.type == Tokentype.INDENT:
            self.advance()
            return IDENTIFIER(token.lexeme)
        if token.type == Tokentype.OPENBRA:
            self.advance() #consume (
            expr = self.expr() #change it future
            if self.peek().type == Tokentype.CLOSEBRA:
                self.advance() #consume )
                return expr
            else :
                print("Error from Lexer missing ) in grouping (expr)")
                exit()

    def peek(self):
        # be aware this peek method is also increasing curr pointer by one
        if self.curr<len(self.tokens):
            return self.tokens[self.curr]
        return Token(Tokentype.EOF,"EOF",0)
    def advance(self):
        if self.IsEnd():
            return False
        self.curr = self.curr + 1
        return True
    def IsEnd(self):
        if self.curr>= len(self.tokens) or self.peek()==Tokentype.EOF:
            return True
        return False
    def peek_previous(self):
        if self.curr-1>=0:
            return self.tokens[self.curr-1]
        else:
            print("Error from parser: peek_previous() accessing index less than 0")
            exit()
    def consume(self,token_type:Tokentype,message):
        if self.peek().type != token_type:
            print(message)
            exit()
        else:
            self.advance()
            return self.peek_previous()
    def check_semicolon(self):
        if self.peek().type != Tokentype.SEMICOLON:
            print("Missing semicolon in statement")
            exit()
        self.advance() #consume ;