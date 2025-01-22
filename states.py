from aiogram.fsm.state import State, StatesGroup

# форма о пользователе
class Form(StatesGroup):
    weight = State() # вес
    height = State() # рост
    age = State() # возраст
    action_minutes = State()
    city = State()
    calories_goal = State()