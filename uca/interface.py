"""Build a single-file, auto-opening UCA interface (chantier UCA-12).

One command produces ONE html file:

    python -m uca interface            # writes interface/uca.html and opens it

Design contract:

- **Everything loads with the file**: the live engine status (module states,
  parallel levels), a measured model summary when present, the versioned
  cognitive-contract report, and real demo answers computed at build time are
  embedded as `window.UCA_BOOT`. No CDN, font, script or stylesheet is fetched:
  the file works from a double-click on `file://`.
- **Honest about what is live**: offline, the chat composer is disabled with an
  explicit notice (a static file cannot run the Python engine; we do not fake
  it). When the page happens to be served by `python -m uca serve`, the chat
  activates against the real API automatically (same-origin `/api/...`).
- **Still genuinely useful offline**: an exact rational-arithmetic console
  (BigInt fractions, a faithful browser port of the server-side kernel) runs
  real computation in the page — never a simulation of model outputs.

The page template lives in `uca/interface_page.html`; the only injected token
is `window.UCA_BOOT = <json>;`.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json
import webbrowser

from .config import load_config
from .factory import build_engine

TEMPLATE = Path(__file__).resolve().parent / "interface_page.html"
DEMO_PROMPTS = ("calcule 22/7 + 3", "Que contient le corpus local à cette heure ?")


def collect_boot_payload(root: str | Path, config_path: str | Path | None = None,
                         demo_prompts: tuple[str, ...] = DEMO_PROMPTS) -> dict[str, Any]:
    """Real data captured at build time; nothing is simulated."""
    root = Path(root)
    cfg = load_config(root, config_path)
    engine = build_engine(root, cfg)
    demo_answers: list[dict[str, str]] = []
    for prompt in demo_prompts:
        try:
            context = engine.process(prompt)
            answer = context.final_response or ""
        except Exception as error:  # degraded honesty, even at build time
            answer = f"Erreur de construction: {type(error).__name__}: {str(error)[:200]}"
        demo_answers.append({"prompt": prompt, "answer": answer})
    model_metrics: dict[str, Any] | None = None
    metrics_path = root / "models" / "micro-denoiser" / "metrics.json"
    if metrics_path.exists():
        try:
            model_metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            model_metrics = None
    eval_summary: dict[str, Any] | None = None
    results_dir = root / "coordination" / "shared-workspace" / "results"
    if results_dir.is_dir():
        reports = sorted(results_dir.glob("UCA-05b-cognitive-eval-*.json"))
        if reports:
            try:
                report = json.loads(reports[-1].read_text(encoding="utf-8"))
                eval_summary = {"file": reports[-1].name, "summary": report.get("summary"),
                                "case_ids": [case["id"] for case in report.get("cases", [])]}
            except (OSError, json.JSONDecodeError):
                eval_summary = None
    return {"generated_at": datetime.now(timezone.utc).isoformat(),
            "status": engine.status(),
            "demo_answers": demo_answers,
            "model_metrics": model_metrics,
            "cognitive_eval": eval_summary}


def render_page(payload: dict[str, Any]) -> str:
    template = TEMPLATE.read_text(encoding="utf-8")
    marker = "window.UCA_BOOT = null;"
    if marker not in template:
        raise RuntimeError("Interface template marker missing")
    boot = "window.UCA_BOOT = " + json.dumps(payload, ensure_ascii=False) + ";"
    return template.replace(marker, boot)


def build_interface(root: str | Path = ".", output: str | Path = "interface/uca.html", *,
                    config_path: str | Path | None = None, open_browser: bool = True) -> dict[str, Any]:
    payload = collect_boot_payload(root, config_path)
    html = render_page(payload)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding="utf-8")
    opened = False
    if open_browser:
        try:
            opened = bool(webbrowser.open(output.resolve().as_uri()))
        except Exception:
            opened = False
    return {"output": str(output), "opened_in_browser": opened,
            "bytes": len(html.encode("utf-8")), "generated_at": payload["generated_at"]}
