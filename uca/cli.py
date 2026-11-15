"""Command line entry point for local UCA administration."""
from __future__ import annotations

import argparse
from pathlib import Path
import json
import sys
from typing import Any

from .benchmark import load_tasks, run_benchmark
from .config import load_config, local_path
from .factory import build_engine
from .model_adapters import MaskedNanoDiffAdapter
from .nanodiff_validation import load_cases, validate_masked_denoiser
from .storage import import_documents, initialize_knowledge_db
from .web import UcaWebApplication, serve


def cmd_init(args: argparse.Namespace) -> int:
    cfg = load_config(args.root)
    memory = local_path(cfg, cfg["stores"]["memory_path"])
    memory.parent.mkdir(parents=True, exist_ok=True)
    if not memory.exists():
        memory.write_text(json.dumps({"schema": "uca.explicit-memory.v1", "entries": []}, indent=2), encoding="utf-8")
    facts = local_path(cfg, cfg["stores"]["facts_path"])
    if not facts.exists():
        facts.write_text(json.dumps({"schema": "uca.operator-facts.v1", "facts": [],
                                     "note": "Empty by design: import only actual operator facts."}, indent=2), encoding="utf-8")
    initialize_knowledge_db(local_path(cfg, cfg["stores"]["knowledge_db"]), cfg["stores"].get("knowledge_table", "documents"))
    print("Initialized empty local UCA stores. No model, fact, or Wikipedia data was downloaded.")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    print(json.dumps(build_engine(args.root).status(), ensure_ascii=False, indent=2))
    return 0


def cmd_chat(args: argparse.Namespace) -> int:
    context = build_engine(args.root).process(args.message)
    print(json.dumps(context.to_dict(developer=args.developer), ensure_ascii=False, indent=2) if args.developer else context.final_response)
    return 0


def cmd_import_documents(args: argparse.Namespace) -> int:
    cfg = load_config(args.root)
    source = Path(args.file)
    records: list[dict[str, Any]] = []
    with source.open(encoding="utf-8") as handle:
        for number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError as error:
                raise SystemExit(f"Invalid JSONL at line {number}: {error}")
            if not isinstance(item, dict):
                raise SystemExit(f"JSONL line {number} is not an object")
            records.append(item)
    inserted = import_documents(local_path(cfg, cfg["stores"]["knowledge_db"]), records,
                                cfg["stores"].get("knowledge_table", "documents"))
    print(f"Imported {inserted} local passages. Provenance is preserved per record.")
    return 0


def cmd_validate_nanodiff(args: argparse.Namespace) -> int:
    cfg = load_config(args.root)
    report = validate_masked_denoiser(MaskedNanoDiffAdapter(cfg["models"]["nanodiff"], cfg), load_cases(args.cases),
                                      timeout=float(args.timeout), min_mean_delta=float(args.min_mean_delta))
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(rendered + "\n", encoding="utf-8")
        print(f"nanoDiff calibration report written to {args.output}")
    else:
        print(rendered)
    return 0 if report["status"] == "executed" else 2


def cmd_benchmark(args: argparse.Namespace) -> int:
    cfg = load_config(args.root)
    variants = [item.strip() for item in args.variants.split(",") if item.strip()]
    report = run_benchmark(cfg, load_tasks(args.tasks), variants)
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(rendered + "\n", encoding="utf-8")
        print(f"Benchmark report written to {args.output}")
    else:
        print(rendered)
    return 0


def cmd_serve(args: argparse.Namespace) -> int:
    server = serve(UcaWebApplication(build_engine(args.root)), args.host, args.port)
    print(f"UCA conversation UI listening on http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


def main(argv: list[str] | None = None) -> int:
    # Accept --root before or after a subcommand, matching the documented CLI.
    arguments = list(sys.argv[1:] if argv is None else argv)
    if "--root" in arguments:
        index = arguments.index("--root")
        if index and index + 1 < len(arguments):
            root_pair = arguments[index:index + 2]
            arguments = root_pair + arguments[:index] + arguments[index + 2:]
    parser = argparse.ArgumentParser(prog="uca", description="Unified Cognitive Architecture (local only)")
    parser.add_argument("--root", default=".", help="Repository / local asset root")
    commands = parser.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init", help="Create empty explicit local stores")
    init.set_defaults(func=cmd_init)
    status = commands.add_parser("status", help="Show availability and pipeline status")
    status.set_defaults(func=cmd_status)
    chat = commands.add_parser("chat", help="Execute one UCA request")
    chat.add_argument("message")
    chat.add_argument("--developer", action="store_true")
    chat.set_defaults(func=cmd_chat)
    importer = commands.add_parser("import-documents", help="Import operator-supplied JSONL into SQLite FTS5")
    importer.add_argument("file")
    importer.set_defaults(func=cmd_import_documents)
    calibration = commands.add_parser("validate-nanodiff", help="Compare masked-denoiser strategies against curated references")
    calibration.add_argument("cases", help="JSONL cases with text and reference")
    calibration.add_argument("--timeout", type=float, default=45)
    calibration.add_argument("--min-mean-delta", type=float, default=0.01)
    calibration.add_argument("--output", help="Optional JSON report path")
    calibration.set_defaults(func=cmd_validate_nanodiff)
    benchmark = commands.add_parser("benchmark", help="Run reproducible variants; unavailable assets remain explicit")
    benchmark.add_argument("tasks", help="Operator-reviewed JSONL task set")
    benchmark.add_argument("--variants", default="smollm2_360_alone,smollm2_135_alone,nanodiff_compatible_only,legacy_current_project,uca_full,uca_without_memory,uca_without_retrieval,uca_without_symbolic,uca_without_ncm,uca_without_nanodiff")
    benchmark.add_argument("--output", help="Optional JSON report path")
    benchmark.set_defaults(func=cmd_benchmark)
    web = commands.add_parser("serve", help="Run the single local conversation UI")
    web.add_argument("--host", default="0.0.0.0")
    web.add_argument("--port", default=8080, type=int)
    web.set_defaults(func=cmd_serve)
    args = parser.parse_args(arguments)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
