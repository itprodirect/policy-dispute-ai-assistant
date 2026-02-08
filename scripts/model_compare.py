#!/usr/bin/env python3
"""
Model comparison script for W&B telemetry validation.

Runs the same policy + denial fixture through multiple models and
creates separate W&B runs for comparison.

Usage:
    python -m scripts.model_compare --policy_text_fixture <path> --denial_text_fixture <path> --models gpt-4.1-mini,gpt-4.1

Requirements:
    - WANDB_ENABLED=true in .env
    - OPENAI_API_KEY set
    - Fixtures in data/processed_safe/ and data/raw_denials/
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.summarizer_frontier import build_denial_aware_report
from src.wandb_telemetry import start_wandb_run, finish_wandb_run, evaluate_ag_structure
from src.config import get_settings


DEFAULT_POLICY_FIXTURE = PROJECT_ROOT / "data/processed_safe/HO3_TRUE_FL_2021.json"
DEFAULT_DENIAL_FIXTURE = PROJECT_ROOT / "data/raw_denials/HO3_TRUE_FL_2021_denial.txt"
DEFAULT_MODELS = ["gpt-4.1-mini"]


def _parse_models(raw: str) -> List[str]:
    return [m.strip() for m in raw.split(",") if m.strip()]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run model comparison with W&B telemetry per model.",
    )
    parser.add_argument(
        "--policy_text_fixture",
        default=str(DEFAULT_POLICY_FIXTURE),
        help=(
            "Path to policy summary JSON fixture (output of summarize_policy). "
            f"Default: {DEFAULT_POLICY_FIXTURE}"
        ),
    )
    parser.add_argument(
        "--denial_text_fixture",
        default=str(DEFAULT_DENIAL_FIXTURE),
        help=(
            "Path to denial text fixture. "
            f"Default: {DEFAULT_DENIAL_FIXTURE}"
        ),
    )
    parser.add_argument(
        "--models",
        default=",".join(DEFAULT_MODELS),
        help="Comma-separated list of models to run.",
    )
    return parser.parse_args()


def run_model_comparison() -> None:
    """
    Run dispute analysis with multiple models and compare via W&B.
    """
    args = parse_args()

    policy_fixture = Path(args.policy_text_fixture)
    denial_fixture = Path(args.denial_text_fixture)
    models = _parse_models(args.models)

    if not models:
        print("[ERROR] No models provided. Use --models model_a,model_b")
        sys.exit(1)

    # Validate fixtures exist
    if not policy_fixture.exists():
        print(f"[ERROR] Policy fixture not found: {policy_fixture}")
        sys.exit(1)
    if not denial_fixture.exists():
        print(f"[ERROR] Denial fixture not found: {denial_fixture}")
        sys.exit(1)

    # Load fixtures
    policy_payload = json.loads(policy_fixture.read_text(encoding="utf-8"))
    denial_text = denial_fixture.read_text(encoding="utf-8")

    print(f"\n[MODEL COMPARISON RUNNER]")
    print(f"=" * 60)
    print(f"Policy fixture: {policy_fixture}")
    print(f"Denial fixture: {denial_fixture}")
    print(f"Models: {', '.join(models)}")
    print(f"=" * 60)

    settings = get_settings()
    if not settings.wandb_enabled:
        print("\n[WARNING] WANDB_ENABLED=false - runs will not be logged to W&B")
        print("   Set WANDB_ENABLED=true in .env to enable telemetry\n")

    results = []

    for model in models:
        print(f"\n[RUNNING] model: {model}")
        print("-" * 60)

        claim_id = f"model_compare_{model.replace('.', '_').replace('-', '_')}"

        # Start W&B run with model-specific claim_id
        start_wandb_run(
            claim_id=claim_id,
            mode="model_compare",
            default_model=model,
        )

        try:
            # Override model via environment (call_llm_json checks this)
            original_model = os.environ.get("OPENAI_MODEL")
            os.environ["OPENAI_MODEL"] = model

            try:
                # Run dispute analysis
                dispute_report = build_denial_aware_report(policy_payload, denial_text)

                # Evaluate A-G structure
                quality_metrics = evaluate_ag_structure(dispute_report)

                print(f"[SUCCESS] Completed: {model}")
                print(f"   A-G sections present: {quality_metrics['quality/ag_present_count']}/7")
                print(f"   A-G order OK: {quality_metrics['quality/ag_order_ok']}")

                results.append({
                    "model": model,
                    "success": True,
                    "quality": quality_metrics,
                })

            finally:
                # Restore original model
                if original_model is not None:
                    os.environ["OPENAI_MODEL"] = original_model
                else:
                    os.environ.pop("OPENAI_MODEL", None)

        except Exception as e:
            print(f"[FAILED] Failed: {model}")
            print(f"   Error: {e}")
            results.append({
                "model": model,
                "success": False,
                "error": str(e),
            })

        finally:
            # Always finish W&B run
            finish_wandb_run()

    # Summary
    print(f"\n{'=' * 60}")
    print(f"[SUMMARY] Model Comparison Summary")
    print(f"{'=' * 60}")

    for result in results:
        if result["success"]:
            quality = result["quality"]
            print(f"[OK] {result['model']:20s} | A-G: {quality['quality/ag_present_count']}/7 | Order: {quality['quality/ag_order_ok']}")
        else:
            print(f"[FAIL] {result['model']:20s} | Error: {result['error']}")

    if settings.wandb_enabled:
        print(f"\n[W&B] View runs in W&B: https://wandb.ai/{settings.wandb_entity}/{settings.wandb_project}")
        print(f"   Filter by tag: mode=model_compare")
    else:
        print(f"\n[TIP] Enable W&B logging: WANDB_ENABLED=true in .env")

    print()


if __name__ == "__main__":
    run_model_comparison()
