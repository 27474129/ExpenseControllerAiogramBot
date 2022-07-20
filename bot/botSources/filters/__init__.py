from .is_expense_category import IsExpenseCategory
from .is_user_authenticated import IsUserAuthenticated
from ..namespace import *

if (__name__ == "__main__"):
    dp.filters_factory.bind(IsUserAuthenticated)
    dp.filters_factory.bind(IsExpenseCategory)