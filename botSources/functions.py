from .mysql.Mysql import Mysql
from .namespace import *
from datetime import datetime


def is_user_auth(user_telegram_id) -> bool:
    sql_request = f"SELECT * FROM users WHERE user_telegram_id='{user_telegram_id}';"
    mysql = Mysql()
    return True if len(mysql.make_request(sql_request, is_need_data=True)) != 0 else False


def add_new_user(message) -> bool:

    mysql = Mysql()
    sql_request = f"INSERT INTO users (id, username, user_telegram_id) VALUES (null, '{message.from_user.username}',\
                    '{message.from_user.id}')"

    if (not mysql.make_request(sql_request, is_need_data=False)):
        logger.error("Failed to create user in users (line 18 in functions.py)")
        return False
    else:
        return True


def add_expense_categories_for_user(message) -> bool:
    mysql = Mysql()
    categories = [
        "Такси", "Кинотеатр", "Кафе", "Ресторан", "Одежда", "Подарок", "Бензин", "Продукты",
        "Ремонт и обслуживание машины", "Интернет покупки", "Лечение", "Парикмахерская"
    ]
    commands = [
        "/taxi", "/cinema", "/cafe", "/restaurant", "/clothes", "/present", "/gasoline", "/products",
        "/repair_service_car", "/ethernet_expense", "/treatment", "/salon"
    ]
    expense_categories_for_db = ""



    for element_id in range(0, len(categories)):
        expense_categories_for_db += f"{categories[element_id] + commands[element_id]};"
    request = f"UPDATE users SET user_expense_categories='{expense_categories_for_db}' \
        WHERE user_telegram_id='{message.from_user.id}';"


    if (not mysql.make_request(request, is_need_data=False)):
        logger.error("Failed to update users.user_expense_categories (line 45 in functions.py)")
        return False
    else:
        return True


def get_current_amount(user_telegram_id) -> int:
    mysql = Mysql()
    now = datetime.now()
    date = f"{now.day}:{now.month}:{now.year}"
    request_for_find_today_expense_row = f"SELECT * FROM expenses WHERE user_telegram_id='{user_telegram_id}' AND date='{date}';"
    request_for_get_user_daily_amount = f"SELECT * FROM users WHERE user_telegram_id='{user_telegram_id}';"

    response = mysql.make_request(request_for_find_today_expense_row, is_need_data=True)
    if (response is not None):
        return response[ 0 ]["current_daily_amount"]
    else:
        response = mysql.make_request(request_for_get_user_daily_amount, is_need_data=True)
        return response[ 0 ]["daily_amount"]