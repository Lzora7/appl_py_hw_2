import os
from dotenv import load_dotenv

# Загрузка переменных из .env файла
load_dotenv()

# Чтение токена из переменной окружения
TOKEN = os.getenv("BOT_TOKEN")
API_CITY_KEY = os.getenv("API_CITY_KEY")

if not TOKEN:
    raise ValueError("Переменная окружения BOT_TOKEN не установлена!")
if not API_CITY_KEY:
    raise ValueError("Переменная окружения API_CITY_KEY не установлена!")