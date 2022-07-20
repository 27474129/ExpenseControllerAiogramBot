from aiogram.dispatcher.filters.state import State, StatesGroup

class Client(StatesGroup):
    main = State()

    daily_amount = State()
    set_expense_category = State()
    set_expense = State()
