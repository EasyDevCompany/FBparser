from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from pydantic import BaseSettings, Field


class Config(BaseSettings):
    DEBUG: bool = Field(True, env="DEBUG")
    DB_NAME: str = Field("postgres", env="DB_NAME")
    DB_USER: str = Field("postgres", env="POSTGRES_USER")
    DB_PASSWORD: str = Field("pass", env="POSTGRES_PASSWORD")
    DB_HOST: str = Field("localhost", env="DB_HOST")
    DB_PORT: int = Field(5432, env="DB_PORT")
    RABBITMQ_DEFAULT_USER: str = Field("rabbitmq", env="RABBITMQ_DEFAULT_USER")
    RABBITMQ_DEFAULT_PASS: str = Field("rabbitmq", env="RABBITMQ_DEFAULT_PASS")
    RABBITMQ_DEFAULT_PORT: int = Field(5672, env="RABBITMQ_DEFAULT_PORT")
    RABBITMQ_DEFAULT_HOST: str = Field("rabbit", env="RABBITMQ_DEFAULT_HOST")
    BOT_TOKEN: str = Field(..., env="BOT_TOKEN")
    REDIS_HOST: str = Field("redis", env="REDIS_HOST")
    REDIS_PORT: int = Field(6379, env="REDIS_PORT")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


config = Config()

bot = Bot(config.BOT_TOKEN)
storage = RedisStorage2(config.REDIS_HOST, config.REDIS_PORT, db=1, pool_size=10, prefix="fsm_key")
dp = Dispatcher(bot, storage=storage)


database_uri = (
    f"postgresql+psycopg2://{config.DB_USER}:{config.DB_PASSWORD}@"
    f"{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}"
)
