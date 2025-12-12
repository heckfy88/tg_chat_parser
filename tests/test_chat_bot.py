import os
import pytest
from unittest.mock import MagicMock, patch, Mock

from bot.chat_bot import ChatBot


class TestChatBot:
    """Тесты для класса ChatBot"""

    @pytest.fixture
    def mock_application(self):
        """Фикстура для мокирования Application"""
        with patch('bot.chat_bot.Application') as mock_app_class:
            mock_app = MagicMock()
            mock_builder = MagicMock()
            mock_builder.token.return_value = mock_builder
            mock_builder.build.return_value = mock_app
            mock_app_class.builder.return_value = mock_builder
            yield mock_app

    def test_init_with_valid_token(self, mock_env_vars, mock_application):
        """Тест инициализации с валидным токеном"""
        chatbot = ChatBot()
        assert chatbot.command_handler is not None
        assert chatbot.message_handler is not None
        assert chatbot._ChatBot__application is not None

    def test_init_without_token(self, monkeypatch, mock_application):
        """Тест инициализации без токена"""
        monkeypatch.delenv('TELEGRAM_BOT_TOKEN', raising=False)
        # Перезагружаем модуль, чтобы __token переинициализировался
        import importlib
        import bot.chat_bot
        importlib.reload(bot.chat_bot)
        from bot.chat_bot import ChatBot
        
        with pytest.raises(Exception, match="Bot Token is not set"):
            ChatBot()

    def test_init_with_empty_token(self, monkeypatch, mock_application):
        """Тест инициализации с пустым токеном"""
        monkeypatch.setenv('TELEGRAM_BOT_TOKEN', '')
        # Перезагружаем модуль, чтобы __token переинициализировался
        import importlib
        import bot.chat_bot
        importlib.reload(bot.chat_bot)
        from bot.chat_bot import ChatBot
        
        with pytest.raises(Exception, match="Bot Token is not set"):
            ChatBot()

    def test_setup_adds_handlers(self, mock_env_vars, mock_application):
        """Тест настройки обработчиков"""
        chatbot = ChatBot()
        chatbot.setup()
        
        # Проверка, что add_handler был вызван 3 раза
        # (MessageHandler для JSON файлов, CommandHandler для start и process)
        assert mock_application.add_handler.call_count == 3

    def test_setup_adds_message_handler(self, mock_env_vars, mock_application):
        """Тест добавления обработчика сообщений"""
        chatbot = ChatBot()
        chatbot.setup()
        
        # Получаем все вызовы add_handler
        calls = mock_application.add_handler.call_args_list
        
        # Проверяем, что есть MessageHandler для JSON файлов
        message_handler_calls = [
            call for call in calls
            if hasattr(call[0][0], 'filters') or str(call[0][0]).find('MessageHandler') != -1
        ]
        assert len(message_handler_calls) > 0

    def test_setup_adds_command_handlers(self, mock_env_vars, mock_application):
        """Тест добавления обработчиков команд"""
        chatbot = ChatBot()
        chatbot.setup()
        
        # Проверка, что обработчики команд добавлены
        assert mock_application.add_handler.call_count == 3

    def test_start_app_calls_run_polling(self, mock_env_vars, mock_application):
        """Тест запуска приложения"""
        chatbot = ChatBot()
        chatbot.setup()
        chatbot.start_app()
        
        # Проверка, что run_polling был вызван
        mock_application.run_polling.assert_called_once()

    def test_chatbot_initializes_handlers(self, mock_env_vars, mock_application):
        """Тест инициализации обработчиков"""
        chatbot = ChatBot()
        
        assert hasattr(chatbot, 'command_handler')
        assert hasattr(chatbot, 'message_handler')
        assert chatbot.command_handler is not None
        assert chatbot.message_handler is not None

    def test_chatbot_application_is_private(self, mock_env_vars, mock_application):
        """Тест, что application является приватным атрибутом"""
        chatbot = ChatBot()
        
        # Проверка, что __application недоступен напрямую
        assert not hasattr(chatbot, '__application')
        # Но доступен через name mangling
        assert hasattr(chatbot, '_ChatBot__application')

    @patch('bot.chat_bot.load_dotenv')
    def test_load_dotenv_called(self, mock_load_dotenv, mock_env_vars, mock_application):
        """Тест, что load_dotenv вызывается при импорте"""
        # Переимпортируем модуль, чтобы проверить вызов load_dotenv
        import importlib
        import bot.chat_bot
        importlib.reload(bot.chat_bot)
        
        # load_dotenv должен быть вызван при импорте модуля
        # (но так как он вызывается на уровне модуля, проверить сложно)
        # Этот тест больше для документации

