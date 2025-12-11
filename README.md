# Описание
Telegram-бот анализирует экспортированные JSON-файлы чатов Telegram и собирает статистику об участниках.

Бот поддерживает два режима развертывания:
- локальный запуск (без Docker)
- запуск в контейнере через Docker Compose

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

## Как локально развернуть проект? С докером
1. Убедитесь, что установлен Docker и Docker Compose
Проверка:
```
docker -v
docker compose version
```
2. Создайте и заполните .env файл в корне проекта (пример выше)
3. Соберите и запустите контейнер, выполнив команду:
```
docker compose up -d --build
```
4. Также можно проверить логи, выполнив команду:
```
docker logs tg_chat_parser -f
```
5. Остановить бота можно командой:
```
docker compose down
```