from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
from ..mysql.Mysql import Mysql

class IsUserAuthenticated(BoundFilter):
    async def check(self, message : types.Message) -> bool:
        mysql = Mysql()
        sql_request = f"SELECT * FROM users WHERE user_telegram_id = '{message.from_user.id}';"
        response = mysql.make_request(sql_request, is_need_data=True)

        return True if len(response) != 0 else False






