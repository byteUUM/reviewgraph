"""LLM 适配：配置了 OPENAI_API_KEY 就用真实模型，否则用离线模拟模型。"""
import os
from typing import Callable

LLM = Callable[[str, list[dict], int], str]


def offline_llm(code: str, findings: list[dict], round_: int) -> str:
    # 第一轮只覆盖高/中风险，第二轮补全——用来演示 critic → 重写 的循环
    picked = [f for f in findings if round_ > 0 or f["severity"] != "low"]
    if not picked:
        return "未发现明显问题，代码风格良好。"
    lines = [f"- 第 {f['line']} 行 [{f['rule']}]：{f['msg']}" for f in picked]
    return "审查意见：\n" + "\n".join(lines)


def openai_llm(code: str, findings: list[dict], round_: int) -> str:
    from langchain_openai import ChatOpenAI
    model = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                       base_url=os.getenv("OPENAI_BASE_URL") or None, temperature=0.2)
    hint = "\n".join(f"{f['line']}:{f['rule']}:{f['msg']}" for f in findings)
    prompt = (f"你是资深 Python 审查员。结合静态检查结果审查下面代码，逐条给出带行号的中文意见，"
              f"每条格式为“第 N 行 [规则名]：说明”，必须覆盖全部检查项。"
              f"{'这是第二轮，请补全遗漏。' if round_ else ''}\n"
              f"静态检查：\n{hint}\n\n代码：\n{code}")
    return model.invoke(prompt).content


def get_llm() -> LLM:
    return openai_llm if os.getenv("OPENAI_API_KEY") else offline_llm
