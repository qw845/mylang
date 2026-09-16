import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from errors import LangError, format_error
from lexer import Lexer
from parser import Parser
from interpreter import Interpreter

VERSION = "1.0"

HELP_TEXT = f"""mylang 编程语言 v{VERSION}

用法:
    mylang <文件.mylang>        运行文件
    mylang                      进入 REPL
    mylang --help               显示帮助
    mylang --version            显示版本

语法速查:
    变量      let x = 10;
    函数      fn add(a, b) {{ return a + b; }}
    匿名函数  fn(x) {{ return x * 2; }}
    条件      if / elif / else
    循环      while / for
    多分支    switch / case / default
    异常      try / catch
    打印      print("hello");
    输入      input("prompt: ")
    数组      [1, 2, 3]
    字典      dict()
    注释      // ...

示例:
    mylang hello.mylang
"""


def _project_dir():
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


def load_stdlib(interp):
    stdlib = os.path.join(_project_dir(), 'stdlib.mylang')
    if not os.path.exists(stdlib):
        return
    with open(stdlib, encoding='utf-8') as f:
        src = f.read()
    ast = Parser(Lexer(src).tokenize()).parse()
    interp.execute(ast)


def run_source(source, filename="<stdin>", base_dir=None):
    interp = Interpreter(base_dir=base_dir or os.getcwd())
    load_stdlib(interp)
    try:
        ast = Parser(Lexer(source).tokenize()).parse()
        interp.execute(ast)
    except LangError as e:
        print(format_error(e, source, filename), file=sys.stderr)
        sys.exit(1)
    except RecursionError:
        print("错误: 递归太深（可能是无限递归）", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"运行时错误: {e}", file=sys.stderr)
        sys.exit(1)


def run_file(path):
    if not os.path.exists(path):
        print(f"错误: 找不到文件 {path}", file=sys.stderr)
        sys.exit(1)
    with open(path, encoding='utf-8') as f:
        source = f.read()
    run_source(source, path, os.path.dirname(os.path.abspath(path)))


def repl():
    print(f"mylang v{VERSION} REPL")
    print("输入 exit 退出, help 查看语法")
    print()

    interp = Interpreter()
    load_stdlib(interp)

    history_file = os.path.join(os.path.expanduser("~"), ".mylang_history")
    try:
        import readline
        if os.path.exists(history_file):
            try:
                readline.read_history_file(history_file)
            except Exception:
                pass
    except ImportError:
        readline = None

    while True:
        try:
            line = input(">>> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not line.strip():
            continue
        if line.strip() in ('exit', 'quit', 'exit()', 'quit()'):
            break
        if line.strip() in ('help', '--help', '-h'):
            print(HELP_TEXT)
            continue
        if line.strip() in ('version', '--version', '-v'):
            print(f"mylang {VERSION}")
            continue

        try:
            ast = Parser(Lexer(line).tokenize()).parse()
            interp.execute(ast)
        except LangError as e:
            print(format_error(e, line, "<repl>"))
        except RecursionError:
            print("错误: 递归太深")
        except Exception as e:
            print(f"运行时错误: {e}")

    if readline:
        try:
            readline.write_history_file(history_file)
        except Exception:
            pass


def main():
    args = sys.argv[1:]

    if not args:
        repl()
        return

    first = args[0]
    if first in ('--help', '-h'):
        print(HELP_TEXT)
        return
    if first in ('--version', '-v'):
        print(f"mylang {VERSION}")
        return

    run_file(first)


if __name__ == "__main__":
    main()