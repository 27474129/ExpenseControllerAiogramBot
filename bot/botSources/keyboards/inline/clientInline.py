from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

class ClientInline:
    def get_main_commands_inline_keyboard(self):
        command1 = InlineKeyboardButton(text="Добавить ежедневную трату", callback_data="add_today_expense")
        command2 = InlineKeyboardButton(text="Добавить категорию трат", callback_data="add_expense_category")
        command3 = InlineKeyboardButton(text="Посмотреть оставшуюся сумму на день", callback_data="check_current_amount")
        command4 = InlineKeyboardButton(text="Изменить ежедневную сумму для трат", callback_data="change_daily_amount")
        command5 = InlineKeyboardButton(text="Вчерашние затраты", callback_data="check_tomorrow_expenses")
        command6 = InlineKeyboardButton(text="Затраты за определенное число", callback_data="check_previous_expense")
        command7 = InlineKeyboardButton(text="Статистика", callback_data="statistic")

        main_commands_inline_keyboard = InlineKeyboardMarkup()
        main_commands_inline_keyboard.add(command1)
        main_commands_inline_keyboard.add(command2)
        main_commands_inline_keyboard.add(command3)
        main_commands_inline_keyboard.add(command4)
        main_commands_inline_keyboard.add(command5)
        main_commands_inline_keyboard.add(command6)
        main_commands_inline_keyboard.add(command7)
        return main_commands_inline_keyboard

