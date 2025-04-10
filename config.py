from os import environ
from time import time


class Config:
    API_ID = int(environ.get("API_ID", "21288218"))
    API_HASH = environ.get("API_HASH", "dd47d5c4fbc31534aa764ef9918b3acd")
    BOT_TOKEN = environ.get("BOT_TOKEN", "7104434929:AAFPUwKyRNI_d9_P4jnIJGBDDB3OkQf77zo")
    BOT_SESSION = environ.get("BOT_SESSION", "bot")
    DATABASE_URI = environ.get("DATABASE", "mongodb+srv://SnowForwardBot:z8C0JT1iyOXa7RjZ@cluster0.ufgamee.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    DATABASE_NAME = environ.get("DATABASE_NAME", "Cluster0")
    BOT_OWNER_ID = [int(id) for id in environ.get("BOT_OWNER_ID", '6065594762').split()]
    BOT_START_TIME = time()


class temp(object):
    lock = {}
    CANCEL = {}
    forwardings = 0
    BANNED_USERS = []
    IS_FRWD_CHAT = []
