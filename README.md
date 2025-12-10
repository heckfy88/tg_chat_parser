# Тут будет описание

## Как заполнить .env? 
```
TELEGRAM_BOT_TOKEN=<токен вашего бота телеграм>
MAX_FILE_SIZE=<???>
MAX_FILES_AMOUNT=<???>
EXCEL_USER_THRESHOLD=<???>
```

## Как локально развернуть проект? Без докера
1. Скопируйте этот репозиторий ```git clone git@github.com:heckfy88/tg_chat_parser.git```
2. Перейдите в него ```cd /tg_chat_parser```
3. Создайте виртуальное окружение ```python -m venv venv```
4. Активируйте виртуальное окружение ```source /venv/bin/activate/```
5. Установите зависимости ```pip insdtall -r requirements.txt```
5. Заполните файл ```.env```
6. Запустите файл ```main.py```

## Как локально развеинуть проект? С докером