import logging
from pathlib import Path
from agent_framework import InMemoryCheckpointStorage, FileCheckpointStorage
from persistence.postgres_checkpoint_storage import PostgresCheckpointStorage
from config import (
    POSTGRES_HOST, POSTGRES_PORT,
    POSTGRES_USER, POSTGRES_PASS,
    POSTGRES_DB, 
)

logger = logging.getLogger("maf.persistence.factory")

class CheckpointStorageFactory:
    """
    Centralized factory for creating and initializing checkpoint storage backends.
    """

    def __init__(self):
        self._storage = None

    async def init_memory(self):
        """Use in-memory checkpointing (volatile, ideal for tests)."""
        self._storage = InMemoryCheckpointStorage()
        logger.info("✅ Using InMemoryCheckpointStorage")
        return self._storage

    async def init_file(self, path: str | Path = "./checkpoints"):
        """Use local file-based checkpointing (simple persistence)."""
        self._storage = FileCheckpointStorage(path)
        logger.info(f"✅ Using FileCheckpointStorage at {path}")
        return self._storage

    async def init_postgres(self):
        """Use PostgreSQL-backed checkpointing (persistent, recommended)."""
        dsn = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASS}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
        storage = PostgresCheckpointStorage(dsn)
        await storage.initialize()
        self._storage = storage
        logger.info(f"✅ Using PostgresCheckpointStorage on {POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}")
        return self._storage

    def get(self):
        if not self._storage:
            raise RuntimeError("Checkpoint storage not initialized. Call init_*() first.")
        return self._storage
