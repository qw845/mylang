from errors import LangError


class Token:
    def __init__(self, type_, value, line):
        self.type = type_
        self.value = value
        self.line = line

    def __repr__(self):
        return f"Token({self.type}, {self.value!r}, line={self.line})"


class Lexer:
    KEYWORDS = {
        'let', 'fn', 'if', 'elif', 'else', 'while', 'return',
        'print', 'true', 'false', 'break', 'continue',
        'for', 'switch', 'case', 'default', 'try', 'catch',
        'import', 'as'
    }

    def __init__(self, source):
        self.src = source
        self.pos = 0
        self.line = 1

    def error(self, msg):
        raise LangError(msg, self.line)

    def tokenize(self):
        tokens = []
        while self.pos < len(self.src):
            ch = self.src[self.pos]

            if ch in ' \t\r':
                self.pos += 1
            elif ch == '\n':
                self.line += 1
                self.pos += 1
            elif ch == '/' and self.src.startswith('//', self.pos):
                while self.pos < len(self.src) and self.src[self.pos] != '\n':
                    self.pos += 1
            elif ch.isdigit():
                tokens.append(self.read_number())
            elif ch.isalpha() or ch == '_':
                tokens.append(self.read_ident())
            elif ch == '"':
                tokens.append(self.read_string())
            else:
                tokens.append(self.read_op())

        tokens.append(Token('EOF', None, self.line))
        return tokens

    def read_number(self):
        start = self.pos
        while self.pos < len(self.src) and self.src[self.pos].isdigit():
            self.pos += 1
        if self.pos < len(self.src) and self.src[self.pos] == '.':
            self.pos += 1
            while self.pos < len(self.src) and self.src[self.pos].isdigit():
                self.pos += 1
            return Token('NUMBER', float(self.src[start:self.pos]), self.line)
        return Token('NUMBER', int(self.src[start:self.pos]), self.line)

    def read_ident(self):
        start = self.pos
        while self.pos < len(self.src) and (self.src[self.pos].isalnum() or self.src[self.pos] == '_'):
            self.pos += 1
        word = self.src[start:self.pos]
        t = 'KEYWORD' if word in self.KEYWORDS else 'IDENT'
        return Token(t, word, self.line)

    def read_string(self):
        start_line = self.line
        self.pos += 1
        start = self.pos
        while self.pos < len(self.src) and self.src[self.pos] != '"':
            if self.src[self.pos] == '\n':
                self.line += 1
            if self.src[self.pos] == '\\' and self.pos + 1 < len(self.src):
                self.pos += 2
                continue
            self.pos += 1
        if self.pos >= len(self.src):
            raise LangError("字符串缺少结束引号", start_line)
        raw = self.src[start:self.pos]
        self.pos += 1
        value = raw.replace('\\n', '\n').replace('\\t', '\t').replace('\\"', '"').replace('\\\\', '\\')
        return Token('STRING', value, start_line)

    def read_op(self):
        for op in ['==', '!=', '<=', '>=', '&&', '||', '+=', '-=', '*=', '/=', '->']:
            if self.src.startswith(op, self.pos):
                self.pos += len(op)
                return Token('OP', op, self.line)
        ch = self.src[self.pos]
        self.pos += 1
        return Token('OP', ch, self.line)