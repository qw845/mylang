"""
简化版类型检查器
- 只在显式标注类型时检查
- 不标注的变量跳过
- 不做类型推导
"""
from ast_nodes import *


class TypeChecker:
    def __init__(self):
        self.env = {}
        self.funcs = {}

    def check(self, program):
        for stmt in program.stmts:
            self.check_stmt(stmt)

    def check_stmt(self, node):
        if isinstance(node, Let):
            if node.type_:
                actual = self.infer(node.expr)
                if actual and actual != node.type_:
                    raise TypeError(
                        f"类型不匹配: {node.name} 声明为 {node.type_}, 实际 {actual}"
                    )
                self.env[node.name] = node.type_
            else:
                t = self.infer(node.expr)
                if t:
                    self.env[node.name] = t

        elif isinstance(node, FuncDecl):
            params = [(p[0], p[1] or 'any') for p in node.params]
            self.funcs[node.name] = (params, node.return_type or 'any')
            # 检查函数体
            old_env = self.env
            self.env = dict(self.env)
            for pname, ptype in params:
                self.env[pname] = ptype
            self.check_stmt(node.body)
            self.env = old_env

        elif isinstance(node, Block):
            old_env = self.env
            self.env = dict(self.env)
            for s in node.stmts:
                self.check_stmt(s)
            self.env = old_env

        elif isinstance(node, If):
            self.check_stmt(node.then)
            if node.els:
                self.check_stmt(node.els)

        elif isinstance(node, While):
            self.check_stmt(node.body)

        elif isinstance(node, Return):
            self.infer(node.expr)

    def infer(self, node):
        if isinstance(node, Number):
            return 'float' if isinstance(node.value, float) else 'int'
        if isinstance(node, String):
            return 'string'
        if isinstance(node, Bool):
            return 'bool'
        if isinstance(node, Var):
            return self.env.get(node.name, None)
        if isinstance(node, BinOp):
            lt = self.infer(node.left)
            rt = self.infer(node.right)
            if node.op == '+':
                if lt == 'string' or rt == 'string':
                    return 'string'
                if lt and rt:
                    return 'int' if lt == rt == 'int' else 'float'
                return None
            if node.op in ('-', '*', '/', '%'):
                if lt and rt:
                    return 'int' if lt == rt == 'int' else 'float'
                return None
            if node.op in ('<', '>', '<=', '>=', '==', '!='):
                return 'bool'
            if node.op in ('&&', '||'):
                return 'bool'
        if isinstance(node, UnaryOp):
            if node.op == '-':
                return self.infer(node.operand)
            if node.op == '!':
                return 'bool'
        if isinstance(node, Call):
            if isinstance(node.func, Var):
                fname = node.func.name
                if fname in self.funcs:
                    return self.funcs[fname][1]
            return None
        if isinstance(node, ListLit):
            return 'list'
        return None