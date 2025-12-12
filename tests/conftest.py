import os
import pytest
from unittest.mock import MagicMock, Mock, AsyncMock


def pytest_configure(config):
    """Устанавливает переменные окружения до импорта модулей"""
    # Устанавливаем переменные окружения до импорта тестовых модулей
    # чтобы избежать ошибок при инициализации классов на уровне модуля
    os.environ['TELEGRAM_BOT_TOKEN'] = 'test_token_12345'
    os.environ['EXCEL_USER_THRESHOLD'] = '10'
    os.environ['MAX_FILE_SIZE'] = '20'
    os.environ['MAX_FILES_AMOUNT'] = '5'


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Фикстура для установки переменных окружения для тестов"""
    monkeypatch.setenv('TELEGRAM_BOT_TOKEN', 'test_token_12345')
    monkeypatch.setenv('EXCEL_USER_THRESHOLD', '10')
    monkeypatch.setenv('MAX_FILE_SIZE', '20')
    monkeypatch.setenv('MAX_FILES_AMOUNT', '5')


@pytest.fixture
def mock_update():
    """Фикстура для создания мок-объекта Update"""
    update = MagicMock()
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    update.message.reply_document = AsyncMock()
    update.message.document = MagicMock()
    return update


@pytest.fixture
def mock_context():
    """Фикстура для создания мок-объекта Context"""
    context = MagicMock()
    context.user_data = {}
    return context


@pytest.fixture
def sample_telegram_json():
    """Пример JSON данных из экспорта Telegram"""
    return {
        "messages": [
            {
                "from_id": "user123",
                "from": "john_doe",
                "text": "Hello @alice and @bob!",
                "text_entities": [
                    {"type": "mention", "text": "@alice"},
                    {"type": "mention", "text": "@bob"}
                ]
            },
            {
                "from_id": "user456",
                "from": "jane_smith",
                "text": "Hi everyone!",
                "text_entities": []
            },
            {
                "from_id": "user789",
                "from": "Deleted Account",
                "text": "Some message",
                "text_entities": []
            }
        ]
    }

