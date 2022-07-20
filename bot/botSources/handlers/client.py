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




@dp.message_handler(commands=[ "start" ])
async def command_start_handler(message : types.Message) -> None:
    if (not functions.is_user_auth(message.from_user.id)):
        if (functions.add_new_user(message)):
            if (functions.add_expense_categories_for_user(message)):
                await message.answer(f"Привет, <b>{message.from_user.username}</b>,\n\nЭтот бот предназначен для учета ваших расходов\n\
                           \nВведите сумму, в рамках которой вы собираетесь тратиться ежедневно:")
                await Client.daily_amount.set()




@dp.message_handler(is_user_authenticated.IsUserAuthenticated(), state=Client.daily_amount)
async def set_daily_amount_handler(message : types.Message) -> None:
    try:
        daily_amount = int(message.text)
    except ValueError:
        await message.answer("Ваша сумма не является целым числом:\n<b>Введите повторно:</b>")
        return

    if (len(message.text) > 10):
        await message.answer("Ваша сумма слишком велика")
        return

    sql_request = f"UPDATE users SET daily_amount={daily_amount} WHERE user_telegram_id='{message.from_user.id}';"
    mysql = Mysql()
    if (not mysql.make_request(sql_request, is_need_data=False)):
        logger.error("Failed to update users.daily_amount field (line 41 in handlers/client.py)")
        return

    main_commands_keyboard = cl_inline.get_main_commands_inline_keyboard()
    await message.answer("Сумма успешно установлена\n<b>Выберите одну из предложенных комманд:</b>", reply_markup=main_commands_keyboard)
    await Client.main.set()




@dp.callback_query_handler(text="change_daily_amount", state=Client.main)
async def change_daily_amount_handler(callback : types.CallbackQuery) -> None:
    await callback.message.answer("<b>Введите сумму</b>, в рамках которой вы собираетесь тратиться ежедневно:")
    await Client.daily_amount.set()




@dp.callback_query_handler(text="add_today_expense", state=Client.main)
async def select_expense_category_handler(callback : types.CallbackQuery) -> None:
    categories = []
    commands = []
    messages = ""
    mysql = Mysql()
    request = f"SELECT * FROM users WHERE user_telegram_id='{callback.from_user.id}';"


    user_data = mysql.make_request(request, is_need_data=True)
    parsed_categories_from_db = user_data[ 0 ][ "user_expense_categories" ].split(";")
    parsed_categories_from_db.pop(len(parsed_categories_from_db) - 1)

    for category in parsed_categories_from_db:
        match = re.findall(r".+/", category)[ 0 ]
        categories.append( match[ 0 : len(match) - 1 ] )
        match1 = re.findall(r"/\w+", category)[ 0 ]
        commands.append( match1 )



    for element_id in range(0, len(commands)):
        messages += f"<b>{categories[ element_id ]}   :   {commands[ element_id ]}</b>\n"


    await callback.message.answer(f"<b>Выберите категорию траты:</b>\n\n{messages}", reply_markup=back_button)
    await Client.set_expense_category.set()





@dp.message_handler(is_expense_category.IsExpenseCategory(), state=Client.set_expense_category)
async def set_expense_category_handler(message : types.Message, state : FSMContext) -> None:
    command = message.text
    mysql = Mysql()
    request = f"SELECT * FROM users WHERE user_telegram_id='{message.from_user.id}';"

    user_data = mysql.make_request(request, is_need_data=True)
    parsed_categories_from_db = user_data[ 0 ][ "user_expense_categories" ].split(";")
    parsed_categories_from_db.pop(len(parsed_categories_from_db) - 1)

    is_find_command = False
    for category in parsed_categories_from_db:
        if (command in category):
            is_find_command = True
            match = re.findall(r".+/", category)[ 0 ]
            category_name = match[ 0 : len(match) - 1 ]



    async with state.proxy() as data:
        if (is_find_command):
            data[ "current_expense_category" ] = category_name
        else:
            return

    await message.answer("Введите сумму которую вы потратили")
    await Client.set_expense.set()



@dp.message_handler(state=Client.set_expense)
async def set_expense_handler(message : types.Message, state : FSMContext) -> None:
    async with state.proxy() as data:
        # Взятие из FSM название текущей операции
        # Это поле было добавлено в handler`е выше
        category_name = data[ "current_expense_category" ]

    try:
        amount = int(message.text)
    except ValueError:
        await message.answer("Сумма, потраченная вами, должна быть целочисленной\n<b>Введите повторно:</b>")
        return

    mysql = Mysql()
    now = datetime.now()
    date = f"{now.day}:{now.month}:{now.year}"
    expense = f"{category_name}:{amount};"



    # Запрос, имеется ли в таблице expenses запись о расходах на текущее число
    request = f"SELECT * FROM expenses WHERE user_telegram_id='{message.from_user.id}' AND date='{date}'"
    response = mysql.make_request(request, is_need_data=True)

    # Проверка по результатам запроса

    # Если запись есть
    if (len(response) != 0):
        # Взятие из бд сегоднешних расходов и добавление к ним нового
        expenses = response[ 0 ][ "expenses" ] + expense

        # Обновление expenses
        request = f"UPDATE expenses SET expenses='{expenses}' WHERE user_telegram_id='{message.from_user.id}' AND date='{date}';"

        # Выполнение и проверка на успех запроса
        if (not mysql.make_request(request, is_need_data=False)):
            logger.error("Failed to update expenses.expenses (line 151 in handlers/client.py)")

    # Если записи в бд нет
    else:
        # Запрос для получение данных о пользователе
        request = f"SELECT * FROM users WHERE user_telegram_id='{message.from_user.id}';"
        response = mysql.make_request(request, is_need_data=True)

        # Взятие из результатов запроса поля, которое отвечает за дневную расходную планку
        daily_amount = response[ 0 ][ "daily_amount" ]

        # Создание записи, в которой будут записаны рассходы пользователя на текущее число
        request = f"INSERT INTO expenses (id, user_telegram_id, date, expenses, current_daily_amount) VALUES (null, '{message.from_user.id}',\
            '{date}', null, {daily_amount});"

        # Выполнение и проверка на успех запроса
        if (not mysql.make_request(request, is_need_data=False)):
            logger.error("Failed to insert new field in expenses (line 157 in handler/client.py)")

        # Обновление expenses таблицы, измение столбца expenses с null на expense, который совершил user
        request = f"UPDATE expenses SET expenses='{expense}' WHERE user_telegram_id='{message.from_user.id}' AND date='{date}';"

        # Выполнение и проверка на успех запроса
        if (not mysql.make_request(request, is_need_data=False)):
            logger.error("Failed to update expenses.expenses (line 167 in handlers/client.py)")


    # Поиск строки в которой идет учет расходов, которые были совершены сегодня пользователем
    request_for_get_today_expense = f"SELECT * FROM expenses WHERE user_telegram_id='{message.from_user.id}' AND date='{date}';"
    response = mysql.make_request(request_for_get_today_expense, is_need_data=True)

    # Взятие из результата остатка ежедневного бюджета
    current_daily_amount = response[ 0 ][ "current_daily_amount" ]

    # Сумма денег которая будет добавлена в expenses.current_daily_amount как остаток
    daily_amount = current_daily_amount - amount

    # Обновление остатка
    request_for_update_current_daily_amount = f"UPDATE expenses SET current_daily_amount='{daily_amount}' \
        WHERE user_telegram_id='{message.from_user.id}' AND date='{date}';"

    # Выполнение и проверка на успех запроса
    if (not mysql.make_request(request_for_update_current_daily_amount, is_need_data=False)):
        logger.error("Failed to update expenses.current_daily_amount (line 178 in handlers/client.py)")

    # Если остаток положителен
    if (daily_amount > 0):
        # Отправление главной клавиатуры с сообщение об остатке
        await message.answer(f"<b>Дневная трата успешно добавлена</b>\n\nНа сегодня у вас осталось: \
    {functions.get_current_amount(message.from_user.id)} руб.", reply_markup=cl_inline.get_main_commands_inline_keyboard())
    # Если остаток ушел в минус
    else:
        # Получение изначального ежедневного количества денег
        request_for_get_user_daily_amount = f"SELECT * FROM users WHERE user_telegram_id='{message.from_user.id}';"
        response = mysql.make_request(request_for_get_user_daily_amount, is_need_data=True)
        # Сообщение пользователю о том что он вышел за пределы суммы, и отправление общей суммы потраченной за день
        await message.answer(f"<b>Дневная трата успешно добавлена</b>\n\n<b>Вы вышли за дневную сумму</b>, за сегодня вы потратили уже:\
    {functions.get_current_amount(message.from_user.id) * -1 + response[ 0 ][ 'daily_amount' ]} руб.",
            reply_markup=cl_inline.get_main_commands_inline_keyboard())

    # Установка главного состояния
    await Client.main.set()





@dp.callback_query_handler(text="check_current_amount", state=Client.main)
async def check_current_amount_handler(callback : types.CallbackQuery):
    current_daily_amount = functions.get_current_amount(callback.from_user.id)
    await callback.message.answer(f"<b>Оставшаяся сумма на день:</b>    {current_daily_amount} руб.",
                                  reply_markup=cl_inline.get_main_commands_inline_keyboard())





@dp.message_handler(state=Client.main)
async def general_main_state_handler(message : types.Message) -> None:
    main_commands_keyboard = cl_inline.get_main_commands_inline_keyboard()
    await message.answer("Выберите одну из предложенных команд: ", reply_markup=main_commands_keyboard)



@dp.message_handler()
async def general_handler(message : types.Message, state : FSMContext) -> None:
    if (functions.is_user_auth(message.from_user.id)):
        current_state = await state.get_state()
        if (current_state != "Client:main"):
            await Client.main.set()

        main_commands_keyboard = cl_inline.get_main_commands_inline_keyboard()
        await message.answer("Выберите одну из предложенных команд: ", reply_markup=main_commands_keyboard)
    else:
        await message.answer("У вас еще нет аккауна: нажмите /start чтобы его создать")

