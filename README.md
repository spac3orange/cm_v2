Шаг 1: Установка Python 3.11
Если у вас еще нет Python 3.11, скачайте и установите его с официального сайта.

Шаг 2: Создание виртуального окружения
Откройте терминал (или командную строку).
Перейдите в директорию вашего проекта.
Создайте виртуальное окружение.
```python3.11 -m venv venv```

Шаг 3: Активируйте виртуальное окружение.
На Windows:
```venv\Scripts\activate```
На macOS и Linux:
```source venv/bin/activate```

Шаг 4: Заполните файл .env
Создайте и заполните конфиг файл .env папке bot/config/.env в соответствии с файлом env_example

Шаг 5: Установите зависимости.
```pip install -r requirements.txt```

Шаг 6: Запустите бот.
```python bot.py```