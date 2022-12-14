import logging
from typing import Union

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from pydantic import BaseSettings, Field, PostgresDsn, validator


class Settings(BaseSettings):
    DB_NAME: str = Field("postgres", env="DB_NAME")
    DB_USER: str = Field("postgres", env="POSTGRES_USER")
    DB_PASSWORD: str = Field("pass", env="POSTGRES_PASSWORD")
    DB_HOST: str = Field("localhost", env="DB_HOST")
    DB_PORT: int = Field(5432, env="DB_PORT")
    RABBITMQ_DEFAULT_USER: str = Field("rabbitmq", env="RABBITMQ_DEFAULT_USER")
    RABBITMQ_DEFAULT_PASS: str = Field("rabbitmq", env="RABBITMQ_DEFAULT_PASS")
    RABBITMQ_DEFAULT_PORT: int = Field(5672, env="RABBITMQ_DEFAULT_PORT")
    RABBITMQ_DEFAULT_HOST: str = Field("rabbit", env="RABBITMQ_DEFAULT_HOST")
    BOT_TOKEN: str = Field("token", env="BOT_TOKEN")
    REDIS_HOST: str = Field("redis", env="REDIS_HOST")
    REDIS_PORT: int = Field(6379, env="REDIS_PORT")
    PSQL_DATABASE_URI: Union[str, None] = None

    @validator("PSQL_DATABASE_URI", pre=True)
    def build_db_uri(cls, v: Union[str, None], values: dict) -> str:
        return PostgresDsn.build(
            scheme="postgresql+psycopg2",
            user=values.get("DB_USER"),
            password=values.get("DB_PASSWORD"),
            host=values.get("DB_HOST"),
            port=str(values.get("DB_PORT")),
            path=f"/{values.get('DB_NAME')}",
        )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s.%(funcName)s:%(lineno)d - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

app_logger = logging.getLogger()

config = Settings()

bot = Bot(config.BOT_TOKEN)
storage = RedisStorage2(config.REDIS_HOST, config.REDIS_PORT, db=1, pool_size=10, prefix="fsm_key")
dp = Dispatcher(bot, storage=storage)


database_uri = config.PSQL_DATABASE_URI
