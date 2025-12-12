# Тесты

## Запуск

```bash
pytest
```

## Зависимости

```bash
pip install -r requirements-test.txt
```

## Структура

- `test_command_handler.py` - обработчик команд
- `test_message_handler.py` - обработчик сообщений
- `test_chat_bot.py` - основной класс бота
- `test_main.py` - точка входа
- `conftest.py` - общие фикстуры

Подробное описание тестов см. в `TESTS_DESCRIPTION.md`.
