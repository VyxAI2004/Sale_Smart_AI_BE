import os

from dotenv import load_dotenv
from pydantic import BaseModel

from app_environment import AppEnvironment

app_env = os.getenv("APP_ENV", None)

if (app_env is None) or (app_env not in AppEnvironment.__members__):
    raise ValueError(
        f"APP_ENV not set, or invalid value. Valid values are: {', '.join(AppEnvironment.__members__)}"
    )

if app_env == AppEnvironment.test.value:
    load_dotenv(".env.test")
else:
    load_dotenv(".env", override=True)


class Env(BaseModel):
    APP_ENV: AppEnvironment
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    APP_DEBUG: bool
    FRONTEND_URL: str
    DOMAIN_URL: str
    OPENAI_API_KEY: str
    GEMINI_API_KEY: str
    ALLOWED_ORIGIN_REGEX: str
    JWT_SECRET_KEY: str
    JWT_REFRESH_SECRET_KEY: str
    JWT_ALGORITHM: str
    JWT_ACCESS_TOKEN_EXPIRE_WEEKS: int
    JWT_REFRESH_TOKEN_EXPIRE_WEEKS: int
    CLERK_PUBLISHABLE_KEY: str


env = Env.model_validate(os.environ)