from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
from ..mysql.Mysql import Mysql

import re


class IsExpenseCategory(BoundFilter):
    async def check(self, message : types.Message) -> bool:
        request = f"SELECT * FROM users WHERE user_telegram_id='{message.from_user.id}';"
        mysql = Mysql()
        commands = []


        user_data = mysql.make_request(request, is_need_data=True)
        parsed_categories_from_db = user_data[0]["user_expense_categories"].split(";")
        parsed_categories_from_db.pop(len(parsed_categories_from_db) - 1)

        for category in parsed_categories_from_db:
            match = re.findall(r"/\w+", category)[ 0 ]
            commands.append( match )

        return True if message.text in commands else False

