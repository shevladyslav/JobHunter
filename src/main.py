import asyncio
import logging
import os
import sys
from datetime import datetime, timedelta
from parser import fetch_jobs_from_djinni

from aiogram import Bot, Dispatcher, F, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import engine
from keyboards import startMenu
from models import Vacancy
from services import UserService

load_dotenv()
env = Environment(loader=FileSystemLoader("templates"))

TOKEN = os.getenv("TELEGRAM_TOKEN")

dp = Dispatcher()
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


async def delete_old_vacancies():
    while True:
        with Session(engine) as session:
            three_days_ago = datetime.utcnow() - timedelta(days=3)
            old_vacancies = (
                session.query(Vacancy)
                .filter(Vacancy.publication_date < three_days_ago)
                .all()
            )

            if old_vacancies:
                for vacancy in old_vacancies:
                    session.delete(vacancy)
                session.commit()

        await asyncio.sleep(60)


async def check_user_status_and_send_vacancies(telegram_id: int, chat_id: int) -> None:
    while True:

        new_jobs = fetch_jobs_from_djinni()

        with Session(engine) as session:
            user_service = UserService(session)
            user = user_service.get_user_by_telegram_id(telegram_id)

            if not user or not user.task_status:
                break

            new_vacancies = []

            for job in new_jobs:
                vacancy_exists = session.execute(
                    select(Vacancy).where(Vacancy.vacancy_link == job["vacancy_link"])
                ).scalar_one_or_none()

                if not vacancy_exists:
                    vacancy = Vacancy(
                        company_name=job["company_name"],
                        job_title=job["job_title"],
                        publication_date=datetime.strptime(
                            job["publication_date"], "%H:%M %d.%m.%Y"
                        ),
                        vacancy_link=job["vacancy_link"],
                    )
                    session.add(vacancy)
                    session.commit()
                    user.vacancies.append(vacancy)
                    new_vacancies.append(vacancy)
                else:
                    if vacancy_exists not in user.vacancies:
                        user.vacancies.append(vacancy_exists)
                        new_vacancies.append(vacancy_exists)

            session.commit()

            if new_vacancies:
                template = env.get_template("vacancies.html")
                html_response = template.render(vacancies=new_vacancies)
                await bot.send_message(
                    chat_id, html_response, parse_mode=ParseMode.HTML
                )

        await asyncio.sleep(60)


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    with Session(engine) as session:
        user_service = UserService(session)
        user_service.create_user(message)
        await message.answer("Ви зареєстровані. Вітаю!", reply_markup=startMenu)


@dp.message(F.text == "Переглянути останні вакансії за сьогодні")
async def view_vacancies_by_user(message: Message) -> None:
    with Session(engine) as session:
        user_service = UserService(session)
        if user := user_service.get_user_by_telegram_id(message.from_user.id):
            vacancies = user_service.get_today_vacancies_by_user(user.id)
            template = env.get_template("vacancies.html")
            html_response = template.render(vacancies=vacancies)
            await message.answer(html_response, parse_mode=ParseMode.HTML)


@dp.message(F.text == "Розпочати пошук вакансій")
async def start_updates_handler(message: Message) -> None:
    telegram_id = message.from_user.id
    chat_id = message.chat.id

    with Session(engine) as session:
        user_service = UserService(session)
        user = user_service.get_user_by_telegram_id(telegram_id)

        if user:
            if not user.task_status:
                user.task_status = True
                session.commit()
                await message.answer("Пошук вакансій розпочато!")
                await asyncio.create_task(
                    check_user_status_and_send_vacancies(telegram_id, chat_id)
                )
            else:
                await message.answer("Пошук вакансій вже запущено.")
        else:
            await message.answer("Не знайдено користувача.")


@dp.message(F.text == "Зупинити пошук вакансій")
async def stop_updates_handler(message: Message) -> None:
    telegram_id = message.from_user.id
    with Session(engine) as session:
        user_service = UserService(session)
        user = user_service.get_user_by_telegram_id(telegram_id)
        if user and user.task_status:
            user.task_status = False
            session.commit()
            await message.answer("Оновлення вакансій зупинено!")
        else:
            await message.answer(
                "Оновлення вакансій не було запущено або не знайдено користувача."
            )


async def main() -> None:
    cron_delete_old_vacancies = asyncio.create_task(delete_old_vacancies())
    await dp.start_polling(bot)
    await cron_delete_old_vacancies


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
