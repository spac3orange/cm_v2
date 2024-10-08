import asyncio
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from app.config import aiogram_bot
from app.filters import IsAdmin
from app.keyboards import main_kb
from app.crud import json_action
from app.states import states
router = Router()
router.message.filter(
    IsAdmin(F)
)


async def groups_settings(message):
    chats_list = await json_action.open_json('app/crud/data/chats.json')
    if chats_list != 'Нет':
        string = ''
        print(chats_list)
        for chat in chats_list:
            string += f'\n{chat}'
    else:
        string = chats_list
    await message.answer('<b>Список чатов Telegram: </b>'
                         f'\n{string}', reply_markup=main_kb.chats_action(), parse_mode='HTML', disable_web_page_preview=True)


@router.callback_query(F.data == 'tg_groups')
async def p_groups(callback: CallbackQuery):
    await callback.answer()
    chats_list = await json_action.open_json('app/crud/data/chats.json')
    if chats_list != 'Нет':
        string = ''
        for chat in chats_list:
            string += f'\n{chat}'
    else:
        string = chats_list
    max_length = 4060
    print(len(string))
    if len(string) < max_length:
        await callback.message.answer('<b>Список чатов Telegram: </b>'
                                      f'\n{string}', reply_markup=main_kb.chats_action(), parse_mode='HTML', disable_web_page_preview=True)
    else:
        print(1)
        midpoint = len(string) // 2 # Находим середину строки
        part1 = string[:midpoint] # Первая часть строки
        part2 = string[midpoint:] # Вторая часть строки
        await callback.message.answer('<b>Список чатов Telegram: </b>'
                                      f'\n{part1}', reply_markup=main_kb.chats_action(), parse_mode='HTML', disable_web_page_preview=True)
        await callback.message.answer('<b>Список чатов Telegram: </b>'                                                                    
                                      f'\n{part2}', reply_markup=main_kb.chats_action(), parse_mode='HTML', disable_web_page_preview=True)

@router.callback_query(F.data == 'add_chat')
async def p_add_chat(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer('Введите ссылку на чат:')
    await state.set_state(states.AddChat.input_chat)


@router.message(states.AddChat.input_chat, lambda message: len(message.text) <= 30)
async def save_chat(message: Message, state: FSMContext):
    new_chat = message.text
    chats_lst = await json_action.open_json('app/crud/data/chats.json')
    if chats_lst == 'Нет':
        chats_lst = [new_chat]
    elif new_chat in chats_lst:
        await message.answer(f'Ошибка! Чат {new_chat} уже есть в списке.')
        return
    else:
        chats_lst.append(new_chat)
    filename = 'chats.json'
    await json_action.write_json(chats_lst, filename)
    await message.answer('Чат добавлен.')
    chats_lst = await json_action.open_json('app/crud/data/chats.json')
    await state.clear()
    await groups_settings(message)



@router.callback_query(F.data == 'del_chat')
async def p_del_chat(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer('Введите ссылку для удаления: ')
    await state.set_state(states.DelChat.input_chat)


@router.message(states.DelChat.input_chat)
async def chat_deleted(message: Message, state: FSMContext):
    del_chat = message.text
    chats_list = await json_action.open_json('app/crud/data/chats.json')
    if chats_list == 'Нет':
        await message.answer('Список чатов пуст.')
        await state.clear()
    else:
        if del_chat in chats_list:
            chats_list.remove(del_chat)
            await json_action.write_json(chats_list, 'chats.json')
            await message.answer(f'Чат [{del_chat}] удален из списка чатов.')
            await groups_settings(message)
        else:
            await message.answer(f'Чат [{del_chat}] не найден в списке чатов.')
        await state.clear()


@router.message(states.AddChat.input_chat)
async def save_chat(message: Message, state: FSMContext):
    new_chats = message.text.split('\n')
    chats_lst = await json_action.open_json('app/crud/data/chats.json')
    for chat in new_chats:
        if chat in chats_lst:
            await message.answer(f'Чат {chat} уже есть в списке.')
            continue
        else:
            chats_lst.append(chat)
            await message.answer(f'Чат {chat} добавлен в список.')
    filename = 'chats.json'
    await json_action.write_json(chats_lst, filename)
    await state.clear()

