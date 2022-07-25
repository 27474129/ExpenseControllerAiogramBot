from aiogram import types
from ..namespace import *
from ..states import Client
from ..filters import is_user_authenticated, is_expense_category
from ..mysql.Mysql import Mysql
from .. import functions
from aiogram.dispatcher import FSMContext
from datetime import datetime
from aiogram import filters

import logging
import re
import asyncio


@dp.message_handler(commands=[ "back" ], state="*")
@dp.message_handler(filters.Text("Отменить"), state="*")
async def back_handler(message : types.Message):
    await message.answer("Выберите одну из предложенных команд: ", reply_markup=cl_inline.get_main_commands_inline_keyboard())
    await Client.main.set()