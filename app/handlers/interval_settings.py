import asyncio
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from app.config import aiogram_bot
from app.filters import IsAdmin
from app.keyboards import main_kb
from app.utils import monitor_obj
from app.crud import json_action
from app.states import states
router = Router()
router.message.filter(
    IsAdmin(F)
)


@router.callback_query(F.data == 'timing_settings')
async def p_interval_settings(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer('Введите новый интервал в минутах: ')
    await state.set_state(states.IntSet.input_interval)


@router.message(states.IntSet.input_interval)
async def p_set_int(message: Message, state: FSMContext):
    new_int = int(message.text) if message.text.isdigit() else 5
    await monitor_obj.set_interval(new_int)
    await message.answer(f'Интервал мониторинга успешно изменен на {new_int} минут.'
                         f'\nМониторинг был перезапущен.')

