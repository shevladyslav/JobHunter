import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from database import engine
from services import UserService

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")

dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    with Session(engine) as session:
        user_service = UserService(session)
        user_service.create_user(message)
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
