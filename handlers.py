from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from states import Form
import aiohttp
import requests

router = Router()

users = {
    1: {
            "weight": 80,
            "height": 184,
            "age": 26,
            "activity": 45,
            "city": "Paris",
            "water_goal": 2400,
            "calorie_goal": 2500,
            "logged_water": 500,
            "logged_calories": 1800,
            "burned_calories": 400
    }
}

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


# def upload_user_data(lst_data):
#     # Берём первое значение из словаря
#     first_value = users[1]
#     # Находим максимальную цифру (ключ) в первом значении
#     max_digit = max(first_value.keys())
#     for data in lst_data:
#         users[max_digit][data] =

def water_goal(weight, action_minutes):
    base_water = weight * 30 # мл
    add_water_action = action_minutes / 30 * 500 # мл
    # add_water_weather
    sum_water = base_water + add_water_action
    return sum_water

def calorie_norm(weight, height, age):
    cal = 10*weight + 6.25*height - 5*age
    return cal

# FSM: Заполнение формы о пользователе
@router.message(Command("form"))
async def start_form(message: Message, state: FSMContext):
    await message.reply("Введите ваш вес (в кг):")
    await users
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

# Итог (вывод введенных данных + занесение в хранилище)
@router.message(Form.calories_goal)
async def process_city(message: Message, state: FSMContext):
    # получение данных из заполненной формы
    data = await state.get_data()
    weight = data.get("weight")
    height = data.get("height")
    age = data.get("age")
    action_minutes = data.get("action_minutes")
    city =  data.get("city")
    calories_goal = data.get("calories_goal")

    # Новый user_id
    first_value = users[1]
    new_id = int(max(first_value.keys())) + 1
    # Внесение данных
    users[new_id]['weight'] = weight
    users[new_id]['height'] = height
    users[new_id]['age'] = age
    users[new_id]['activity'] = action_minutes
    users[new_id]['city'] = city
    if calories_goal is not '':
        users[new_id]['calorie_goal'] = calories_goal
    else:
        users[new_id]['calorie_goal'] = calorie_norm(weight, height, age)
    users[new_id]['water_goal'] = water_goal(weight, action_minutes)

    # age = message.text
    await message.reply(f"Итак, \n"
                        f"- вес: {weight} \n"
                        f"- рост: {height} \n"
                        f"- возраст: {age} \n"
                        f"- кол-во активных минут: {action_minutes} \n"
                        f"- город: {city} \n"
                        f"- цель по калориям: {users[new_id]['calorie_goal']} \n"
                        f"- цель по выпитой воде: {users[new_id]['water_goal']}"
                        )
    await state.clear()

# Логирование воды
@router.message(Command("log_water"))
async def log_water(message: Message, command: CommandObject):
    if command.args is None:
        await message.answer(
            "Ошибка: не переданы аргументы"
        )
    # актуальный пользователь
    first_value = users[1]
    last_id = int(max(first_value.keys()))
    # логируем воду
    users[last_id]['logged_water'] += command.args
    # остаток по воде
    residue_water = users[last_id]['water_goal'] - users[last_id]['logged_water']
    await message.reply(f"До нормы осталось выпить: {residue_water} мл")

def get_food_info(product_name):
    url = f"https://world.openfoodfacts.org/cgi/search.pl?action=process&search_terms={product_name}&json=true"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        products = data.get('products', [])
        if products:  # Проверяем, есть ли найденные продукты
            first_product = products[0]
            return {
                'name': first_product.get('product_name', 'Неизвестно'),
                'calories': first_product.get('nutriments', {}).get('energy-kcal_100g', 0)
            }
        return None
    print(f"Ошибка: {response.status_code}")
    return None

# Логирование еды
@router.message(Command("log_food"))
async def log_food(message: Message, command: CommandObject, state: FSMContext):
    if command.args is None:
        await message.answer(
            "Ошибка: не переданы аргументы"
        )
    # Поиск калорийности по API
    food_info = get_food_info(CommandObject)
    food_name = food_info['name']
    food_cal = int(food_info['calories'])
    await state.set_state(Form.weight)
    # грамовка
    await message.reply(f"{food_name} - {food_cal} ккал на 100 г. Сколько грамм вы съели?")

    # актуальный пользователь
    first_value = users[1]
    last_id = int(max(first_value.keys()))
    # логируем калории
    users[last_id]['logged_calories'] += food_cal
    # остаток по калориям
    residue_water = users[last_id]['calorie_goal'] - users[last_id]['logged_calories']
    await message.reply(f"До нормы осталось выпить: {residue_water} мл")


# Логирование тренировок
@router.message(Command("log_workout"))
async def log_water(message: Message, command: CommandObject):
    if command.args is None:
        await message.answer(
            "Ошибка: не переданы аргументы"
        )
    # извлекаем входные данные
    workout_msg = message.text.split(sep=' ')
    workout_type = workout_msg[0]
    workout_minutes = workout_msg[1]

    # актуальный пользователь
    first_value = users[1]
    last_id = int(max(first_value.keys()))
    # логируем воду
    users[last_id]['logged_water'] += command.args
    # остаток по воде
    residue_water = users[last_id]['water_goal'] - users[last_id]['logged_water']
    await message.reply(f"До нормы осталось выпить: {residue_water} мл")



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