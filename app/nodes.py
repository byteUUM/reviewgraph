from .analyzer import analyze
from .llm import get_llm
from .state import ReviewState

PASS_SCORE = 0.9
MAX_ROUNDS = 2


def static_check(s: ReviewState) -> ReviewState:
    try:
        return {"findings": analyze(s["code"]), "iteration": 0}
    except SyntaxError as e:
        return {"syntax_error": f"第 {e.lineno} 行语法错误：{e.msg}", "findings": []}


def llm_review(s: ReviewState) -> ReviewState:
    it = s.get("iteration", 0)
    return {"review": get_llm()(s["code"], s["findings"], it), "iteration": it + 1}


def critic(s: ReviewState) -> ReviewState:
    """评分 = 审查意见覆盖了多少条静态检查项（按规则名 + 行号匹配）。"""
    fs = s["findings"]
    if not fs:
        return {"score": 1.0}
    hit = sum(1 for f in fs if f"第 {f['line']} 行" in s["review"] and f["rule"] in s["review"])
    return {"score": round(hit / len(fs), 2)}


def make_report(s: ReviewState) -> ReviewState:
    if s.get("syntax_error"):
        return {"report": f"无法审查：{s['syntax_error']}"}
    n = len(s["findings"])
    head = f"共 {n} 项发现，审查 {s['iteration']} 轮，覆盖率 {int(s['score'] * 100)}%。\n\n"
    return {"report": head + s["review"]}


def after_static(s: ReviewState) -> str:
    return "report" if s.get("syntax_error") else "review"


def after_critic(s: ReviewState) -> str:
    return "report" if s["score"] >= PASS_SCORE or s["iteration"] >= MAX_ROUNDS else "review"
