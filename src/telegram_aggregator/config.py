import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Config:
    tg_api_id: int
    tg_api_hash: str
    tg_phone: str
    tg_session_path: str

def load_config() -> Config:
    return Config(
        tg_api_id=int(os.environ["TG_API_ID"]),
        tg_api_hash=os.environ["TG_API_HASH"],
        tg_phone=os.environ["TG_PHONE"],
        tg_session_path=os.environ.get("TG_SESSION_PATH"),
    )

config: Config = load_config()