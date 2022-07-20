from aiogram.dispatcher.filters.state import State, StatesGroup

class Client(StatesGroup):
    main = State()

    daily_amount = State()
    set_initial_expense_categories = State()
    set_expense = State()
    get_category_name = State()
    get_category_command = State()

    get_date_and_show_expenses = State()

    delete_expense = State()
    get_date = State()
    get_category = State()