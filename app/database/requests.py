from .session import async_session
from . import start_words as sw
from .models import User, Word, Past, Mode
from sqlalchemy import select, update, delete, or_
from sqlalchemy.future import select
from sqlalchemy.sql import func
from random import randint

async def set_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            session.add(User(tg_id=tg_id))
            await session.commit()
            user_id = await session.scalar(select(User.id).where(User.tg_id == tg_id))
            for i in sw.w:
                session.add(Word(eng=i[0], rus=i[1], user_id=user_id))
            session.add(Mode(state=1, user_id=user_id))
            await session.commit()


async def get_words(tg_id):
    async with async_session() as session:
        try:
            user_id = await session.scalar(select(User.id).where(User.tg_id == tg_id))
            words = await session.execute(
                select(Word.eng, Word.rus).where(Word.user_id == user_id)
            )

            return words
        except Exception as e:
            print(f'Ошибка {e} в функции get_words. Входные данные: tg_id={tg_id}')


async def get_word_info(tg_id, words):
    async with async_session() as session:
        user_id = await session.scalar(select(User.id).where(User.tg_id == tg_id))
        try:
            word = await session.execute(
                select(Word.eng, Word.rus).where(or_(Word.eng == words, Word.rus == words), Word.user_id == user_id)
            )
            return list(word)[0]
        except Exception as e:
            print(f'Ошибка {e} в функции get_word_info. Входные данные: tg_id={tg_id}, words={words}')
        


async def set_words(tg_id, words):
    async with async_session() as session:
        try:
            user_id = await session.scalar(select(User.id).where(User.tg_id == tg_id))
            check_repeat = await session.scalar(
                select(Word.eng).where(Word.eng == words[0], Word.user_id == user_id)
            )

            if check_repeat:
                return "Такое слово уже есть"

            else:
                session.add(Word(eng=words[0], rus=words[1], user_id=user_id))
                await session.commit()
        except Exception as e:
            print(f'Ошибка {e} в функции set_words. Входные данные: tg_id={tg_id}, words={words}')

async def delete_words(tg_id, word_del):
    async with async_session() as session:
        try:
            user_id = await session.scalar(select(User.id).where(User.tg_id == tg_id))
            word_id = await session.scalar(
                select(Word.id).where(Word.eng == word_del, Word.user_id == user_id)
            )
            await session.execute(
                delete(Word).where(Word.id == word_id, Word.user_id == user_id)
            )
            await session.commit()
        except Exception as e:
            print(f'Ошибка {e} в функции delete_words. Входные данные: tg_id={tg_id}, word_del={word_del}')

async def check_rus_answer(tg_id, word_question, user_answer):
    async with async_session() as session:
        try:
            user_id = await session.scalar(select(User.id).where(User.tg_id == tg_id))
            check_word = await session.scalar(
                select(Word.eng).where(Word.rus.ilike(word_question), Word.user_id == user_id)
            )
            right_answer = check_word
            return True if right_answer == user_answer else False
        except Exception as e:
            print(f'Ошибка {e} в функции check_rus_answer. Входные данные: tg_id={tg_id}, word_question={word_question}, user_answer={user_answer}')

async def check_eng_answer(tg_id, word_question, user_answer):
    async with async_session() as session:
        try:
            user_id = await session.scalar(select(User.id).where(User.tg_id == tg_id))
            check_word = await session.scalar(
                select(Word.rus).where(Word.eng.ilike(word_question), Word.user_id == user_id)
            )
            right_answer = check_word
            return True if right_answer == user_answer else False
        except Exception as e:
            print(f'Ошибка {e} в функции check_eng_answer. Входные данные: tg_id={tg_id}, word_question={word_question}, user_answer={user_answer}')

async def random_words(tg_id):
    async with async_session() as session:
        try:
            user_id = await session.scalar(select(User.id).where(User.tg_id == tg_id))
            words = await session.execute(
                select(Word.eng, Word.rus).where(Word.user_id == user_id)
            )

            return list(words)[randint(0, len(list(await get_words(tg_id))) - 1)]
        except Exception as e:
            print(f'Ошибка {e} в функции random_words. Входные данные: tg_id={tg_id}')
async def add_past_word(tg_id, add_word):
    async with async_session() as session:
        try:
            user_id = await session.scalar(select(User.id).where(User.tg_id == tg_id))
            total_words = await session.scalar(
                select(func.count(Word.id)).where(Word.user_id == user_id)
            )
            past_words_count = await session.scalar(
                select(func.count(Past.id)).where(Past.user_id == user_id)
            )
            if past_words_count == total_words:
                await session.execute(delete(Past).where(Past.user_id == user_id))
                await session.commit()
            is_word_in_past = await session.scalar(
                select(Past.id).where(Past.words == add_word, Past.user_id == user_id)
            )
            if not is_word_in_past:
                session.add(Past(words=add_word, user_id=user_id))
                await session.commit()
                return False

            return True
        except Exception as e:
            print(f'Ошибка {e} в функции add_past_word. Входные данные: tg_id={tg_id}, words={add_word}')

async def change_user_mode(tg_id, state):
    async with async_session() as session:
        try:
            user_id = await session.scalar(select(User.id).where(User.tg_id == tg_id))
            await session.execute(update(Mode).where(Mode.user_id == user_id).values(state=state))
            await session.commit()
        except Exception as e:
            print(f'Ошибка {e} в функции change_user_mode. Входные данные: tg_id={tg_id}')

async def check_user_mode(tg_id):
    async with async_session() as session:
        try:
            user_id = await session.scalar(select(User.id).where(User.tg_id == tg_id))
            cur_state = await session.scalar(select(Mode.state).where(Mode.user_id == user_id))
            return cur_state
        except Exception as e:
            print(f'Ошибка {e} в функции check_user_mode. Входные данные: tg_id={tg_id}')