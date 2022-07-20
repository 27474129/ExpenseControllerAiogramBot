from aiogram import executor
from .namespace import *
from . import middlewares, filters, handlers

import os
import logging


def launch_bot():
    logging.basicConfig(level=logging.ERROR)

    executor.start_polling(dispatcher=dp, skip_updates=True)

