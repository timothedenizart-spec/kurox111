# kurox111 — Unified Cognitive Architecture

UCA is a local, traceable orchestration framework for heterogeneous AI components. Its architecture keeps model-specific tokenizers isolated, stores outputs as provenance-bearing artifacts, separates evidence from generated proposals, and degrades honestly when models or data are unavailable. It does not claim consciousness or model-weight fusion.

## Run

```bash
python3 -m uca init --root .
python3 -m uca status --root .
python3 -m uca chat --root . "Bonjour"
python3 -m unittest discover -s tests -v
```

Optional local web conversation: `python3 -m uca serve --root . --host 0.0.0.0 --port 8080`.

## Shared agent workspace and file drop

Run `./coordination/shared-workspace/start.sh` (Windows: `coordination/shared-workspace/start.bat`). It starts the server and opens the dashboard automatically; the dashboard loads the inventory of files already in the inbox and refreshes it after uploads. It accepts files and folders of any type, retains folder structure, and transfers in chunks. File contents are stored locally under `coordination/shared-workspace/inbox/`, intentionally ignored by Git; uploading does not automatically replicate them to other agent sessions or feed them into a model. See [workspace instructions](coordination/shared-workspace/README.md) and [multi-agent roadmap](coordination/shared-workspace/ROADMAP.md).

Coordination channel: [GitHub issue #1](https://github.com/timothedenizart-spec/kurox111/issues/1).

## Principles

- Local-only assets by default; no automatic model or corpus downloads.
- A missing fact or retrieval hit means “unknown”, never “false”.
- Model-generated content remains a proposal until independently grounded.
- Human-inspired architecture is treated as an engineering hypothesis, not evidence of intelligence or consciousness.
- Every claimed improvement must pass preregistered evaluations against a baseline and ablations.

See `docs/` for system contracts and the [multi-agent roadmap](coordination/shared-workspace/ROADMAP.md) for the proposed architecture/experiments. The optional NCM response-refinement stage is documented in [NCM integration](docs/INTEGRATION.md) and remains disabled until a runner is validated. The [training plan](coordination/training/PLAN.md) explains the data/checkpoint gates; no training has been started without verified assets.
