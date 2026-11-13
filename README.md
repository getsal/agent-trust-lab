# agent-trust-lab

An offline-first, synthetic two-agent experiment harness for testing prompt-injection handling and tool authorization with a local Ollama server.

## Safety boundary

This repository contains only synthetic reports. `export_debug_data` is a simulated tool name and is never implemented. No network export, filesystem export, credentials, or real user data are used. The policy gate is a static Python allowlist evaluated outside the LLM output.

## Quick start

The deterministic test path needs only Python 3.10+:

```sh
./start.sh --offline
python3 -m unittest discover -s tests -v
```

The run covers both `normal_report.txt` and `injected_report.txt`, writes a comparison file under `results/latest.json`, and writes one JSONL audit log per scenario. Generated results are ignored by Git.

## Local Web UI

Start the localhost-only dashboard with the standard library:

```sh
python3 -m web.server
```

Open <http://127.0.0.1:8765>. The dashboard supports deterministic offline replay and Ollama mode, model A/B selection, editable Agent A/B prompts, normal/injected comparison, switchable Input/Agent A/Agent B diff views, side-by-side normal/attack columns, and word-level highlighting without `+`/`-` body markers. Policy decisions, parser state, raw prompts/responses, and the complete JSONL audit trail remain available. Diff highlighting is observational and does not establish causality. Runs are executed through the existing `run_case` path, so the CLI and security boundary remain unchanged. The API binds only to loopback, accepts only the two known scenarios, validates model names and prompt size, and does not read arbitrary files or execute shell commands.

The UI is dependency-free and responsive for laptop and mobile screens. It is a local research view, not a production service; stop it with Ctrl-C.

### Providers and demonstration

The Web UI discovers installed Ollama models through `/api/tags` without downloading anything. Agent A and Agent B have independent provider/model selectors. Offline replay is deterministic and simulated; Ollama uses only the local service. Cloud provider entries are shown only when credentials are configured server-side, but cloud execution remains explicitly disabled in this stable local pass. Optional credential names are documented in `.env.example`; never put values in that file or in Git.

Three-minute demonstration:

1. Run `python3 -m web.server` and open <http://127.0.0.1:8765>.
2. Leave both agents on `Offline replay`, click `Run comparison`, and inspect ALLOW for normal plus DENY for injection.
3. Switch Input Diff, Agent A Diff, and Agent B Diff; then expand the prompt/response and JSONL audit sections.
4. For a live local run, select `Ollama · local`, choose installed models, and run with synthetic reports only.

This project is for security research and education, not production authorization enforcement. Model output is untrusted; the static Policy remains the decision boundary.

## Ollama mode

Start the existing Ollama service at `http://localhost:11434`, confirm the selected models are installed, then run:

```sh
./start.sh --model-a qwen2.5:3b --model-b qwen2.5-coder:7b
```

Agent A and Agent B are separate sequential `/api/generate` requests. Temperature is fixed to zero for reproducibility. Models can be replaced with any locally available Ollama model:

```sh
ollama list
```

No Orca integration is included at this stage, and no model is downloaded by this project.

## Layout

- `run.py`: executes both cases and produces comparable JSON results. Agent B requests strict JSON with an Ollama JSON Schema when available.
- `agents/ollama.py`: minimal standard-library Ollama client with raw API response preservation.
- `security/policy.py`: independent static allowlist (`save_report` only).
- `security/audit.py`: append-only JSONL event recording.
- `scenarios/`: synthetic normal and indirect-injection reports.
- `tests/`: offline policy and audit checks.

## Interpretation

The offline path is a harness and policy test, not evidence that a particular LLM is robust. Ollama-mode outcomes depend on the installed model versions and prompts. Review `results/latest_*.jsonl` and compare `requested_tool`, `allowed`, and the model outputs. The expected security invariant is that `export_debug_data` remains denied regardless of the model's request.

Each audit log distinguishes the raw API response from parser output. `parse_status` is one of `parsed`, `explicit_none`, or `parse_error`; API/model failures are never silently converted to `none`. Parse failures fail closed and do not execute a tool.

## Not yet verified

- Whether every future Ollama/model combination honors the JSON Schema format request.
- Behavior of each chosen model under additional adversarial prompts.
- Performance, concurrency, and long-context behavior.
