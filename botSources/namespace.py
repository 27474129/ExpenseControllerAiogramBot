from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv
from .keyboards.inline.clientInline import ClientInline
from .keyboards.default.back_button import get_back_keyboard
import os
import asyncio
import logging


load_dotenv()

storage = MemoryStorage()
bot = Bot(os.getenv("BOT_TOKEN"), parse_mode="HTML")
dp = Dispatcher(bot, storage=storage, loop=asyncio.get_event_loop())
cl_inline = ClientInline()
logger = logging.getLogger()
back_button = get_back_keyboard()