# Local integration contracts

UCA intentionally does not download projects, weights, corpora or packages.
Point `config/uca.toml` at operator-owned local assets only.

## SmolLM2

Set `models.smollm2_135.path` and/or `models.smollm2_360.path` to a local,
complete Hugging Face-compatible checkpoint directory and install the optional
local dependencies:

```bash
pip install -e '.[models]'
```

The adapter calls `AutoTokenizer.from_pretrained(path, local_files_only=True)`
and `AutoModelForCausalLM.from_pretrained(path, local_files_only=True)` for the
**same** path. It decodes generated text before putting it in UCA. It never
passes token IDs or embeddings to another model. It uses no remote code.

## MeTTa / Hyperon

Set `metta.runner_command` to an executable command for an operator-owned shim.
It receives one JSON object on stdin:

```json
{"operation":"metta_query","query":"...","context":{"document_ids":[]},"contract_version":1}
```

It must print one JSON object, with a `facts` list. A fact may contain `id`,
`statement`, `subject`, `predicate`, `object`, `metadata`, `confidence`, and
`uncertainty`. No returned fact means *inconclusive*, not false. This explicit
shim is used because neither a MeTTa installation nor its program was in the
starting repository and CLI grammar/version must not be guessed.

If `data/operator_facts.json` contains actual imported facts but no MeTTa
runner is configured, UCA performs a plainly labeled **explicit fact-index
lookup**. It does not infer relations or call that fallback MeTTa. This makes a
provided 50-fact base usable without misrepresenting its reasoning capability.

## NCM LM1B / VQ

Enable only after a checkpoint-specific shim is tested. It receives
`operation: concept_generation` and must output `{"proposals":[{"text":"…"}]}`.
Set both `enabled = true` and `validated = true`. UCA marks all results
`NON_VERIFIE` forever unless a distinct symbolic/documentary process supports
an assertion; it never promotes them itself.

## nanoDiff-50m-sft-alpaca (masked denoiser)

This is deliberately not wired as a causal transformer. Its runner receives:

```json
{"operation":"masked_denoise","architecture":"nanodiff_masked_denoiser","token_ids":[...],"masked_token_ids":[...],"mask_positions":[...],"mask_token_id":123}
```

and must return `{"candidate_token_ids":[...],"candidate_score":0.0,
"calibration_id":"..."}`. Configure the actual nanoDiff tokenizer path and a
real mask token ID; GPT-2 tokenizers do not supply one implicitly. Candidates
remain proposals, never automatic replacements. Before activation, run:

```bash
python -m uca validate-nanodiff benchmarks/nanodiff-calibration.example.jsonl --root . --output nanodiff-report.json
```

This uses each configured masking strategy and compares its output with
operator-curated references via a transparent string-similarity proxy. It runs
while `validated=false`, but **cannot** activate the module itself. Inspect the
case-level report plus human factual/coherence labels before setting
`validated=true`; no positive result is shipped.

## LoRA, TIES, DARE, AoE, FLA, E2E, Scallop

These appear in the central administrative registry. LoRA/TIES/DARE require a
compatibility manifest naming exactly `SmolLM2-360M-Instruct`, a local base
fingerprint and `validated: true`; even then UCA reports non-validated because
no merge backend was supplied by the starting repository. AoE rejects anything
but real shape/dtype/architecture-compatible expert metadata. FLA and E2E/JAX
remain non-validated pending their dependencies and checkpoints. Scallop is a
future unavailable interface, not a bundled dependency.
