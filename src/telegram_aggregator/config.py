import os
import logging
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class LoggingConfig:
    level: int
    format: str

@dataclass(frozen=True)
class TGConfig:
    tg_api_id: int
    tg_api_hash: str
    tg_phone: str
    tg_session_path: str

@dataclass(frozen=True)
class Config:
    tg: TGConfig
    logging: LoggingConfig

def load_config() -> Config:
    return Config(
        tg=TGConfig(
            tg_api_id=int(os.environ["TG_API_ID"]),
            tg_api_hash=os.environ["TG_API_HASH"],
            tg_phone=os.environ["TG_PHONE"],
            tg_session_path=os.environ["TG_SESSION_PATH"],
        ),
        logging=LoggingConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        )
    )

config: Config = load_config()