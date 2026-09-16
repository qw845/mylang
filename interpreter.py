import math
import os
from ast_nodes import *
from errors import LangError


class Env:
    def __init__(self, parent=None):
        self.vars = {}
        self.parent = parent

    def get(self, name):
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get(name)
        raise LangError(f"未定义变量: {name}")

    def set(self, name, value):
        self.vars[name] = value

    def assign(self, name, value):
        if name in self.vars:
            self.vars[name] = value
        elif self.parent:
            self.parent.assign(name, value)
        else:
            raise LangError(f"未定义变量: {name}")

    def has(self, name):
        if name in self.vars: return True
        if self.parent: return self.parent.has(name)
        return False


class ReturnSignal(Exception):
    def __init__(self, value): self.value = value

class BreakSignal(Exception): pass
class ContinueSignal(Exception): pass


class Function:
    def __init__(self, params, body, closure, name='<anonymous>'):
        self.params = params
        self.body = body
        self.closure = closure
        self.name = name

    def call(self, args, interpreter):
        env = Env(self.closure)
        for (pname, _), a in zip(self.params, args):
            env.set(pname, a)
        try:
            interpreter.exec_block(self.body.stmts, env)
        except ReturnSignal as r:
            return r.value
        return None

    def __repr__(self):
        return f"<fn {self.name}>"


class Interpreter:
    def __init__(self, base_dir=None):
        self.global_env = Env()
        self.base_dir = base_dir or os.getcwd()
        self.install_builtins(self.global_env)
        self.imported = set()

    def execute(self, program):
        self.exec_block(program.stmts, self.global_env)

    def install_builtins(self, env):
        env.set('print', lambda *args: print(*args))
        env.set('input', lambda prompt='': input(prompt))
        env.set('len', lambda x: len(x))
        env.set('str', lambda x: str(x))
        env.set('num', lambda x: float(x) if '.' in str(x) else int(x))
        env.set('type', lambda x: type(x).__name__)
        env.set('abs', abs)
        env.set('max', max)
        env.set('min', min)
        env.set('sqrt', math.sqrt)
        env.set('range', lambda n: list(range(n)))
        env.set('int', lambda x: int(float(x)) if isinstance(x, str) else int(x))

        env.set('upper', lambda s: s.upper())
        env.set('lower', lambda s: s.lower())
        env.set('split', lambda s, sep=' ': s.split(sep))
        env.set('join', lambda sep, lst: sep.join(str(x) for x in lst))
        env.set('replace', lambda s, a, b: s.replace(a, b))
        env.set('trim', lambda s: s.strip())
        env.set('substr', lambda s, i, n: s[i:i+n])
        env.set('find', lambda s, sub: s.find(sub))

        env.set('push', lambda lst, x: (lst.append(x), lst)[1])
        env.set('pop', lambda lst: lst.pop())
        env.set('sort', lambda lst: sorted(lst))
        env.set('reverse', lambda lst: list(reversed(lst)))
        env.set('contains', lambda lst, x: x in lst)

        env.set('dict', lambda: {})
        env.set('has', lambda d, k: k in d)
        env.set('keys', lambda d: list(d.keys()))
        env.set('values', lambda d: list(d.values()))
        env.set('del', lambda d, k: d.pop(k, None))

        env.set('read_file', lambda p: open(p, encoding='utf-8').read())
        env.set('write_file', lambda p, c: open(p, 'w', encoding='utf-8').write(c))
        env.set('append_file', lambda p, c: open(p, 'a', encoding='utf-8').write(c))
        env.set('exists', lambda p: os.path.exists(p))

    def exec_block(self, stmts, env):
        for s in stmts:
            self.exec_stmt(s, env)

    def exec_stmt(self, node, env):
        if isinstance(node, Let):
            env.set(node.name, self.eval(node.expr, env))

        elif isinstance(node, Assign):
            value = self.eval(node.expr, env)
            self.assign_target(node.target, value, env)

        elif isinstance(node, Print):
            print(self.eval(node.expr, env))

        elif isinstance(node, If):
            if self.truthy(self.eval(node.cond, env)):
                self.exec_stmt(node.then, env)
            elif node.els:
                self.exec_stmt(node.els, env)

        elif isinstance(node, While):
            while self.truthy(self.eval(node.cond, env)):
                try:
                    self.exec_stmt(node.body, env)
                except BreakSignal:
                    break
                except ContinueSignal:
                    continue

        elif isinstance(node, Block):
            self.exec_block(node.stmts, Env(env))

        elif isinstance(node, FuncDecl):
            fn = Function(node.params, node.body, env, node.name)
            env.set(node.name, fn)

        elif isinstance(node, Return):
            raise ReturnSignal(self.eval(node.expr, env))

        elif isinstance(node, Break):
            raise BreakSignal()

        elif isinstance(node, Continue):
            raise ContinueSignal()

        elif isinstance(node, ExprStmt):
            self.eval(node.expr, env)

        elif isinstance(node, Try):
            try:
                self.exec_stmt(node.try_block, env)
            except (ReturnSignal, BreakSignal, ContinueSignal):
                raise
            except LangError as e:
                catch_env = Env(env)
                catch_env.set(node.catch_var, e.message)
                self.exec_block(node.catch_block.stmts, catch_env)
            except Exception as e:
                catch_env = Env(env)
                catch_env.set(node.catch_var, str(e))
                self.exec_block(node.catch_block.stmts, catch_env)

        elif isinstance(node, Import):
            self.do_import(node.path, env)

        else:
            raise RuntimeError(f"unknown statement: {node}")

    def do_import(self, path, env):
        if not os.path.isabs(path):
            path = os.path.join(self.base_dir, path)
        if path in self.imported:
            return
        self.imported.add(path)
        if not os.path.exists(path):
            raise LangError(f"找不到模块: {path}")
        with open(path, encoding='utf-8') as f:
            source = f.read()
        from lexer import Lexer
        from parser import Parser
        tokens = Lexer(source).tokenize()
        ast = Parser(tokens).parse()
        self.exec_block(ast.stmts, env)

    def assign_target(self, target, value, env):
        if isinstance(target, Var):
            env.assign(target.name, value)
        elif isinstance(target, Index):
            obj = self.eval(target.obj, env)
            idx = self.eval(target.index, env)
            obj[idx] = value
        else:
            raise LangError("无效的赋值目标")

    def eval(self, node, env):
        if isinstance(node, Number): return node.value
        if isinstance(node, String): return node.value
        if isinstance(node, Bool): return node.value
        if isinstance(node, Var): return env.get(node.name)

        if isinstance(node, ListLit):
            return [self.eval(e, env) for e in node.elements]

        if isinstance(node, FuncLit):
            return Function(node.params, node.body, env)

        if isinstance(node, Index):
            obj = self.eval(node.obj, env)
            idx = self.eval(node.index, env)
            try:
                return obj[idx]
            except (IndexError, KeyError):
                raise LangError(f"索引越界: {idx}")

        if isinstance(node, UnaryOp):
            v = self.eval(node.operand, env)
            if node.op == '-': return -v
            if node.op == '!': return not self.truthy(v)

        if isinstance(node, BinOp):
            op = node.op
            if op == '&&':
                return self.truthy(self.eval(node.left, env)) and self.truthy(self.eval(node.right, env))
            if op == '||':
                return self.truthy(self.eval(node.left, env)) or self.truthy(self.eval(node.right, env))

            l = self.eval(node.left, env)
            r = self.eval(node.right, env)

            if op == '+':
                if isinstance(l, str) or isinstance(r, str):
                    return str(l) + str(r)
                return l + r
            if op == '-': return l - r
            if op == '*': return l * r
            if op == '/':
                if r == 0:
                    raise LangError("除零错误")
                return l / r
            if op == '%':
                if r == 0:
                    raise LangError("取模零错误")
                return l % r
            if op == '==': return l == r
            if op == '!=': return l != r
            if op == '<': return l < r
            if op == '>': return l > r
            if op == '<=': return l <= r
            if op == '>=': return l >= r
            raise LangError(f"未知运算符: {op}")

        if isinstance(node, Call):
            fn = self.eval(node.func, env)
            args = [self.eval(a, env) for a in node.args]
            if isinstance(fn, Function):
                return fn.call(args, self)
            if callable(fn):
                try:
                    return fn(*args)
                except Exception as e:
                    raise LangError(str(e))
            raise LangError(f"对象不可调用: {fn}")

        if isinstance(node, Assign):
            value = self.eval(node.expr, env)
            self.assign_target(node.target, value, env)
            return value

        raise LangError(f"未知表达式: {node}")

    def truthy(self, v):
        if v is None or v is False: return False
        if v == 0 or v == '' or v == []: return False
        return True