from aiogram.fsm.state import StatesGroup, State


class Ans(StatesGroup):
    word_eng = State()
    word_rus = State()
    user_answer = State()
    question = State()
    current_word = State()
    cur_state = State()
