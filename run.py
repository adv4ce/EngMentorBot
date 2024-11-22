from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
import logging
import asyncio

from app.handlers import r
from params import TOKEN
from app.database.models import async_main

async def main():
  bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
  dp = Dispatcher()
  dp.include_router(r)
  dp.startup.register(startup)
  dp.shutdown.register(shutdown)

  await dp.start_polling(bot)


async def startup(dispatcher: Dispatcher):
    await async_main()
    print('Starting up...')


async def shutdown(dispatcher: Dispatcher):
    print('Shutting down...')

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        print("Exit")