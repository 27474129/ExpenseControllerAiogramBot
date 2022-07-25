from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_back_keyboard():
    return ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("Отменить"))
