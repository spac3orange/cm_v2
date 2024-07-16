import asyncio

from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from app.config import aiogram_bot
from app.config.logger import logger
from app.filters import IsAdmin
from app.keyboards import main_kb
from app.crud import json_action
from app.states import states
router = Router()
router.message.filter(
    IsAdmin(F)
)


async def kw_settings(message):
    keywords_list = await json_action.open_json('app/crud/data/keywords.json')
    kw_str = ''
    for kw in keywords_list:
        kw_str += f'\n{kw}'
    await message.answer('<b>Список текущих установленных ключевых слов: </b>'
                         f'\n{kw_str}', reply_markup=main_kb.keywords_action(), parse_mode='HTML')


@router.callback_query(F.data == 'keywords')
async def p_keywords(callback: CallbackQuery):
    await callback.answer()
    keywords_list = await json_action.open_json('app/crud/data/keywords.json')
    kw_str = ''
    for kw in keywords_list:
        kw_str += f'\n{kw}'
    await callback.message.answer('<b>Список текущих установленных ключевых слов: </b>'
                                  f'\n{kw_str}', reply_markup=main_kb.keywords_action(), parse_mode='HTML')


@router.callback_query(F.data == 'add_kw')
async def p_add_kw(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer('Введите новое ключевое слово:')
    await state.set_state(states.AddKw.input_kw)


@router.message(states.AddKw.input_kw)
async def save_kw(message: Message, state: FSMContext):
    #await aiogram_bot.send_chat_action(message.chat.id, 'typing')
    new_kw = message.text
    kw_list = await json_action.open_json('app/crud/data/keywords.json')
    if kw_list == 'Нет':
        chats_lst = [new_kw]
    else:
        kw_list.append(new_kw)

    file_name = 'keywords.json'
    await json_action.write_json(kw_list, file_name)
    await message.answer('Ключевое слово успешно добавлено.')
    keywords_list = await json_action.open_json('app/crud/data/keywords.json')
    await state.clear()
    kw_str = ''
    for kw in keywords_list:
        kw_str += f'\n{kw}'
    await message.answer('<b>Список ключевых слов: </b>'
                         f'\n{kw_str}', reply_markup=main_kb.keywords_action(), parse_mode='HTML')


@router.callback_query(F.data == 'del_kw')
async def p_del_kw(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer('Введите ключевое слово для удаления: ')
    await state.set_state(states.DelKw.input_kw)


@router.message(states.DelKw.input_kw)
async def kw_deleted(message: Message, state: FSMContext):
    del_kw = message.text
    kw_list = await json_action.open_json('app/crud/data/keywords.json')
    if kw_list == 'Нет':
        await message.answer('Список ключевых слов пуст.')
        await state.clear()
    else:
        if del_kw in kw_list:
            kw_list.remove(del_kw)
            await json_action.write_json(kw_list, 'keywords.json')
            await message.answer(f'Ключевое слово [{del_kw}] удалено.')
            await kw_settings(message)
        else:
            await message.answer(f'Ключевое слово [{del_kw}] не найдено в списке ключевых слов.')
        await state.clear()