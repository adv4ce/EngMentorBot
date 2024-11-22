from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from . import keyboards as kb
from .database import requests as rq
from .states import Ans
import random as rand
import numpy as np

r = Router()


@r.message(CommandStart())
async def start(message: Message):
    await rq.set_user(message.from_user.id)
    await message.answer(
        f"Привет, {message.from_user.full_name}!\n👋 Я твой помощник для изучения английских слов! 🌟\n🎯 Цель простая: помочь тебе выучить английский легко и интересно. Давай начинать! 😊",
        reply_markup=kb.main,
    )


@r.message(F.text == "Профиль ⚙️")
async def profile(message: Message):
    state_learning = await rq.check_user_mode(message.from_user.id)
    if state_learning == 1:
        state_learning = "Английский"
    else:
        state_learning = "Русский"
    await message.answer(
        f"👤 Ученик: {message.from_user.first_name}\n\n🆔 ID: {message.from_user.id}\n\n🔢 Кол-во твоих слов: {len([i for i in await rq.get_words(message.from_user.id)])}\n\n🎓 Режим обучения: {state_learning}",
        reply_markup=kb.mode,
    )


@r.callback_query(F.data == "state_1")
async def state_1(callback: CallbackQuery):
    await callback.answer("Режим переключен на Английский")
    state_learning = await rq.check_user_mode(callback.from_user.id)
    if state_learning == 2:
        await callback.message.edit_text(
            f"👤 Ученик: {callback.from_user.first_name}\n\n🆔 ID: {callback.from_user.id}\n\n🔢 Кол-во твоих слов: {len([i for i in await rq.get_words(callback.from_user.id)])}\n\n🎓 Режим обучения: Английский",
            reply_markup=kb.mode,
        )
        await rq.change_user_mode(callback.from_user.id, 1)


@r.callback_query(F.data == "state_2")
async def state_1(callback: CallbackQuery):
    await callback.answer("Режим переключен на Русский")
    state_learning = await rq.check_user_mode(callback.from_user.id)
    if state_learning == 1:
        if state_learning == 1:
            state_learning = "Английский"
        else:
            state_learning = "Русский"
        await callback.message.edit_text(
            f"👤 Ученик: {callback.from_user.first_name}\n\n🆔 ID: {callback.from_user.id}\n\n🔢 Кол-во твоих слов: {len([i for i in await rq.get_words(callback.from_user.id)])}\n\n🎓 Режим обучения: Русский",
            reply_markup=kb.mode,
        )
        await rq.change_user_mode(callback.from_user.id, 2)


@r.message(F.text == "Назад 🔙")
async def back(message: Message):
    await message.answer(
        f"Чем ты хочешь заняться, {message.from_user.first_name}? 😊",
        reply_markup=kb.main,
    )


@r.message(F.text == "Мои слова 📓")
async def my_words(message: Message):
    await message.answer(
        "Твои слова 📓", reply_markup=await kb.words_quantity(message.from_user.id)
    )


@r.callback_query(F.data == "add")
async def add_word(callback: CallbackQuery, state: FSMContext):
    await callback.answer("")
    await state.set_state(Ans.word_eng)
    await callback.message.delete()
    await callback.message.answer("✍️ Введи слово на английском", reply_markup=kb.back)


@r.message(Ans.word_eng)
async def add_eng_word(message: Message, state: FSMContext):
    await state.update_data(word_eng=message.text)
    await state.set_state(Ans.word_rus)
    await message.reply("✍️ Введи слово на русском", reply_markup=kb.back)


@r.message(Ans.word_rus)
async def add_rus_word(message: Message, state: FSMContext):
    await state.update_data(word_rus=message.text)
    data = await state.get_data()
    check = await rq.set_words(message.from_user.id, [data[i] for i in data.keys()])
    if check:
        await message.answer(f"Слово: {data['word_eng']} уже есть в твоей коллекции", reply_markup=kb.main)
    else:
        await message.answer(f"Слово {data['word_eng']} добавлено", reply_markup=kb.main)
        await message.answer(
            f"Твои слова", reply_markup=await kb.words_quantity(message.from_user.id)
        )
    await state.clear()


@r.callback_query(F.data.startswith("word_"))
async def word_info(callback: CallbackQuery, state: FSMContext):
    word = await rq.get_word_info(
        callback.from_user.id, callback.data.split("_")[1].strip()
    )
    await callback.message.edit_text(
        f"{word[0]} -> {word[1]}", reply_markup=kb.word_info
    )
    await state.set_state(Ans.current_word)
    await state.update_data(current_word=word[0])


@r.callback_query(F.data == "delete")
async def delete_info(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await rq.delete_words(callback.from_user.id, data["current_word"])
    await callback.message.edit_text(f"Слово: {data['current_word']} удалено")
    await state.clear()
    await callback.message.answer(
        f"Твои слова", reply_markup=await kb.words_quantity(callback.from_user.id)
    )


@r.callback_query(F.data == "back")
async def delete_info(callback: CallbackQuery):
    await callback.message.edit_text(
        f"Твои слова", reply_markup=await kb.words_quantity(callback.from_user.id)
    )


@r.message(F.text == "Обучение 📝")
async def start_learning(message: Message, state: FSMContext):
    await message.answer("Переключаюсь в режим обучения 🎓")
    mode = await rq.check_user_mode(message.from_user.id)
    if mode == 1:
        await eng_learning(message, state, message.from_user.id)
    else:
        await rus_learning(message, state, message.from_user.id)


async def rus_learning(message, state, tg_id):
    question = await rq.random_words(tg_id)
    question = question[1]
    check = await rq.add_past_word(message.from_user.id, question)
    if check:
        question = await rq.random_words(tg_id)
        question = question[1]

    await state.set_state(Ans.question)
    await state.update_data(question=question)
    await message.answer(
        f"Как переводится слово:\n{question}",
        reply_markup=await kb.rus_learning_kb(tg_id, question),
    )
    await state.set_state(Ans.user_answer)
    await state.update_data(cur_state=2)

@r.message(Ans.user_answer)
async def user_answ(message: Message, state: FSMContext):
    await state.update_data(user_answer=message.text)
    data = await state.get_data()
    cur_state = data['cur_state']
    if cur_state == 1:
        check_answer = await rq.check_eng_answer(
            message.from_user.id, data["question"], data["user_answer"]
        )
    else:
        check_answer = await rq.check_rus_answer(
            message.from_user.id, data["question"], data["user_answer"]
        )
    if message.text == "Закончить обучение 🔙":
        await message.answer(
            f"Чем ты хочешь заняться, {message.from_user.first_name}? 😊",
            reply_markup=kb.main,
        )
        await state.clear()

    elif check_answer:
        await message.reply(
            f"Правильно!\nСлово: {data['question']} переводится как {data['user_answer']}"
        )
        await state.clear()
        if cur_state == 1:
            await eng_learning(message, state, message.from_user.id)
        else:
            await rus_learning(message, state, message.from_user.id)
    else:
        await bad_answer(message, state)

async def eng_learning(message, state, tg_id):
    question = await rq.random_words(tg_id)
    question = question[0]
    check = await rq.add_past_word(message.from_user.id, question)
    if check:
        question = await rq.random_words(tg_id)
        question = question[0]

    await state.set_state(Ans.question)
    await state.update_data(question=question)
    await message.answer(
        f"Как переводится слово:\n{question}",
        reply_markup=await kb.learning_kb(tg_id, question),
    )
    await state.set_state(Ans.user_answer)
    await state.update_data(cur_state=1)

async def bad_answer(message, state):
    data = await state.get_data()
    await message.answer("Неправильно, попробуй еще раз")
    await message.answer(f"Как переводится слово:\n{data['question']}")
    await state.set_state(Ans.user_answer)


@r.message(F.text == "Закончить обучение 🔙")
async def exit(message: Message):
    await message.answer(
        f"Чем ты хочешь заняться, {message.from_user.first_name}? 😊",
        reply_markup=kb.main,
    )
