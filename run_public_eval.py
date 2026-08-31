#!/usr/bin/env python3
"""Run the organizer-provided public evaluator against this submission.

This helper stages ``agent.py`` as ``starter/agent.py`` in a temporary
working directory because the supplied local evaluator imports that module
path. It does not modify the evaluator or any dataset.

The supplied evaluator writes its complete JSON result before Python begins
interpreter cleanup. Some SQLite builds can spend a long time releasing the
large in-memory FTS5 index at process exit, so this helper treats a complete,
parseable result file as successful completion and then stops the staged
process. This behavior is only for local reproducibility; official scoring
should use the organizer's normal harness lifecycle.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def _existing_file(value: str, label: str) -> Path:
    path = Path(value).expanduser().resolve()
    if not path.is_file():
        raise SystemExit(f"{label} was not found: {path}")
    return path


def _complete_result(path: Path) -> dict | None:
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    required = {
        "sample_count",
        "hit_rate_at_10",
        "mrr",
        "mttc",
        "efficiency",
        "recommended_technical_score",
        "scenario_metrics",
        "sessions",
    }
    return payload if isinstance(payload, dict) and required.issubset(payload) else None


def _stop_process(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Stage agent.py and run the organizer-provided local evaluator."
    )
    parser.add_argument("--evaluator", required=True, help="Path to local_evaluator.py")
    parser.add_argument("--catalog", required=True, help="Path to catalog.jsonl")
    parser.add_argument("--dataset", required=True, help="Path to public_set.jsonl")
    parser.add_argument(
        "--output",
        default="public_results.json",
        help="Destination for evaluator JSON output (default: public_results.json)",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=600.0,
        help="Maximum evaluation time before termination (default: 600)",
    )
    args = parser.parse_args()
    if args.timeout_seconds <= 0:
        raise SystemExit("--timeout-seconds must be greater than zero")

    submission_dir = Path(__file__).resolve().parent
    agent_path = _existing_file(str(submission_dir / "agent.py"), "agent.py")
    evaluator_path = _existing_file(args.evaluator, "Evaluator")
    catalog_path = _existing_file(args.catalog, "Catalog")
    dataset_path = _existing_file(args.dataset, "Dataset")
    output_path = Path(args.output).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.unlink(missing_ok=True)

    with tempfile.TemporaryDirectory(prefix="techjam_eval_") as temporary:
        workdir = Path(temporary)
        starter_dir = workdir / "starter"
        starter_dir.mkdir()
        shutil.copy2(agent_path, starter_dir / "agent.py")
        (starter_dir / "__init__.py").write_text(
            '"""Staged submission package."""\n', encoding="utf-8"
        )
        staged_evaluator = workdir / "local_evaluator.py"
        shutil.copy2(evaluator_path, staged_evaluator)

        command = [
            sys.executable,
            str(staged_evaluator),
            "--catalog",
            str(catalog_path),
            "--dataset",
            str(dataset_path),
            "--output",
            str(output_path),
        ]
        process = subprocess.Popen(
            command,
            cwd=workdir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )
        deadline = time.monotonic() + args.timeout_seconds
        result: dict | None = None
        try:
            while time.monotonic() < deadline:
                result = _complete_result(output_path)
                if result is not None:
                    _stop_process(process)
                    break
                return_code = process.poll()
                if return_code is not None:
                    stderr = process.stderr.read() if process.stderr else ""
                    raise SystemExit(
                        f"Evaluator exited with status {return_code} before writing "
                        f"a complete result.\n{stderr}".rstrip()
                    )
                time.sleep(0.1)
            else:
                _stop_process(process)
                raise SystemExit(
                    f"Evaluation exceeded {args.timeout_seconds:g} seconds without "
                    "writing a complete result."
                )
        finally:
            if process.poll() is None:
                _stop_process(process)

    if result is None:
        raise SystemExit("The evaluator did not produce a complete result.")

    summary_keys = [
        "sample_count",
        "hit_rate_at_10",
        "mrr",
        "mttc",
        "efficiency",
        "recommended_technical_score",
        "reported_token_usage",
        "scenario_metrics",
    ]
    summary = {key: result.get(key) for key in summary_keys}
    print(json.dumps(summary, indent=2))
    print(f"Evaluation output written to: {output_path}")


if __name__ == "__main__":
    main()
