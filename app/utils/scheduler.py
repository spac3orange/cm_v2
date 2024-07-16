import asyncio
import random
from app.config.logger import logger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.config import config_telethon
from environs import Env
env = Env()
env.read_env()


class ChatMonitor:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.interval = env.int('INTERVAL')
        self.monitoring_enabled = False

    async def start_monitoring(self):
        if self.monitoring_enabled:
            return
        try:
            monitor = config_telethon.TelethonMonitorChats(env.str('telethon_session'))
            self.scheduler.add_job(monitor.get_chats_history, 'interval', minutes=self.interval, args=(self.interval,))
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
