from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseModel):
    database_url: str = os.getenv("DATABASE_URL", "")
    postgres_raw_table: str = os.getenv("POSTGRES_RAW_TABLE", "raw_player_session_events")

    spark_local_master: str = os.getenv("SPARK_LOCAL_MASTER", "local[*]")
    app_name: str = os.getenv("APP_NAME", "igaming-player-elt")

    target_warehouse: str = os.getenv("TARGET_WAREHOUSE", "bigquery")
    bq_project_id: str = os.getenv("BQ_PROJECT_ID", "")
    bq_dataset: str = os.getenv("BQ_DATASET", "igaming_analytics")

settings = Settings()
