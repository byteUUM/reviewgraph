"""基于 ast 的静态检查，纯标准库，不依赖模型。"""
import ast

SEV = {"high": 3, "medium": 2, "low": 1}


def analyze(code: str) -> list[dict]:
    tree = ast.parse(code)
    out = []
    add = lambda n, sev, rule, msg: out.append(
        {"line": getattr(n, "lineno", 0), "severity": sev, "rule": rule, "msg": msg})

    for n in ast.walk(tree):
        if isinstance(n, ast.ExceptHandler) and n.type is None:
            add(n, "high", "bare-except", "裸 except 会吞掉 KeyboardInterrupt 等异常，请指定异常类型")
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in ("eval", "exec"):
            add(n, "high", "eval-exec", f"{n.func.id}() 存在代码注入风险")
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for d in n.args.defaults + n.args.kw_defaults:
                if isinstance(d, (ast.List, ast.Dict, ast.Set)):
                    add(n, "medium", "mutable-default", f"函数 {n.name} 使用了可变默认参数")
            if not ast.get_docstring(n):
                add(n, "low", "no-docstring", f"函数 {n.name} 缺少文档字符串")
            if (getattr(n, "end_lineno", n.lineno) - n.lineno) > 40:
                add(n, "medium", "long-function", f"函数 {n.name} 超过 40 行，建议拆分")
        if isinstance(n, ast.Compare) and any(isinstance(o, (ast.Eq, ast.NotEq)) for o in n.ops):
            if any(isinstance(c, ast.Constant) and c.value is None for c in n.comparators):
                add(n, "low", "none-compare", "与 None 比较应使用 is / is not")
        if isinstance(n, ast.ImportFrom) and any(a.name == "*" for a in n.names):
            add(n, "medium", "star-import", "避免 from x import *")
    return sorted(out, key=lambda f: (-SEV[f["severity"]], f["line"]))
