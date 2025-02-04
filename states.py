from aiogram.fsm.state import State, StatesGroup

# форма о пользователе
class Form(StatesGroup):
    weight = State() # вес
    height = State() # рост
    age = State() # возраст
    action_minutes = State()
    city = State()
    calories_goal = State()
    city_temp = State()

# контекст разговора при логировании еды
class LogFoodContext(StatesGroup):
    food_name = State() # название еды
    # food_cal = State() # количество калорий в 100 гр еды
    amount_gram = State() # кол-во грамм, что съел пользователь