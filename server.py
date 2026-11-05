import sqlite3
from datetime import date, timedelta
from pathlib import Path

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

mcp = MCPServer("Placement Tracker")

DB_PATH = Path(__file__).parent / "applications.db"

STATUSES = ["applied", "oa", "interview", "offer", "rejected"]


def db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    conn.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            role TEXT NOT NULL,
            status TEXT NOT NULL,
            applied_on TEXT NOT NULL,
            notes TEXT DEFAULT ''
        )
    """)

    return conn

@mcp.tool()
def add_application(company: str, role: str, notes: str = "") -> str:
    """
    Save a new job/internship application.
    Status starts as 'applied'.
    """

    with db() as conn:
        cur = conn.execute(
            """
            INSERT INTO applications
            (company, role, status, applied_on, notes)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                company,
                role,
                "applied",
                date.today().isoformat(),
                notes
            )
        )

    return f"Saved: {company} - {role} (id {cur.lastrowid})"

    
@mcp.tool()
def update_status(app_id: int, status: str, notes: str = "") -> str:
    """Change the status of an application. Status must be one of: applied, oa, interview, offer, rejected."""

    status = status.lower()

    if status not in STATUSES:
        raise ToolError(f"Status must be one of {STATUSES}")

    with db() as conn:
        cur = conn.execute(
            "UPDATE applications SET status = ?, notes = ? WHERE id = ?",
            (status, notes, app_id),
        )

    if cur.rowcount == 0:
        raise ToolError(f"No application with id {app_id}")

    return f"Application {app_id} is now '{status}'"


@mcp.tool()
def list_applications(status: str = "") -> list[dict]:
    """List applications, newest first. Pass a status to filter (for example 'interview')."""

    with db() as conn:
        if status:
            rows = conn.execute(
                "SELECT * FROM applications WHERE status = ? ORDER BY id DESC",
                (status.lower(),),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM applications ORDER BY id DESC"
            ).fetchall()

    return [dict(r) for r in rows]


@mcp.tool()
def get_stats() -> dict:
    """Count applications by status and the share that got a reply (OA, interview or offer)."""

    with db() as conn:
        rows = conn.execute(
            "SELECT status, COUNT(*) AS n FROM applications GROUP BY status"
        ).fetchall()

    counts = {s: 0 for s in STATUSES}
    counts.update({r["status"]: r["n"] for r in rows})

    total = sum(counts.values())
    replied = counts["oa"] + counts["interview"] + counts["offer"]

    return {
        "total": total,
        "by_status": counts,
        "reply_rate_percent": round(100 * replied / total) if total else 0
    }


@mcp.tool()
def edit_application(
    app_id: int,
    company: str | None = None,
    role: str | None = None,
    status: str | None = None,
    applied_on: str | None = None,
    notes: str | None = None,
) -> str:
    """
    Edit any fields of an existing application.
    Only supplied fields are changed.
    Date format: YYYY-MM-DD.
    """

    updates = {}

    if company is not None:
        if not company.strip():
            raise ToolError("Company name cannot be empty")
        updates["company"] = company.strip()

    if role is not None:
        if not role.strip():
            raise ToolError("Job role cannot be empty")
        updates["role"] = role.strip()

    if status is not None:
        status = status.lower().strip()
        if status not in STATUSES:
            raise ToolError(f"Status must be one of {STATUSES}")
        updates["status"] = status

    if applied_on is not None:
        try:
            date.fromisoformat(applied_on)
        except ValueError:
            raise ToolError("Date must be in YYYY-MM-DD format")
        updates["applied_on"] = applied_on

    if notes is not None:
        updates["notes"] = notes

    if not updates:
        raise ToolError("Provide at least one field to update")

    with db() as conn:
        cur = conn.execute(
            "SELECT id FROM applications WHERE id = ?",
            (app_id,),
        )

        if cur.fetchone() is None:
            raise ToolError(f"No application with id {app_id}")

        columns = ", ".join(f"{column} = ?" for column in updates)
        values = list(updates.values()) + [app_id]

        conn.execute(
            f"UPDATE applications SET {columns} WHERE id = ?",
            values,
        )

    return f"Application {app_id} updated successfully: {', '.join(updates.keys())}"


@mcp.tool()
def delete_application(app_id: int) -> str:
    """Permanently delete an application by its ID."""

    with db() as conn:
        cur = conn.execute(
            "DELETE FROM applications WHERE id = ?",
            (app_id,),
        )

    if cur.rowcount == 0:
        raise ToolError(f"No application with id {app_id}")

    return f"Application {app_id} deleted successfully"

@mcp.resource("tracker://summary")
def summary() -> str:
    """A one-line summary of the whole tracker."""
    s = get_stats()
    return f"{s['total']} applications, {s['reply_rate_percent']}% got a reply"


@mcp.prompt()
def weekly_review() -> str:
    """Review applications and suggest next steps."""
    return (
        "Review my placement applications. "
        "First call get_stats to show my statistics. "
        "Then call list_applications to review all applications. "
        "Call list_stale_applications to identify applications "
        "still in 'applied' status for more than 7 days. "
        "Suggest which applications need follow-up and what "
        "I should prepare next for upcoming assessments or interviews. "
        "Clearly distinguish facts from recommendations."
    )



@mcp.tool()
def list_stale_applications() -> list[dict]:
    """List applications still in 'applied' status for more than 7 days."""

    cutoff_date = date.today() - timedelta(days=7)

    with db() as conn:
        rows = conn.execute(
            """
            SELECT * FROM applications
            WHERE status = ?
            AND applied_on < ?
            ORDER BY applied_on ASC
            """,
            ("applied", cutoff_date.isoformat()),
        ).fetchall()

    return [dict(row) for row in rows]


if __name__ == "__main__":
    mcp.run()
