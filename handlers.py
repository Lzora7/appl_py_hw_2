from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from states import Form
import aiohttp

router = Router()

# Обработчик команды /start
@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.reply("Добро пожаловать! Я ваш бот.\nВведите /help для списка команд.")

# Обработчик команды /help
@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.reply(
        "Доступные команды:\n"
        "/start - Начало работы\n"
        "/set_profile - Настройка вашего профиля\n"
        "/log_water <количество> - Количество выпитой воды\n"
        "/log_food <название продукта> - Количество съеденной еды|\n"
        "/log_workout <тип тренировки> <время (мин)> - Запись информации о тренировке\n"
        "/check_progress - Информация о прогрессе"
    )

# Обработчик команды /keyboard с инлайн-кнопками
@router.message(Command("keyboard"))
async def show_keyboard(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Кнопка 1", callback_data="btn1")],
            [InlineKeyboardButton(text="Кнопка 2", callback_data="btn2")],
        ]
    )
    await message.reply("Выберите опцию:", reply_markup=keyboard)

@router.callback_query()
async def handle_callback(callback_query):
    if callback_query.data == "btn1":
        await callback_query.message.reply("Вы нажали Кнопка 1")
    elif callback_query.data == "btn2":
        await callback_query.message.reply("Вы нажали Кнопка 2")


# FSM: Заполнение формы о пользователе
@router.message(Command("form"))
async def start_form(message: Message, state: FSMContext):
    await message.reply("Введите ваш вес (в кг):")
    await state.set_state(Form.weight)

@router.message(Form.weight)
async def process_height(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.reply("Введите ваш рост (в см):")
    await state.set_state(Form.height)

@router.message(Form.height)
async def process_age(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.reply("Введите ваш возраст:")
    await state.set_state(Form.age)

@router.message(Form.age)
async def process_action_minutes(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.reply("Сколько минут активности у вас в день?")
    await state.set_state(Form.action_minutes)

@router.message(Form.action_minutes)
async def process_city(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.reply("В каком городе вы находитесь?")
    await state.set_state(Form.city)

@router.message(Form.city)
async def process_city(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.reply("Какая у вас цель калорий?")
    await state.set_state(Form.calories_goal)

# Итог
@router.message(Form.calories_goal)
async def process_city(message: Message, state: FSMContext):
    data = await state.get_data()
    weight = data.get("weight")
    height = data.get("height")
    age = data.get("age")
    action_minutes = data.get("action_minutes")
    city =  data.get("city")
    calories_goal = data.get("calories_goal")
    # age = message.text
    await message.reply(f"Итак, \n"
                        f"- вес: {weight} \n"
                        f"- рост: {height} \n"
                        f"- возраст: {age} \n"
                        f"- кол-во активных минут: {action_minutes} \n"
                        f"- город: {city} \n"
                        f"- цель по калориям: {city} \n"
                        )
    await state.clear()

# Получение шутки из API
@router.message(Command("joke"))
async def get_joke(message: Message):
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.chucknorris.io/jokes/random") as response:
            joke = await response.json()
            await message.reply(joke["value"])

# Функция для подключения обработчиков
def setup_handlers(dp):
    dp.include_router(router)