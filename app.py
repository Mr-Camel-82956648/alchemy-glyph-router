from __future__ import annotations

import argparse
import json
import logging
import re
import sys
import time
from datetime import datetime
from pathlib import Path

from config import load_settings
from generator import generate_prompt, load_full_template
from llm_client import LLMClient
from router import route_theme

FULL_TEMPLATE_MAP = {
    "A": "A_container_full",
    "B1": "B1_fallback_full",
    "B2": "B2_rain_full",
    "C": "C_eruption_full",
    "D": "D_trail_full",
    "E": "E_burst_full",
    "F": "F_manifest_full",
}


def main() -> int:
    args = _parse_args()

    try:
        settings = load_settings()
        setup_logging(settings.logs_dir, settings.log_level)
        settings.outputs_dir.mkdir(parents=True, exist_ok=True)

        client = LLMClient(settings)
        started_at_dt = datetime.now().astimezone()
        started_at = started_at_dt.strftime("%Y-%m-%d %H:%M:%S")
        total_started = time.perf_counter()

        logging.info("started_at=%s", started_at)
        logging.info("theme=%s", args.theme)

        route_started = time.perf_counter()
        route = route_theme(args.theme, settings.cards_dir, client)
        route_elapsed_ms = _elapsed_ms(route_started)

        fallback_applied = False
        final_route_code = route.selected_template
        final_template = FULL_TEMPLATE_MAP.get(final_route_code)
        if not final_template and route.fallback_needed and route.fallback_target:
            final_route_code = route.fallback_target
            final_template = FULL_TEMPLATE_MAP.get(final_route_code)
            fallback_applied = bool(final_template)
        if not final_template:
            raise ValueError(f"missing_full_template_mapping={final_route_code}")

        logging.info("route_selected=%s", route.selected_template)
        logging.info("route_reason=%s", route.route_reason)
        logging.info("fallback_applied=%s", str(fallback_applied).lower())
        logging.info("route_elapsed_ms=%s", route_elapsed_ms)
        logging.info("final_template=%s", final_template)

        generation_started = time.perf_counter()
        template_markdown = load_full_template(settings.full_templates_dir, final_template)
        final_prompt = generate_prompt(args.theme, template_markdown, client)
        generation_elapsed_ms = _elapsed_ms(generation_started)
        total_elapsed_ms = _elapsed_ms(total_started)

        logging.info("generation_elapsed_ms=%s", generation_elapsed_ms)
        logging.info("total_elapsed_ms=%s", total_elapsed_ms)
        logging.info("model=%s", settings.model)

        payload = {
            "theme": args.theme,
            "route_selected": route.selected_template,
            "route_reason": route.route_reason,
            "fallback_applied": fallback_applied,
            "final_template": final_template,
            "model": settings.model,
            "final_prompt": final_prompt,
            "created_at": datetime.now().astimezone().isoformat(),
            "started_at": started_at,
            "route_elapsed_ms": route_elapsed_ms,
            "generation_elapsed_ms": generation_elapsed_ms,
            "total_elapsed_ms": total_elapsed_ms,
        }
        output_path = save_output(payload, settings.outputs_dir, args.theme)
        logging.info("output=%s", output_path.relative_to(settings.root_dir).as_posix())
        return 0
    except Exception as exc:
        logging.error("run_failed=%s", exc)
        return 1


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--theme", required=True, help="输入主题词或短语")
    return parser.parse_args()


def setup_logging(logs_dir: Path, log_level: str) -> Path:
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_path = logs_dir / "app.log"

    formatter = logging.Formatter("[%(levelname)s] %(message)s")
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(getattr(logging, log_level, logging.INFO))

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)

    root_logger.addHandler(stream_handler)
    root_logger.addHandler(file_handler)
    return log_path


def save_output(payload: dict, outputs_dir: Path, theme: str) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    theme_slug = _slugify_theme(theme)
    file_name = f"{timestamp}_{theme_slug}.json" if theme_slug else f"{timestamp}.json"
    output_path = outputs_dir / file_name
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return output_path


def _slugify_theme(theme: str) -> str:
    slug = re.sub(r"[^\w\u4e00-\u9fff-]+", "_", theme.strip())
    return slug.strip("_")[:40]


def _elapsed_ms(started_at: float) -> int:
    return int((time.perf_counter() - started_at) * 1000)


if __name__ == "__main__":
    raise SystemExit(main())
