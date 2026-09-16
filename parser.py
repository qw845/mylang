from ast_nodes import *
from errors import LangError


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self): return self.tokens[self.pos]
    def advance(self):
        t = self.tokens[self.pos]; self.pos += 1; return t
    def check(self, type_, value=None):
        t = self.peek()
        return t.type == type_ and (value is None or t.value == value)
    def match(self, type_, value=None):
        if self.check(type_, value): return self.advance()
        return None
    def expect(self, type_, value=None):
        t = self.match(type_, value)
        if not t:
            got = self.peek().value
            raise LangError(
                f"期望 {value or type_}，实际是 {got!r}",
                self.peek().line
            )
        return t

    def parse(self):
        stmts = []
        while not self.check('EOF'):
            stmts.append(self.declaration())
        return Program(stmts)

    def declaration(self):
        if self.match('KEYWORD', 'fn'):
            return self.func_decl()
        if self.match('KEYWORD', 'import'):
            path = self.expect('STRING').value
            self.expect('OP', ';')
            return Import(path)
        return self.statement()

    def func_decl(self):
        name = self.expect('IDENT').value
        self.expect('OP', '(')
        params = []
        while not self.check('OP', ')'):
            pname = self.expect('IDENT').value
            ptype = None
            if self.match('OP', ':'):
                ptype = self.expect('IDENT').value
            params.append((pname, ptype))
            if not self.match('OP', ','):
                break
        self.expect('OP', ')')
        ret_type = None
        if self.match('OP', '->'):
            ret_type = self.expect('IDENT').value
        body = self.block()
        return FuncDecl(name, params, body, ret_type)

    def statement(self):
        if self.match('KEYWORD', 'let'):
            name = self.expect('IDENT').value
            type_ = None
            if self.match('OP', ':'):
                type_ = self.expect('IDENT').value
            self.expect('OP', '=')
            expr = self.expression()
            self.expect('OP', ';')
            return Let(name, expr, type_)

        if self.match('KEYWORD', 'print'):
            self.expect('OP', '(')
            expr = self.expression()
            self.expect('OP', ')')
            self.expect('OP', ';')
            return Print(expr)

        if self.match('KEYWORD', 'if'):
            self.expect('OP', '(')
            cond = self.expression()
            self.expect('OP', ')')
            then = self.block()
            els = None
            if self.match('KEYWORD', 'elif'):
                els = self.statement()
            elif self.match('KEYWORD', 'else'):
                els = self.block()
            return If(cond, then, els)

        if self.match('KEYWORD', 'while'):
            self.expect('OP', '(')
            cond = self.expression()
            self.expect('OP', ')')
            body = self.block()
            return While(cond, body)

        if self.match('KEYWORD', 'for'):
            self.expect('OP', '(')
            init = self.statement()
            cond = self.expression()
            self.expect('OP', ';')
            step = self.expression()
            self.expect('OP', ')')
            body = self.block()
            return Block([
                init,
                While(cond, Block([body, ExprStmt(step)]))
            ])

        if self.match('KEYWORD', 'switch'):
            return self.parse_switch()

        if self.match('KEYWORD', 'try'):
            try_block = self.block()
            self.expect('KEYWORD', 'catch')
            self.expect('OP', '(')
            var = self.expect('IDENT').value
            self.expect('OP', ')')
            catch_block = self.block()
            return Try(try_block, var, catch_block)

        if self.match('KEYWORD', 'return'):
            expr = self.expression()
            self.expect('OP', ';')
            return Return(expr)

        if self.match('KEYWORD', 'break'):
            self.expect('OP', ';')
            return Break()

        if self.match('KEYWORD', 'continue'):
            self.expect('OP', ';')
            return Continue()

        if self.check('OP', '{'):
            return self.block()

        expr = self.expression()
        self.expect('OP', ';')
        return ExprStmt(expr)

    def parse_switch(self):
        self.expect('OP', '(')
        subject = self.expression()
        self.expect('OP', ')')
        self.expect('OP', '{')
        cases = []
        default = None
        while not self.check('OP', '}'):
            if self.match('KEYWORD', 'case'):
                val = self.expression()
                self.expect('OP', ':')
                stmts = []
                while not self.check('KEYWORD', 'case') and \
                      not self.check('KEYWORD', 'default') and \
                      not self.check('OP', '}'):
                    if self.check('KEYWORD', 'break'):
                        self.advance()
                        self.expect('OP', ';')
                        continue
                    stmts.append(self.declaration())
                cases.append((val, stmts))
            elif self.match('KEYWORD', 'default'):
                self.expect('OP', ':')
                stmts = []
                while not self.check('OP', '}'):
                    if self.check('KEYWORD', 'break'):
                        self.advance()
                        self.expect('OP', ';')
                        continue
                    stmts.append(self.declaration())
                default = Block(stmts)
            else:
                break
        self.expect('OP', '}')
        node = default or Block([])
        for val, stmts in reversed(cases):
            cond = BinOp('==', subject, val)
            node = If(cond, Block(stmts), node)
        return node

    def block(self):
        self.expect('OP', '{')
        stmts = []
        while not self.check('OP', '}'):
            stmts.append(self.declaration())
        self.expect('OP', '}')
        return Block(stmts)

    def expression(self): return self.assignment()

    def assignment(self):
        expr = self.logic_or()
        if self.check('OP', '='):
            self.advance()
            value = self.assignment()
            if isinstance(expr, (Var, Index)):
                return Assign(expr, value)
            raise LangError("赋值号左边不是变量", self.peek().line)
        for op in ['+=', '-=', '*=', '/=']:
            if self.check('OP', op):
                self.advance()
                value = self.assignment()
                if isinstance(expr, (Var, Index)):
                    return Assign(expr, BinOp(op[0], expr, value))
                raise LangError("赋值号左边不是变量", self.peek().line)
        return expr

    def logic_or(self):
        left = self.logic_and()
        while self.match('OP', '||'):
            left = BinOp('||', left, self.logic_and())
        return left

    def logic_and(self):
        left = self.equality()
        while self.match('OP', '&&'):
            left = BinOp('&&', left, self.equality())
        return left

    def equality(self):
        left = self.comparison()
        while self.check('OP', '==') or self.check('OP', '!='):
            op = self.advance().value
            left = BinOp(op, left, self.comparison())
        return left

    def comparison(self):
        left = self.term()
        while self.peek().type == 'OP' and self.peek().value in ('<', '>', '<=', '>='):
            op = self.advance().value
            left = BinOp(op, left, self.term())
        return left

    def term(self):
        left = self.factor()
        while self.peek().type == 'OP' and self.peek().value in ('+', '-'):
            op = self.advance().value
            left = BinOp(op, left, self.factor())
        return left

    def factor(self):
        left = self.unary()
        while self.peek().type == 'OP' and self.peek().value in ('*', '/', '%'):
            op = self.advance().value
            left = BinOp(op, left, self.unary())
        return left

    def unary(self):
        if self.peek().type == 'OP' and self.peek().value in ('!', '-'):
            op = self.advance().value
            return UnaryOp(op, self.unary())
        return self.call()

    def call(self):
        expr = self.primary()
        while True:
            if self.match('OP', '('):
                args = []
                while not self.check('OP', ')'):
                    args.append(self.expression())
                    if not self.match('OP', ','):
                        break
                self.expect('OP', ')')
                expr = Call(expr, args)
            elif self.match('OP', '['):
                index = self.expression()
                self.expect('OP', ']')
                expr = Index(expr, index)
            else:
                break
        return expr

    def primary(self):
        if self.check('NUMBER'):
            return Number(self.advance().value)
        if self.check('STRING'):
            return String(self.advance().value)
        if self.match('KEYWORD', 'true'):
            return Bool(True)
        if self.match('KEYWORD', 'false'):
            return Bool(False)
        if self.check('IDENT'):
            return Var(self.advance().value)
        if self.match('OP', '('):
            expr = self.expression()
            self.expect('OP', ')')
            return expr
        if self.match('OP', '['):
            elements = []
            while not self.check('OP', ']'):
                elements.append(self.expression())
                if not self.match('OP', ','):
                    break
            self.expect('OP', ']')
            return ListLit(elements)
        if self.check('KEYWORD', 'fn'):
            self.advance()
            self.expect('OP', '(')
            params = []
            while not self.check('OP', ')'):
                pname = self.expect('IDENT').value
                ptype = None
                if self.match('OP', ':'):
                    ptype = self.expect('IDENT').value
                params.append((pname, ptype))
                if not self.match('OP', ','):
                    break
            self.expect('OP', ')')
            body = self.block()
            return FuncLit(params, body)
        raise LangError(f"意外的符号 {self.peek().value!r}", self.peek().line)