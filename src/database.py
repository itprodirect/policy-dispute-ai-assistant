# src/database.py
"""SQLite database for storing claim history."""
from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Default database path (in project data directory)
DEFAULT_DB_PATH = Path("data/claims.db")


@dataclass
class Claim:
    """Represents a saved claim analysis."""
    id: int
    nickname: str
    state: str
    policy_filename: str
    denial_filename: str
    created_at: datetime
    report_json: Dict[str, Any]


def _get_connection(db_path: Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Get a database connection, creating parent directories if needed."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Path = DEFAULT_DB_PATH) -> None:
    """Initialize the database schema."""
    conn = _get_connection(db_path)
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS claims (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nickname TEXT NOT NULL DEFAULT '',
                state TEXT NOT NULL DEFAULT '',
                policy_filename TEXT NOT NULL,
                denial_filename TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                report_json TEXT NOT NULL
            )
        """)
        conn.commit()
    finally:
        conn.close()


def save_claim(
    *,
    nickname: str,
    state: str,
    policy_filename: str,
    denial_filename: str,
    report_json: Dict[str, Any],
    db_path: Path = DEFAULT_DB_PATH,
) -> int:
    """
    Save a completed claim analysis to the database.

    Returns the ID of the newly created claim.
    """
    init_db(db_path)
    conn = _get_connection(db_path)
    try:
        cursor = conn.execute(
            """
            INSERT INTO claims (nickname, state, policy_filename, denial_filename, report_json)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                nickname,
                state,
                policy_filename,
                denial_filename,
                json.dumps(report_json, ensure_ascii=False),
            ),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_all_claims(db_path: Path = DEFAULT_DB_PATH) -> List[Claim]:
    """Retrieve all claims, most recent first."""
    init_db(db_path)
    conn = _get_connection(db_path)
    try:
        rows = conn.execute(
            """
            SELECT id, nickname, state, policy_filename, denial_filename, created_at, report_json
            FROM claims
            ORDER BY created_at DESC
            """
        ).fetchall()

        claims = []
        for row in rows:
            claims.append(Claim(
                id=row["id"],
                nickname=row["nickname"],
                state=row["state"],
                policy_filename=row["policy_filename"],
                denial_filename=row["denial_filename"],
                created_at=datetime.fromisoformat(row["created_at"]),
                report_json=json.loads(row["report_json"]),
            ))
        return claims
    finally:
        conn.close()


def get_claim_by_id(claim_id: int, db_path: Path = DEFAULT_DB_PATH) -> Optional[Claim]:
    """Retrieve a single claim by ID."""
    init_db(db_path)
    conn = _get_connection(db_path)
    try:
        row = conn.execute(
            """
            SELECT id, nickname, state, policy_filename, denial_filename, created_at, report_json
            FROM claims
            WHERE id = ?
            """,
            (claim_id,),
        ).fetchone()

        if row is None:
            return None

        return Claim(
            id=row["id"],
            nickname=row["nickname"],
            state=row["state"],
            policy_filename=row["policy_filename"],
            denial_filename=row["denial_filename"],
            created_at=datetime.fromisoformat(row["created_at"]),
            report_json=json.loads(row["report_json"]),
        )
    finally:
        conn.close()


def delete_claim(claim_id: int, db_path: Path = DEFAULT_DB_PATH) -> bool:
    """Delete a claim by ID. Returns True if a claim was deleted."""
    init_db(db_path)
    conn = _get_connection(db_path)
    try:
        cursor = conn.execute("DELETE FROM claims WHERE id = ?", (claim_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()
