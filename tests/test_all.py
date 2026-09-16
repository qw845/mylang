import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import run_source


def capture(source):
    import io
    from contextlib import redirect_stdout
    buf = io.StringIO()
    with redirect_stdout(buf):
        run_source(source)
    return buf.getvalue().strip()


def test_arith():
    assert capture("print(1 + 2 * 3);") == "7"

def test_string_concat():
    assert capture('print("a" + "b");') == "ab"

def test_if():
    assert capture("if (1 < 2) { print(1); } else { print(2); }") == "1"

def test_while():
    assert capture("let i = 0; while (i < 3) { print(i); i += 1; }") == "0\n1\n2"

def test_func():
    assert capture("fn add(a,b){return a+b;} print(add(3,4));") == "7"

def test_recursion():
    src = "fn fib(n){ if(n<2){return n;} return fib(n-1)+fib(n-2);} print(fib(10));"
    assert capture(src) == "55"

def test_array():
    assert capture("let a=[1,2,3]; print(a[1]);") == "2"

def test_closure():
    src = """
    fn counter() {
        let n = 0;
        fn inc() { n += 1; return n; }
        return inc;
    }
    let c = counter();
    print(c()); print(c()); print(c());
    """
    assert capture(src) == "1\n2\n3"

def test_break_continue():
    src = """
    let i = 0;
    while (i < 10) {
        i += 1;
        if (i == 3) { continue; }
        if (i == 6) { break; }
        print(i);
    }
    """
    assert capture(src) == "1\n2\n4\n5"


if __name__ == '__main__':
    import traceback
    passed = 0
    failed = 0
    for name, fn in list(globals().items()):
        if name.startswith('test_') and callable(fn):
            try:
                fn()
                print(f"✓ {name}")
                passed += 1
            except Exception:
                print(f"✗ {name}")
                traceback.print_exc()
                failed += 1
    print(f"\n{passed} passed, {failed} failed")