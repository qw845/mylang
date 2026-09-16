class LangError(Exception):
    def __init__(self, message, line=None, col=None):
        super().__init__(message)
        self.message = message
        self.line = line
        self.col = col


def format_error(err, source=None, filename="<file>"):
    if not isinstance(err, LangError):
        return f"错误: {err}"

    out = [f"错误: {err.message}"]

    if err.line is None:
        return "\n".join(out)

    pos = f"{filename}:{err.line}"
    if err.col:
        pos += f":{err.col}"
    out.append(f"  --> {pos}")

    if source:
        lines = source.split('\n')
        if 1 <= err.line <= len(lines):
            src_line = lines[err.line - 1]
            line_str = str(err.line)
            pad = " " * len(line_str)
            out.append(f" {pad} |")
            out.append(f" {line_str} | {src_line}")
            if err.col:
                out.append(f" {pad} | " + " " * (err.col - 1) + "^")

    return "\n".join(out)