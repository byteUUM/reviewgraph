from app.analyzer import analyze

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
