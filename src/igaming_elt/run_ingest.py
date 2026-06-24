import asyncio
from .ingest_async import ingest_synthetic_to_postgres

if __name__ == "__main__":
    asyncio.run(ingest_synthetic_to_postgres())
