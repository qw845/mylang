\# mylang



A simple programming language written from scratch.



\[!\[Release]】(https://github.com/qw845/mylang/releases)



\## What is mylang?



`mylang` is a small, easy-to-learn programming language. It is implemented from scratch with a hand-written lexer, parser, and tree-walking interpreter. No parser generators, no compiler frameworks — just plain Python.



It is designed for:



\- Learning how programming languages work

\- Experimenting with new syntax and features

\- Writing small scripts and tools



\## Features



\- Full interpreter pipeline: \*\*Lexer → Parser → AST → Evaluator\*\*

\- Rich syntax:

&#x20; - Variables: `let x = 10;`

&#x20; - Functions: `fn add(a, b) { return a + b; }`

&#x20; - Anonymous functions: `fn(x) { return x \* 2; }`

&#x20; - Conditionals: `if` / `elif` / `else`

&#x20; - Loops: `while`, `for`

&#x20; - Multi-branch: `switch` / `case` / `default`

&#x20; - Exceptions: `try` / `catch`

&#x20; - Arrays: `\[1, 2, 3]`

&#x20; - Dicts: `dict()`

&#x20; - Module import: `import "file.mylang";`

\- Standard library (`stdlib.mylang`):

&#x20; - Functional: `map`, `filter`, `reduce`, `each`

&#x20; - Math: `sum`, `max\_of`, `min\_of`, `pow`

&#x20; - Sorting: `bubble\_sort`, `quick\_sort`

&#x20; - Strings: `repeat`, `starts\_with`, `ends\_with`, `capitalize`

&#x20; - File: `read\_lines`, `write\_lines`

\- Error messages with line number and source snippet

\- REPL, command-line, and double-click run support



\## Download




\- \*\*Source code\*\*: `git clone https://github.com/qw845/mylang.git`



\## Quick Start



After unzipping `mylang-v1.0.zip`:



1\. \*\*Easiest\*\* — drag any `.mylang` file onto `run\_mylang.bat`

2\. \*\*Command line\*\* — run `mylang.exe your\_file.mylang`



\## Syntax Examples



\### Hello world



```mylang

print("Hello, world!");

```



\### Fibonacci



```mylang

fn fib(n) {

&#x20;   if (n < 2) { return n; }

&#x20;   return fib(n - 1) + fib(n - 2);

}



for (let i = 0; i < 10; i += 1) {

&#x20;   print(fib(i));

}

```



\### Arrays and standard library



```mylang

let arr = \[5, 2, 8, 1, 9];



let sorted  = bubble\_sort(arr);

let doubled = map(sorted, fn(x) { return x \* 2; });

let total   = reduce(arr, fn(a, b) { return a + b; }, 0);



print(sorted);   // \[1, 2, 5, 8, 9]

print(doubled);  // \[2, 4, 10, 16, 18]

print(total);    // 25

```



\### Exception handling



```mylang

try {

&#x20;   let y = 1 / 0;

} catch (e) {

&#x20;   print("error: " + e);

}

```



\### File IO



```mylang

write\_file("notes.txt", "line 1\\nline 2\\nline 3");



let lines = read\_lines("notes.txt");

for (let i = 0; i < len(lines); i += 1) {

&#x20;   print(lines\[i]);

}

```



\## Built-in Functions



| Category | Functions |

|----------|-----------|

| Basics   | `print`, `input`, `len`, `str`, `num`, `int`, `type`, `abs`, `max`, `min`, `sqrt`, `range` |

| Strings  | `upper`, `lower`, `split`, `join`, `replace`, `trim`, `substr`, `find` |

| Arrays   | `push`, `pop`, `sort`, `reverse`, `contains` |

| Dicts    | `dict`, `has`, `keys`, `values`, `del` |

| Files    | `read\_file`, `write\_file`, `append\_file`, `exists` |



\## Build from Source



Requires Python 3.8+ and PyInstaller.



```bash

pip install pyinstaller

pyinstaller --onefile --name mylang --add-data "stdlib.mylang;." main.py

```



Output: `dist/mylang.exe`



\## Project Structure



```

mylang/

├── main.py             # Entry point (REPL, CLI)

├── lexer.py            # Tokenizer

├── parser.py           # Parser (produces AST)

├── ast\_nodes.py        # AST node definitions

├── interpreter.py      # Tree-walking interpreter

├── type\_checker.py     # Optional static type checker

├── errors.py           # Error formatting

├── stdlib.mylang       # Standard library, written in mylang itself

└── examples/           # Example programs

```



\## Contributing



Issues and pull requests are welcome.



\## License



\[MIT](LICENSE)



If you have any comments, you can send them to havedrink@outlook.com
Thanks
