from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

startMenu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Переглянути останні вакансії за сьогодні"),
            KeyboardButton(text="Розпочати пошук вакансій"),
            KeyboardButton(text="Зупинити пошук вакансій"),
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=False,
)
