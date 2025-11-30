from pathlib import Path

from dotenv import load_dotenv
from pydantic import field_validator
from pydantic_settings import BaseSettings

load_dotenv(override=True)


class Settings(BaseSettings, env_parse_none_str="None"):
    vk_token: str
    group_id: int | None = None
    db_path: Path = Path("epicnotify.db")

    @field_validator("db_path")
    @classmethod
    def validate_db_path(cls, value: Path) -> Path:
        if not value.is_absolute():
            base_path = Path(__file__).parent.parent.parent
            value = base_path / value
        value.parent.mkdir(parents=True, exist_ok=True)
        return value


settings = Settings()  # type: ignore
