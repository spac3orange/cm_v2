import asyncio
import random
from app.config.logger import logger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.config import config_telethon
from environs import Env
from app.crud import json_action
env = Env()
env.read_env()


class ChatMonitor:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.interval = env.int('INTERVAL')
        self.monitoring_enabled = False

    @staticmethod
    async def split_chats_list(chats_list):
        """Разделяет список chats_list на две части максимально равномерно.

        Args:
          chats_list: Список chats.

        Returns:
          Кортеж из двух списков, разделенных максимально равномерно.
        """
        list_len = len(chats_list)
        midpoint = list_len // 2  # Целочисленное деление для определения середины

        if list_len % 2 == 0:  # Если список четный
            return chats_list[:midpoint], chats_list[midpoint:]
        else:  # Если список нечетный, добавляем один элемент в первую часть
            return chats_list[:midpoint + 1], chats_list[midpoint + 1:]

    async def start_monitoring(self):
        if self.monitoring_enabled:
            return
        try:
            chats_list = await json_action.open_json('app/crud/data/chats.json')
            kw_list = await json_action.open_json('app/crud/data/keywords.json')
            chl1, chl2 = await self.split_chats_list(chats_list)
            sess1, sess2 = env.str('telethon_session'), env.str('telethon_session2')
            monitor = config_telethon.TelethonMonitorChats(sess1)
            monitor2 = config_telethon.TelethonMonitorChats(sess2)

            self.scheduler.add_job(monitor.get_chats_history, 'interval', minutes=self.interval, args=(self.interval, chl1, kw_list, sess1))
            self.scheduler.add_job(monitor2.get_chats_history, 'interval', minutes=self.interval, args=(self.interval, chl2, kw_list, sess2))
            self.scheduler.start()
            self.monitoring_enabled = True
            logger.info('Monitoring started')
        except Exception as e:
            logger.error(e)

    async def stop_monitoring(self):
        if not self.monitoring_enabled:
            return

        self.scheduler.remove_all_jobs()
        self.scheduler.shutdown()
        self.monitoring_enabled = False
        logger.info('Monitoring disabled')

    async def get_status(self):
        return self.monitoring_enabled

    async def set_interval(self, new_interval):
        # Перезапускаем мониторинг с новым интервалом
        self.interval = new_interval
        await self.stop_monitoring()
        await self.start_monitoring()
        logger.info(f'Interval changed to {new_interval} minutes')

    async def get_interval(self):
        return self.interval


monitor_obj = ChatMonitor()
