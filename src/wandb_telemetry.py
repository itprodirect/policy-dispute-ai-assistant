# src/wandb_telemetry.py
"""
W&B run-level telemetry management for claim-level analysis.

Responsibilities:
- Initialize and finalize W&B runs with claim context
- Track and rollup per-run metrics (tokens, latency, calls, errors)
- Evaluate A-G report structure quality (metrics only, no raw text)
"""
from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from typing import Optional, Dict, Any

from .config import get_settings

# Optional wandb import
try:
    import wandb
    _WANDB_AVAILABLE = True
except ImportError:
    wandb = None
    _WANDB_AVAILABLE = False


# Module-level tracker instance
_run_tracker: Optional[WandbRunTracker] = None


@dataclass
class WandbRunTracker:
    """
    Accumulates metrics across all LLM calls in a single claim run.
    """
    total_tokens: int = 0
    total_latency_ms: float = 0.0
    call_count: int = 0
    error_count: int = 0

    def record_call(
        self,
        stage: Optional[str],
        latency_ms: float,
        tokens: int,
        success: bool,
    ) -> None:
        """Record metrics from a single LLM call."""
        self.call_count += 1
        self.total_latency_ms += latency_ms
        self.total_tokens += tokens
        if not success:
            self.error_count += 1


def _get_git_commit() -> str:
    """
    Get current git commit hash (short form).
    Returns 'unknown' if git is unavailable or fails.
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=2.0,
        )
        if result.returncode == 0:
            return result.stdout.strip()[:8]
    except Exception:
        pass
    return "unknown"


def start_wandb_run(
    claim_id: str,
    mode: str,
    git_commit: Optional[str] = None,
) -> None:
    """
    Initialize a W&B run with claim-level context.

    Args:
        claim_id: Unique identifier for this claim/analysis run
        mode: Run mode ("policy_only", "dispute", "demo")
        git_commit: Git commit hash (auto-detected if None)
    """
    global _run_tracker

    if not _WANDB_AVAILABLE:
        return

    settings = get_settings()
    if not settings.wandb_enabled:
        return

    if git_commit is None:
        git_commit = _get_git_commit()

    # Initialize tracker
    _run_tracker = WandbRunTracker()

    # Initialize W&B run with context
    wandb.init(
        project=settings.wandb_project,
        entity=settings.wandb_entity,
        config={
            "run/claim_id": claim_id,
            "run/mode": mode,
            "run/git_commit": git_commit,
            "run/safe_mode": settings.safe_mode,
            "run/persist_raw_text": settings.persist_raw_text,
            "run/default_model": settings.openai_model,
        },
        # Allow multiple runs in same process (for testing/batch scenarios)
        reinit=True,
    )


def get_run_tracker() -> Optional[WandbRunTracker]:
    """Get the current run tracker (if a run is active)."""
    return _run_tracker


def finish_wandb_run() -> None:
    """
    Log per-run rollups and close the W&B run.
    """
    global _run_tracker

    if not _WANDB_AVAILABLE or wandb.run is None:
        return

    if _run_tracker is not None:
        # Log rollup metrics
        wandb.log({
            "run/total_tokens": _run_tracker.total_tokens,
            "run/total_latency_ms": _run_tracker.total_latency_ms,
            "run/calls": _run_tracker.call_count,
            "run/errors": _run_tracker.error_count,
        })

    # Close the run
    wandb.finish()

    # Reset tracker
    _run_tracker = None


def _is_non_empty(value: Any) -> bool:
    """
    Check if a value is non-empty (for A-G section presence detection).

    - Strings: non-empty after stripping
    - Lists: non-empty
    - Objects with attributes: considered present
    - None: empty
    """
    if value is None:
        return False
    if isinstance(value, str):
        return len(value.strip()) > 0
    if isinstance(value, list):
        return len(value) > 0
    # Dataclass instances / dicts are considered "present"
    return True


def evaluate_ag_structure(dispute_report: Any) -> Dict[str, Any]:
    """
    Evaluate A-G report structure quality.

    Returns metrics only (NO raw text logged to W&B).

    Args:
        dispute_report: DisputeReport instance

    Returns:
        Dict with:
          - quality/ag_present_count: Number of non-empty A-G sections (0-7)
          - quality/ag_order_ok: True if all 7 sections are present
    """
    # A-G sections in order
    sections = [
        ("A", dispute_report.plain_summary),
        ("B", dispute_report.coverage_highlights),
        ("C", dispute_report.exclusions_limitations),
        ("D", dispute_report.denial_reasons),
        ("E", dispute_report.dispute_angles),
        ("F", dispute_report.missing_info),
        ("G", dispute_report.confidence),
    ]

    present_count = sum(1 for _, val in sections if _is_non_empty(val))
    order_ok = present_count == 7  # All sections present

    metrics = {
        "quality/ag_present_count": present_count,
        "quality/ag_order_ok": order_ok,
    }

    # Log to W&B if run is active
    if _WANDB_AVAILABLE and wandb.run is not None:
        wandb.log(metrics)

    return metrics
