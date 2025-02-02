from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from states import Form, LogFoodContext
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

def water_goal(weight, action_minutes):
    base_water = int(weight) * 30 # мл
    add_water_action = int(action_minutes) / 30 * 500 # мл
    # add_water_weather
    sum_water = base_water + add_water_action
    return sum_water

def calorie_norm(weight, height, age):
    cal = 10*weight + 6.25*height - 5*age
    return cal

# FSM: Заполнение формы о пользователе
@router.message(Command("set_profile"))
async def start_form(message: Message, state: FSMContext):
    await message.reply("Введите ваш вес (в кг):")
    # переход на заполнение возраста
    await state.set_state(Form.weight)

@router.message(Form.weight)
async def process_height(message: Message, state: FSMContext):
    await state.update_data(weight=message.text)
    await message.reply("Введите ваш рост (в см):")
    await state.set_state(Form.height)

@router.message(Form.height)
async def process_age(message: Message, state: FSMContext):
    await state.update_data(height=message.text)
    await message.reply("Введите ваш возраст:")
    await state.set_state(Form.age)

@router.message(Form.age)
async def process_action_minutes(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.reply("Сколько минут активности у вас в день?")
    await state.set_state(Form.action_minutes)

@router.message(Form.action_minutes)
async def process_city(message: Message, state: FSMContext):
    await state.update_data(action_minutes=message.text)
    await message.reply("В каком городе вы находитесь?")
    await state.set_state(Form.city)

@router.message(Form.city)
async def process_city(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    await message.reply("Какая у вас цель калорий?")
    await state.set_state(Form.calories_goal)

# Итог (вывод введенных данных + занесение в хранилище)
@router.message(Form.calories_goal)
async def process_city(message: Message, state: FSMContext):
    await state.update_data(calories_goal=message.text)
    # получение данных из заполненной формы
    data = await state.get_data()
    weight = data.get("weight")
    height = data.get("height")
    age = data.get("age")
    action_minutes = data.get("action_minutes")
    city = data.get("city")
    calories_goal = data.get("calories_goal")

    # Новый user_id
    new_id = int(max(users.keys())) + 1
    # Внесение данных
    users[new_id] = {}
    users[new_id]['weight'] = int(weight)
    users[new_id]['height'] = int(height)
    users[new_id]['age'] = int(age)
    users[new_id]['activity'] = int(action_minutes)
    users[new_id]['city'] = city
    users[new_id]['logged_water'] = 0
    users[new_id]['logged_calories'] = 0
    users[new_id]['burned_calories'] = 0
    if calories_goal != '':
        users[new_id]['calorie_goal'] = int(calories_goal)
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
    last_id = int(max(users.keys()))
    # логируем воду
    users[last_id]['logged_water'] += int(command.args)
    # остаток по воде
    residue_water = users[last_id]['water_goal'] - users[last_id]['logged_water']
    await message.reply(f"До нормы осталось выпить: {residue_water} мл")

# Информация о продукте (калории)
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

# Логирование еды 1.1
@router.message(Command("log_food"))
async def log_food(message: Message, command: CommandObject, state: FSMContext):
    if command.args is None:
        await message.answer(
            "Ошибка: не переданы аргументы"
        )
    # Поиск калорийности по API
    food_info = get_food_info(CommandObject)
    if food_info is None:
        print('еда не нашлась')
    else:
        food_name = food_info['name']
        food_cal = int(food_info['calories'])
        # запись в контекст
        await state.update_data(food_name=food_name)
        await state.update_data(food_cal=food_cal)
        await state.set_state(LogFoodContext.amount_gram)

# Логирование еды 1.2
@router.message(LogFoodContext.food_cal)
async def log_food(message: Message, state: FSMContext):
    # получение записанных данных
    data = await state.get_data()
    food_name = data.get('food_name')
    food_cal = data.get('food_cal')
    # грамовка
    await message.reply(f"{food_name} - {food_cal} ккал на 100 г. Сколько грамм вы съели?")
    amount_gram = int(message.text)
    new_cal = amount_gram * food_cal
    # актуальный пользователь
    last_id = int(max(users.keys()))
    # логируем калории
    users[last_id]['logged_calories'] += new_cal
    # остаток по калориям
    residue_cal = users[last_id]['calorie_goal'] - users[last_id]['logged_calories']
    await message.reply(f"До нормы осталось употребить: {residue_cal} г")

# Логирование тренировок
@router.message(Command("log_workout"))
async def log_workout(message: Message, command: CommandObject):
    if command.args is None:
        await message.answer(
            "Ошибка: не переданы аргументы"
        )
    # извлекаем входные данные
    workout_msg = command.args.split(sep=' ')
    workout_type = workout_msg[0] # тип тренировки
    workout_minutes = int(workout_msg[1]) # кол-во минут тренировки
    if workout_type == 'бег':
        minute_cal = 10
        water_need = 200
    elif workout_type == 'силовая':
        minute_cal = 30
        water_need = 400
    elif workout_type == 'плавание':
        minute_cal = 15
        water_need = 270
    else:
        print('неизвестный вид тренировки')
    burned_cal = workout_minutes * minute_cal
    # актуальный пользователь
    last_id = int(max(users.keys()))
    # логируем сожженные калории
    users[last_id]['burned_calories'] += burned_cal
    # добавок воды
    extra_water = water_need * workout_minutes / 30
    users[last_id]['water_goal'] += extra_water
    await message.reply(f"{workout_type} {workout_minutes} минут - {burned_cal} ккал. Дополнительно: выпейте {extra_water} мл. воды.")

# Функция для подключения обработчиков
def setup_handlers(dp):
    dp.include_router(router)

