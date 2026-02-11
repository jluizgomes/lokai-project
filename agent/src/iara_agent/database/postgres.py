"""PostgreSQL database client."""

from typing import Any
import asyncpg
import structlog

from iara_agent.config import settings

logger = structlog.get_logger()


class PostgresClient:
    """Client for PostgreSQL database operations."""

    def __init__(self) -> None:
        self._pool: asyncpg.Pool | None = None

    async def connect(self) -> None:
        """Connect to the database."""
        try:
            self._pool = await asyncpg.create_pool(
                host=settings.postgres_host,
                port=settings.postgres_port,
                database=settings.postgres_db,
                user=settings.postgres_user,
                password=settings.postgres_password,
                min_size=2,
                max_size=10,
            )
            logger.info("Connected to PostgreSQL")
        except Exception as e:
            logger.error("Failed to connect to PostgreSQL", error=str(e))
            raise

    async def disconnect(self) -> None:
        """Disconnect from the database."""
        if self._pool:
            await self._pool.close()
            self._pool = None
            logger.info("Disconnected from PostgreSQL")

    async def log_action(
        self,
        session_id: str,
        action_type: str,
        category: str,
        description: str,
        parameters: dict[str, Any],
        result: dict[str, Any] | None = None,
        success: bool = True,
        error_message: str | None = None,
        duration_ms: int | None = None,
        risk_level: str = "low",
        required_approval: bool = False,
        was_approved: bool | None = None,
    ) -> str:
        """Log an action to the database."""
        if not self._pool:
            raise RuntimeError("Database not connected")

        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO action_log (
                    session_id, action_type, category, description,
                    parameters, result, success, error_message,
                    duration_ms, risk_level, required_approval, was_approved
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                RETURNING id
                """,
                session_id,
                action_type,
                category,
                description,
                parameters,
                result,
                success,
                error_message,
                duration_ms,
                risk_level,
                required_approval,
                was_approved,
            )
            return str(row["id"])

    async def create_session(self) -> str:
        """Create a new session."""
        if not self._pool:
            raise RuntimeError("Database not connected")

        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                "INSERT INTO sessions DEFAULT VALUES RETURNING id"
            )
            return str(row["id"])

    async def end_session(self, session_id: str, summary: str | None = None) -> None:
        """End a session."""
        if not self._pool:
            raise RuntimeError("Database not connected")

        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE sessions
                SET ended_at = NOW(), summary = $2
                WHERE id = $1
                """,
                session_id,
                summary,
            )

    async def get_preference(self, key: str) -> Any:
        """Get a preference value."""
        if not self._pool:
            raise RuntimeError("Database not connected")

        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT value FROM preferences WHERE key = $1",
                key,
            )
            return row["value"] if row else None

    async def set_preference(self, key: str, value: Any, category: str | None = None) -> None:
        """Set a preference value."""
        if not self._pool:
            raise RuntimeError("Database not connected")

        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO preferences (key, value, category)
                VALUES ($1, $2, $3)
                ON CONFLICT (key) DO UPDATE
                SET value = $2, category = $3, updated_at = NOW()
                """,
                key,
                value,
                category,
            )

    async def get_allowed_directories(self) -> list[dict[str, Any]]:
        """Get all allowed directories."""
        if not self._pool:
            raise RuntimeError("Database not connected")

        async with self._pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM allowed_directories")
            return [dict(row) for row in rows]

    async def add_allowed_directory(self, path: str, permissions: list[str]) -> None:
        """Add an allowed directory."""
        if not self._pool:
            raise RuntimeError("Database not connected")

        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO allowed_directories (path, permissions)
                VALUES ($1, $2)
                ON CONFLICT (path) DO UPDATE
                SET permissions = $2
                """,
                path,
                permissions,
            )
