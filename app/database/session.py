from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from . import params as p

engine = create_async_engine(url=f'postgresql+asyncpg://{p.params['login']}:{p.params['password']}@localhost:{p.params['localhost']}/{p.params['namedb']}')

async_session = async_sessionmaker(engine)