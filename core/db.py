from sqlalchemy import engine
from sqlalchemy.orm import sessionmaker
from env import env

db = engine.create_engine(
    f"postgresql://{env.DB_USER}:{env.DB_PASSWORD}@{env.DB_HOST}:{env.DB_PORT}/{env.DB_NAME}",
    # echo=(AppEnvironment.is_production_env(env.APP_ENV) == False),
    pool_pre_ping=True,
    # pool_size=5,
    # max_overflow=2,
    # pool_timeout=30,
    pool_recycle=1800,
)

Session = sessionmaker(bind=db)

