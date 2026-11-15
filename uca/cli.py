"""Command line entry point for local UCA administration."""
from __future__ import annotations

import argparse
from pathlib import Path
import json
import sys
from typing import Any

from .benchmark import load_tasks, run_benchmark
from .config import load_config, local_path
from .consolidation import consolidate
from .eval_cognition import load_eval_cases, run_evaluation
from .factory import build_engine
from .interface import build_interface
from .microtrain import make_calibration_cases, run_training
from .probes import run_all_probes
from .model_adapters import MaskedNanoDiffAdapter
from .nanodiff_validation import load_cases, validate_masked_denoiser
from .storage import import_documents, initialize_knowledge_db
from .web import UcaWebApplication, serve


def cmd_init(args: argparse.Namespace) -> int:
    cfg = load_config(args.root, getattr(args, "config", None))
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
    cfg = load_config(args.root, getattr(args, "config", None))
    print(json.dumps(build_engine(args.root, cfg).status(), ensure_ascii=False, indent=2))
    return 0


def cmd_chat(args: argparse.Namespace) -> int:
    cfg = load_config(args.root, getattr(args, "config", None))
    context = build_engine(args.root, cfg).process(args.message)
    print(json.dumps(context.to_dict(developer=args.developer), ensure_ascii=False, indent=2) if args.developer else context.final_response)
    return 0


def cmd_import_documents(args: argparse.Namespace) -> int:
    cfg = load_config(args.root, getattr(args, "config", None))
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
    cfg = load_config(args.root, getattr(args, "config", None))
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


def cmd_eval_cognitive(args: argparse.Namespace) -> int:
    load_config(args.root, getattr(args, "config", None))  # validates root/config early
    report = run_evaluation(load_eval_cases(args.cases))
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(rendered + "\n", encoding="utf-8")
        print(f"Cognitive evaluation report written to {args.output}")
    else:
        print(rendered)
    summary = report["summary"]
    print(f"Cognitive contracts: {summary['passed']}/{summary['total']} case(s) passed.")
    return 0 if summary["failed"] == 0 else 2


def cmd_microtrain(args: argparse.Namespace) -> int:
    metrics = run_training(args.root, args.out, dim=args.dim, window=args.window,
                           epochs=args.epochs, seed=args.seed, extra_corpus=args.extra_corpus)
    if args.calibration_jsonl:
        from .microtrain import MicroTokenizer, load_corpus_sentences
        sentences, _ = load_corpus_sentences(args.root, args.extra_corpus)
        cases = make_calibration_cases(sentences, MicroTokenizer.load(args.out))
        destination = Path(args.calibration_jsonl)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("w", encoding="utf-8") as handle:
            for case in cases:
                handle.write(json.dumps(case, ensure_ascii=False) + "\n")
        print(f"{len(cases)} calibration case(s) written to {destination}")
    print(json.dumps(metrics, ensure_ascii=False, indent=2))
    return 0


def cmd_interface(args: argparse.Namespace) -> int:
    result = build_interface(args.root, args.output, config_path=getattr(args, "config", None),
                             open_browser=not args.no_open)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result["opened_in_browser"]:
        print(f"Ouverture automatique impossible ici (pas d'écran ?) — ouvrez manuellement : {result['output']}")
    return 0


def cmd_probes(args: argparse.Namespace) -> int:
    report = run_all_probes()
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(rendered + "\n", encoding="utf-8")
        print(f"Probe-lab report written to {args.output}")
    else:
        print(rendered)
    weak = report["summary"]["a_ameliorer"]
    print(f"Probes: {report['summary']['solide']}/{report['summary']['total']} solides"
          + (f" — à améliorer: {', '.join(weak)}" if weak else ""))
    return 0


def cmd_consolidate(args: argparse.Namespace) -> int:
    cfg = load_config(args.root, getattr(args, "config", None))
    stores = cfg["stores"]
    report = consolidate(local_path(cfg, stores["facts_path"]),
                         local_path(cfg, stores["knowledge_db"]),
                         stores.get("knowledge_table", "documents"),
                         local_path(cfg, stores.get("associations_path", "data/associations.json")))
    print(json.dumps({"consolidation_id": report["consolidation_id"],
                      "edges": len(report["edges"]),
                      "sources": report["sources"],
                      "notice": report["epistemic_notice"]}, ensure_ascii=False, indent=2))
    return 0


def cmd_serve(args: argparse.Namespace) -> int:
    cfg = load_config(args.root, getattr(args, "config", None))
    server = serve(UcaWebApplication(build_engine(args.root, cfg)), args.host, args.port)
    print(f"UCA conversation UI listening on http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


def main(argv: list[str] | None = None) -> int:
    # Accept --root/--config before or after a subcommand, matching the documented CLI.
    arguments = list(sys.argv[1:] if argv is None else argv)
    for flag in ("--root", "--config"):
        if flag in arguments:
            index = arguments.index(flag)
            if index and index + 1 < len(arguments):
                pair = arguments[index:index + 2]
                arguments = pair + arguments[:index] + arguments[index + 2:]
    parser = argparse.ArgumentParser(prog="uca", description="Unified Cognitive Architecture (local only)")
    parser.add_argument("--root", default=".", help="Repository / local asset root")
    parser.add_argument("--config", default=None, help="Optional TOML config path (default: <root>/config/uca.toml)")
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
    consolidation = commands.add_parser("consolidate", help="Offline Hebbian consolidation over local stores")
    consolidation.set_defaults(func=cmd_consolidate)
    evaluation = commands.add_parser("eval-cognitive", help="Deterministic behavioral-contract checks (UCA-05b)")
    evaluation.add_argument("cases", help="Annotated JSONL case file with fixtures and checks")
    evaluation.add_argument("--output", help="Optional JSON report path")
    evaluation.set_defaults(func=cmd_eval_cognitive)
    trainer = commands.add_parser("microtrain", help="Train the local micro masked-denoiser (numpy, no download)")
    trainer.add_argument("--out", default="models/micro-denoiser", help="Output directory (gitignored)")
    trainer.add_argument("--dim", type=int, default=32)
    trainer.add_argument("--window", type=int, default=4)
    trainer.add_argument("--epochs", type=int, default=40)
    trainer.add_argument("--seed", type=int, default=42)
    trainer.add_argument("--extra-corpus", action="append", default=[],
                         help="Optional operator-provided text file (repeatable)")
    trainer.add_argument("--calibration-jsonl", default=None,
                         help="Also write corruption-based denoising cases to this JSONL path")
    trainer.set_defaults(func=cmd_microtrain)
    interface = commands.add_parser("interface", help="Build the single-file auto-opening UCA interface")
    interface.add_argument("--output", default="interface/uca.html", help="Target HTML file")
    interface.add_argument("--no-open", action="store_true", help="Do not auto-open the browser")
    interface.set_defaults(func=cmd_interface)
    probes = commands.add_parser("probes", help="Run the measured probe lab to identify improvements")
    probes.add_argument("--output", help="Optional JSON report path")
    probes.set_defaults(func=cmd_probes)
    web = commands.add_parser("serve", help="Run the single local conversation UI")
    web.add_argument("--host", default="0.0.0.0")
    web.add_argument("--port", default=8080, type=int)
    web.set_defaults(func=cmd_serve)
    args = parser.parse_args(arguments)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
