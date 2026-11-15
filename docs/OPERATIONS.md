# UCA operations and validation

## Initialize and import local evidence

```bash
python -m uca init --root .
python -m uca import-documents --root . /path/to/passages.jsonl
python -m uca status --root .
```

Each JSONL input must include `doc_id`, `content`, `provenance`, and optional
`metadata`. For a French Wikipedia shard, preserve the source shard/revision in
`provenance` or `metadata`; UCA intentionally calls it a *local corpus*, never
an exhaustive encyclopedia. The initial checkout has no 206,846-passage shard,
so its passage count begins at zero.

Explicit memory has this schema and must be edited/managed by an explicit user
operation outside a chat request:

```json
{"entries":[{"id":"m-1","text":"…","tags":["…"],"explicit":true}]}
```

Entries without exactly `explicit: true` are ignored. Chat calls do not write
this file.

## UI

`python -m uca serve --root . --host 0.0.0.0 --port 8080` provides one
conversation endpoint. Normal mode shows one answer. Developer mode reveals
intermediate artifacts, sources, module availability/errors and advanced
pipeline order editing. All browser requests use relative `/api/...` URLs.

## Benchmark protocol

Create an operator-reviewed JSONL task suite then run from Python or the CLI
extension below. The harness compares `smollm2_360_alone`,
`smollm2_135_alone`, `nanodiff_compatible_only`, `uca_full`, and the historical
`legacy_current_project` slot. The latter deliberately reports
`not_executable`, as no old architecture existed in the audited repository.

Also run `uca_without_memory`, `uca_without_retrieval`, `uca_without_symbolic`,
`uca_without_ncm`, and `uca_without_nanodiff` as ablations. It records wall
time, process max-RSS delta and optional CUDA peak allocation. It leaves
factual accuracy, reasoning, maths, linguistic coherence and hallucination
metrics `null` without a validated evaluator/human labels. Do not report null
or unavailable runs as validated improvements.

Example invocation after installing the package:

```python
from uca.benchmark import load_tasks, run_benchmark
from uca.config import load_config
import json
r = run_benchmark(load_config('.'), load_tasks('benchmarks/tasks.example.jsonl'),
                  ['smollm2_360_alone','smollm2_135_alone','nanodiff_compatible_only',
                   'legacy_current_project','uca_full','uca_without_retrieval'])
print(json.dumps(r, ensure_ascii=False, indent=2))
```
