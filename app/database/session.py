from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from . import params as p

db_url = f'postgresql+asyncpg://{p.params["login"]}:{p.params["password"]}@localhost:{p.params["localhost"]}/{p.params["namedb"]}'

engine = create_async_engine(url=db_url)

async_session = async_sessionmaker(engine)
