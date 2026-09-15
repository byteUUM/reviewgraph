from app.analyzer import analyze
from app.graph import graph

BAD = '''
def f(x, acc=[]):
    try:
        eval(x)
    except:
        pass
    if x == None:
        return acc
'''


def test_analyzer_rules():
    rules = {f["rule"] for f in analyze(BAD)}
    assert {"bare-except", "eval-exec", "mutable-default", "no-docstring", "none-compare"} <= rules


def test_loop_runs_two_rounds():
    out = graph.invoke({"code": BAD})
    assert out["iteration"] == 2 and out["score"] == 1.0


def test_syntax_error_short_circuits():
    out = graph.invoke({"code": "def ("})
    assert "语法错误" in out["report"] and "review" not in out
