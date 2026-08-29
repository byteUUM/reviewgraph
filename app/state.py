from typing import TypedDict


class ReviewState(TypedDict, total=False):
    code: str
    findings: list[dict]   # {line, severity, rule, msg}
    review: str
    score: float           # critic 打分 0~1
    iteration: int
    syntax_error: str
    report: str
