class Node:
    pass

# 语句
class Program(Node):
    def __init__(self, stmts): self.stmts = stmts

class Let(Node):
    def __init__(self, name, expr, type_=None):
        self.name, self.expr, self.type_ = name, expr, type_

class Assign(Node):
    def __init__(self, target, expr): self.target, self.expr = target, expr

class Print(Node):
    def __init__(self, expr): self.expr = expr

class If(Node):
    def __init__(self, cond, then, els=None): self.cond, self.then, self.els = cond, then, els

class While(Node):
    def __init__(self, cond, body): self.cond, self.body = cond, body

class FuncDecl(Node):
    def __init__(self, name, params, body, return_type=None):
        self.name, self.params, self.body, self.return_type = name, params, body, return_type

class Return(Node):
    def __init__(self, expr): self.expr = expr

class Break(Node): pass
class Continue(Node): pass

class Block(Node):
    def __init__(self, stmts): self.stmts = stmts

class ExprStmt(Node):
    def __init__(self, expr): self.expr = expr

class Try(Node):
    def __init__(self, try_block, catch_var, catch_block):
        self.try_block = try_block
        self.catch_var = catch_var
        self.catch_block = catch_block

class Import(Node):
    def __init__(self, path): self.path = path

# 表达式
class Number(Node):
    def __init__(self, value): self.value = value

class String(Node):
    def __init__(self, value): self.value = value

class Bool(Node):
    def __init__(self, value): self.value = value

class Var(Node):
    def __init__(self, name): self.name = name

class BinOp(Node):
    def __init__(self, op, left, right): self.op, self.left, self.right = op, left, right

class UnaryOp(Node):
    def __init__(self, op, operand): self.op, self.operand = op, operand

class Call(Node):
    def __init__(self, func, args): self.func, self.args = func, args

class Index(Node):
    def __init__(self, obj, index): self.obj, self.index = obj, index

class ListLit(Node):
    def __init__(self, elements): self.elements = elements

class FuncLit(Node):
    def __init__(self, params, body): self.params, self.body = params, body