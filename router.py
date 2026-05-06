from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from llm_client import LLMClient

ALLOWED_TEMPLATE_CODES = {"A", "B1", "B2"}


@dataclass(frozen=True)
class RouteDecision:
    selected_template: str
    route_reason: str
    fallback_needed: bool
    fallback_target: str | None


def load_cards(cards_dir: Path) -> list[dict[str, str]]:
    cards = []
    for path in sorted(cards_dir.glob("*.md")):
        cards.append(
            {
                "code": path.stem.split("_", 1)[0].upper(),
                "name": path.stem,
                "content": path.read_text(encoding="utf-8").strip(),
            }
        )
    if not cards:
        raise FileNotFoundError("no_template_cards")
    return cards


def route_theme(theme: str, cards_dir: Path, llm_client: LLMClient) -> RouteDecision:
    cards = load_cards(cards_dir)
    card_block = "\n\n".join(
        f"卡片代号：{card['code']}\n卡片文件：{card['name']}\n{card['content']}" for card in cards
    )

    messages = [
        {
            "role": "system",
            "content": (
                "你是模板路由器。请只根据主题与卡片内容选择最合适的模板代号。"
                "优先根据主题所暗示的运动语法、事件结构和空间组织方式进行判断，而不是根据字面题材联想。"
                "你必须只返回一个 JSON 对象，不要使用代码块，不要输出额外说明。"
            ),
        },
        {
            "role": "user",
            "content": (
                f"主题：{theme}\n\n"
                "可选模板代号只有：A、B1、B2。\n"
                "返回 JSON 字段必须包含：selected_template、route_reason、fallback_needed、fallback_target。\n"
                "其中 selected_template 只能是 A/B1/B2；fallback_needed 只能是 true/false；"
                "如果不需要 fallback，fallback_target 写 null。\n"
                "route_reason 必须只输出一句简短中文说明，长度控制在 20 到 50 字。\n\n"
                f"{card_block}"
            ),
        },
    ]
    raw_text = llm_client.chat(messages, temperature=0)
    data = _parse_json_object(raw_text)

    selected_template = str(data.get("selected_template", "")).strip().upper()
    if selected_template not in ALLOWED_TEMPLATE_CODES:
        raise ValueError(f"invalid_selected_template={selected_template}")

    fallback_target_raw = data.get("fallback_target")
    fallback_target = None
    if fallback_target_raw not in (None, "", "null"):
        fallback_target = str(fallback_target_raw).strip().upper()
        if fallback_target not in ALLOWED_TEMPLATE_CODES:
            fallback_target = None

    return RouteDecision(
        selected_template=selected_template,
        route_reason=str(data.get("route_reason", "")).strip(),
        fallback_needed=_to_bool(data.get("fallback_needed", False)),
        fallback_target=fallback_target,
    )


def _parse_json_object(raw_text: str) -> dict:
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        lines = [line for line in cleaned.splitlines() if not line.strip().startswith("```")]
        cleaned = "\n".join(lines).strip()

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError("route_response_not_json")

    return json.loads(cleaned[start : end + 1])


def _to_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() == "true"
    return bool(value)
