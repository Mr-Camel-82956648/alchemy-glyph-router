from __future__ import annotations

from pathlib import Path

from generator import generate_prompt, load_full_template
from router import route_theme


class StubLLMClient:
    def __init__(self, responses: list[str]) -> None:
        self.responses = responses
        self.calls: list[list[dict[str, str]]] = []

    def chat(self, messages: list[dict[str, str]], temperature: float = 0.2) -> str:
        self.calls.append(messages)
        if not self.responses:
            raise RuntimeError("no_stub_response")
        return self.responses.pop(0)


def main() -> None:
    root_dir = Path(__file__).resolve().parent
    client = StubLLMClient(
        [
            (
                '{"selected_template":"B1","route_reason":"主题更接近区域覆盖式垂直降临打击",'
                '"fallback_needed":true,"fallback_target":"B2"}'
            ),
            (
                "乌云压城，主题“剑雨”作为核心视觉，万千寒光长剑自高空密集垂直坠落，"
                "覆盖整片古城街巷与屋脊，雨幕般连续冲击地面并激起碎石、水雾与冷色反光，"
                "镜头低角度仰拍后切入横向推进，节奏强、压迫感重、电影级奇幻战场氛围。"
            ),
        ]
    )

    route = route_theme("剑雨", root_dir / "templates" / "cards", client)
    assert route.selected_template == "B1"
    assert route.fallback_target == "B2"

    template_markdown = load_full_template(root_dir / "templates" / "full", "B2_rain_full")
    final_prompt = generate_prompt("剑雨", template_markdown, client)

    assert "剑雨" in final_prompt
    assert len(client.calls) == 2
    print("smoke_test_passed")


if __name__ == "__main__":
    main()
