from ..namespace import dp
from .main import MainMiddleware


if (__name__ == "middlewares"):
    dp.middleware.setup(MainMiddleware)
