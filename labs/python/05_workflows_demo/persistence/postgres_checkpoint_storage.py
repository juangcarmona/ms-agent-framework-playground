"""
PostgreSQL-based CheckpointStorage for Microsoft Agent Framework Workflows.

Creates the database (if missing) and ensures maf_checkpoints table exists.
Stores entire WorkflowCheckpoint objects as JSONB payloads.
"""

import logging
import asyncio
from datetime import datetime, timezone
from typing import List, Optional
from dataclasses import asdict

from sqlalchemy import (
    Table,
    Column,
    String,
    JSON,
    DateTime,
    MetaData,
    func,
    select,
    delete,
    text,
)
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import OperationalError
from agent_framework import WorkflowCheckpoint, CheckpointStorage

logger = logging.getLogger("maf.persistence")

metadata = MetaData()

checkpoints_table = Table(
    "maf_checkpoints",
    metadata,
    Column("checkpoint_id", String, primary_key=True),
    Column("workflow_id", String, index=True),
    Column("data", JSON, nullable=False),
    # store timezone-aware UTC timestamps safely
    Column("created_at", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)),
)


class PostgresCheckpointStorage(CheckpointStorage):
    """Lightweight PostgreSQL CheckpointStorage using SQLAlchemy async engine."""

    def __init__(self, dsn: str):
        self.dsn = dsn
        self.engine: Optional[AsyncEngine] = None

    # --------------------------------------------------------------------------
    # Initialization
    # --------------------------------------------------------------------------
    async def initialize(self) -> None:
        """Ensure database and table exist."""
        self.engine = await self._ensure_database_and_engine()
        async with self.engine.begin() as conn:
            await conn.run_sync(metadata.create_all)
        logger.info("✅ PostgresCheckpointStorage initialized and ready")

    async def _ensure_database_and_engine(self) -> AsyncEngine:
        """Ensure target DB exists (create if missing) and return async engine."""
        # Extract base DSN (without DB name)
        # e.g. postgresql+asyncpg://user:pass@host:port/dbname
        import re
        m = re.match(r"^(postgresql\+asyncpg:\/\/[^\/]+)\/(.+)$", self.dsn)
        if not m:
            raise ValueError(f"Invalid DSN: {self.dsn}")
        base_dsn, dbname = m.groups()

        # Connect to postgres default DB first
        admin_dsn = f"{base_dsn}/postgres"
        admin_engine = create_async_engine(admin_dsn, echo=False, future=True)

        # Check/create database
        async with admin_engine.begin() as conn:
            exists = await conn.scalar(
                text("SELECT 1 FROM pg_database WHERE datname = :name"),
                {"name": dbname},
            )
            if not exists:
                logger.warning(f"Database '{dbname}' not found. Creating it...")
                await conn.execute(text(f"CREATE DATABASE {dbname}"))
                logger.info(f"✅ Created database '{dbname}'")

        await admin_engine.dispose()
        # Connect to the target DB
        return create_async_engine(self.dsn, echo=False, future=True)

    # --------------------------------------------------------------------------
    # Core operations
    # --------------------------------------------------------------------------
    async def save_checkpoint(self, checkpoint: WorkflowCheckpoint) -> str:
        assert self.engine is not None, "Storage not initialized"
        checkpoint_dict = asdict(checkpoint)
        async with self.engine.begin() as conn:
            stmt = (
                pg_insert(checkpoints_table)
                .values(
                    checkpoint_id=checkpoint.checkpoint_id,
                    workflow_id=checkpoint.workflow_id,
                    data=checkpoint_dict,
                    created_at=datetime.now(timezone.utc),
                )
                .on_conflict_do_update(
                    index_elements=[checkpoints_table.c.checkpoint_id],
                    set_={
                        "workflow_id": checkpoint.workflow_id,
                        "data": checkpoint_dict,
                        "created_at": func.now(),
                    },
                )
            )
            await conn.execute(stmt)
        logger.debug("💾 Saved checkpoint %s", checkpoint.checkpoint_id)
        return checkpoint.checkpoint_id

    async def load_checkpoint(self, checkpoint_id: str) -> Optional[WorkflowCheckpoint]:
        """Load a checkpoint by ID."""
        assert self.engine is not None
        async with self.engine.connect() as conn:
            result = await conn.execute(
                select(checkpoints_table.c.data).where(
                    checkpoints_table.c.checkpoint_id == checkpoint_id
                )
            )
            row = result.scalar_one_or_none()
            if row:
                logger.debug(f"Loaded checkpoint {checkpoint_id}")
                return WorkflowCheckpoint.from_dict(row)
        return None

    async def list_checkpoint_ids(self, workflow_id: Optional[str] = None) -> List[str]:
        """List checkpoint IDs, optionally filtered by workflow."""
        assert self.engine is not None
        async with self.engine.connect() as conn:
            stmt = select(checkpoints_table.c.checkpoint_id)
            if workflow_id:
                stmt = stmt.where(checkpoints_table.c.workflow_id == workflow_id)
            result = await conn.execute(stmt)
            return [r[0] for r in result.all()]

    async def list_checkpoints(
        self, workflow_id: Optional[str] = None
    ) -> List[WorkflowCheckpoint]:
        """List checkpoints, optionally filtered by workflow."""
        assert self.engine is not None
        async with self.engine.connect() as conn:
            stmt = select(checkpoints_table.c.data)
            if workflow_id:
                stmt = stmt.where(checkpoints_table.c.workflow_id == workflow_id)
            result = await conn.execute(stmt)
            rows = [WorkflowCheckpoint.from_dict(r[0]) for r in result.all()]
            return rows

    async def delete_checkpoint(self, checkpoint_id: str) -> bool:
        """Delete a checkpoint by ID."""
        assert self.engine is not None
        async with self.engine.begin() as conn:
            res = await conn.execute(
                delete(checkpoints_table).where(
                    checkpoints_table.c.checkpoint_id == checkpoint_id
                )
            )
        deleted = res.rowcount > 0
        if deleted:
            logger.debug(f"🧹 Deleted checkpoint {checkpoint_id}")
        return deleted

    async def close(self):
        if self.engine:
            await self.engine.dispose()
            self.engine = None
