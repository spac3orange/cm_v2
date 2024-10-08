import asyncio
import random

import telethon.errors
from telethon import TelegramClient, errors, functions
from environs import Env
from telethon.tl.functions.messages import SendMessageRequest
from telethon.tl.types import InputPeerChannel
from app.config.logger import logger
from telethon.tl.functions.channels import JoinChannelRequest, GetFullChannelRequest
import datetime
from telethon.tl.functions.messages import GetHistoryRequest
from app.config import aiogram_bot, config_aiogram
from environs import Env
from app.crud import json_action
from pprint import pprint
import pytz
from telethon.tl.functions.messages import ImportChatInviteRequest


server_timezone = pytz.timezone('Europe/Moscow')
last_message = None

async def check_task_is_running():
    tasks = asyncio.all_tasks()
    for task in tasks:
        if task.get_coro().__qualname__ == 'TelethonMonitorChats.get_chats_history':
            return True
    return False

class TelethonMonitorChats:
    def __init__(self, session_name):
        env = Env()
        self.api_id = env('API_ID')
        self.api_hash = env('API_HASH')
        print(self.api_id, self.api_hash, session_name)
        self.session_name = 'app/crud/data/telethon_sessions/{}'.format(session_name)
        print(self.session_name)
        self.client = TelegramClient(self.session_name, self.api_id, self.api_hash)

    async def get_chat_messages(self, chat_link, kw_list, interval, offset_date):
        try:
            messages = []
            print(chat_link)
            entity = await self.client.get_entity(chat_link)
            async for message in self.client.iter_messages(entity.id, wait_time=1, limit=30):
                # print(message.text)
                if message.message:
                    message_text = message.message.lower()
                    if len(message_text) > 150:
                        continue
                    # message_text = message_text.split(' ')
                    # print(message_text)
                else:
                    continue
                if message.date < offset_date:
                    continue
                for kw in kw_list:
                    if kw.lower() in message.text.lower():
                        logger.info('Keyword found.')
                        if message not in messages:
                            logger.info('message added to forwarded ')
                            messages.append(message)
            # input_entity = InputPeerChat(entity.id)
            #
            # messages = await self.client(GetHistoryRequest(
            #     peer=input_entity,
            #     limit=limit,
            #     offset_date=None,  # Указать дату начала периода, если необходимо
            #     offset_id=0,
            #     max_id=0,
            #     min_id=0,
            #     add_offset=0,
            #     hash=0
            # ))
            #
            # return messages.messages
            return messages
        except Exception as e:
            logger.error(e)

    async def get_chats_history(self, interval, chat_list, kw_list, session_name):
        logger.info(f'session {session_name}')
        logger.info('Checking groups for new messages...')
        # running = await check_task_is_running()
        # if running:
        #     logger.error('Previous monitor is running. Schedule skipped...')
        #     return
        try:
            approved_messages = []
            chats_list = chat_list

            if chats_list == 'Нет' or kw_list == 'Нет':
                logger.error('Chats or keywords are empty.')
                return
            await self.client.connect()
            print(await self.client.get_me())
            print(self.client.is_connected())
            utc_now = datetime.datetime.now(pytz.utc)
            offset_date = utc_now - datetime.timedelta(minutes=interval)
            for chat in chats_list:
                logger.info(f'checking chat {chat}...')
                try:
                    if chat.startswith('https://t.me/+') or chat.startswith('https://t.me/joinchat/'):
                        try:
                            chatname = chat.split('/')[-1].lstrip('+')
                            updates = await self.client(ImportChatInviteRequest(chatname))
                        except telethon.errors.ChatAdminRequiredError:
                            chat = chatname
                        except Exception as e:
                            logger.error(e)
                            pass
                    try:
                        chat_messages = await asyncio.wait_for(self.get_chat_messages(f'{chat}', kw_list, interval, offset_date), timeout=15)
                    except asyncio.TimeoutError as e:
                        logger.error(e)
                        continue
                    if chat_messages:
                        for msg in chat_messages:
                            approved_messages.append(msg)
                except Exception as e:
                    logger.error(e)
                    continue

            if approved_messages:
                admin_list = config_aiogram.admin_id
                for message in approved_messages:
                    try:
                        try:
                            chat_entity = await self.client.get_entity(message.peer_id)
                            chat_name = chat_entity.username
                        except Exception as e:
                            logger.error(e)
                            chat_name = chat_entity.title

                        try:
                            user_entity = await self.client.get_entity(message.from_id)
                            username = user_entity.username
                        except Exception as e:
                            logger.error(e)
                            username = None

                        message_time = datetime.datetime.fromtimestamp(message.date.timestamp(), tz=pytz.utc)
                        # Преобразуйте время в часовой пояс вашего сервера
                        message_time = message_time.astimezone(server_timezone)
                        # Форматируйте дату в строку
                        msg_date = message_time.strftime('%d-%m-%Y %H:%M:%S')
                        bot_message = (f'<b>Дата:</b> {msg_date}'
                                       f'\n<b>Чат:</b> @{chat_name}'
                                       f'\n<b>Пользователь:</b> @{username}'
                                       f'\n<b>Сообщение:</b>\n{message.message}')

                        global last_message
                        if last_message == bot_message:
                            logger.warning('message skipped cos duplicate')
                            return
                        last_message = bot_message
                        if isinstance(admin_list, list):
                            for admin in admin_list:
                                await aiogram_bot.send_message(admin, bot_message, parse_mode='HTML')
                                print(f'msg sent to {admin}')
                        else:
                            await aiogram_bot.send_message(admin_list, bot_message, parse_mode='HTML')
                    except Exception as e:
                        logger.error(e)
                        continue

        except Exception as e:
            logger.error(e)
            print(e)
        finally:
            await self.client.disconnect()
