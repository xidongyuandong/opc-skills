#!/usr/bin/env python3
"""Regression eval for kg-code query behavior."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
HELPER = ROOT / "kg_code.py"


CASES = [
    {
        "name": "apr_rl_train_shell",
        "repo": "rllm",
        "query": "哪个 shell 文件是对 APR 进行强化训练脚本",
        "expected_any": ["examples/apr/train_smolagents_prod.sh"],
        "top_k": 3,
    },
    {
        "name": "apr_sft_train_shell",
        "repo": "rllm",
        "query": "哪个 shell 文件是对 APR 进行 SFT 训练脚本",
        "expected_any": [
            "examples/sft/test_sft_development-space.sh",
            "examples/sft/train_code_sft_lpai_full_parameter.sh",
        ],
        "top_k": 5,
    },
    {
        "name": "apr_qwen36_eval_shell",
        "repo": "cov-evalution-qwen3_6",
        "query": "哪个 shell 文件是对 APR qwen3.6 进行评测脚本",
        "expected_any": [
            "agent/shells/task052101_run_batch.sh",
            "agent/shells/run_qwen3_6_agent_eval.sh",
        ],
        "top_k": 5,
    },
    {
        "name": "c250_code_complete_uv_config",
        "repo": "code-complete-c250",
        "query": "codebuddy ai_agents pyproject uv index python mirror",
        "expected_any": ["codebuddy/ai_agents/pyproject.toml"],
        "top_k": 5,
    },
    {
        "name": "lpai_rllm_sft_shell",
        "repo": "rllm-lpai-dev",
        "query": "APR SFT full parameter shell",
        "expected_any": ["examples/sft/train_code_sft_lpai_full_parameter.sh"],
        "top_k": 8,
    },
]


def run_case(case: dict) -> dict:
    cmd = [
        sys.executable,
        str(HELPER),
        "query",
        "--repo",
        case["repo"],
        case["query"],
        "--limit",
        str(max(case["top_k"], 8)),
        "--json",
    ]
    proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if proc.returncode not in (0, 2):
        return {"name": case["name"], "status": "error", "output": proc.stdout[-1200:]}
    payload = json.loads(proc.stdout)
    top = payload.get("results", [])[: case["top_k"]]
    paths = [str(item.get("file_path") or "") for item in top]
    matched = [expected for expected in case["expected_any"] if any(expected in path for path in paths)]
    return {
        "name": case["name"],
        "status": "pass" if matched else "fail",
        "repo": case["repo"],
        "query": case["query"],
        "expected_any": case["expected_any"],
        "matched": matched,
        "top_paths": paths,
    }


def main() -> int:
    results = [run_case(case) for case in CASES]
    passed = sum(1 for item in results if item["status"] == "pass")
    summary = {"passed": passed, "total": len(results), "results": results}
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
