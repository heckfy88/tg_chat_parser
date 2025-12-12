import pytest
from unittest.mock import patch, MagicMock
import runpy
import sys


class TestMain:
    """Тесты для main.py"""

    @patch('bot.chat_bot.Application')
    def test_main_creates_chatbot(self, mock_application_class, mock_env_vars):
        """Тест создания экземпляра ChatBot в main"""
        mock_app = MagicMock()
        mock_app.run_polling = MagicMock()
        mock_builder = MagicMock()
        mock_builder.token.return_value = mock_builder
        mock_builder.build.return_value = mock_app
        mock_application_class.builder.return_value = mock_builder
        
        if 'main' in sys.modules:
            del sys.modules['main']
        
        runpy.run_path('main.py', run_name='__main__')
        
        mock_application_class.builder.assert_called_once()

    @patch('bot.chat_bot.Application')
    def test_main_calls_setup(self, mock_application_class, mock_env_vars):
        """Тест вызова setup в main"""
        mock_app = MagicMock()
        mock_app.run_polling = MagicMock()
        mock_builder = MagicMock()
        mock_builder.token.return_value = mock_builder
        mock_builder.build.return_value = mock_app
        mock_application_class.builder.return_value = mock_builder
        
        if 'main' in sys.modules:
            del sys.modules['main']
        
        runpy.run_path('main.py', run_name='__main__')
        
        assert mock_app.add_handler.call_count >= 1

    @patch('bot.chat_bot.Application')
    def test_main_calls_start_app(self, mock_application_class, mock_env_vars):
        """Тест вызова start_app в main"""
        mock_app = MagicMock()
        mock_app.run_polling = MagicMock()
        mock_builder = MagicMock()
        mock_builder.token.return_value = mock_builder
        mock_builder.build.return_value = mock_app
        mock_application_class.builder.return_value = mock_builder
        
        if 'main' in sys.modules:
            del sys.modules['main']
        
        runpy.run_path('main.py', run_name='__main__')
        
        mock_app.run_polling.assert_called_once()

    @patch('bot.chat_bot.Application')
    def test_main_execution_order(self, mock_application_class, mock_env_vars):
        """Тест порядка выполнения в main"""
        mock_app = MagicMock()
        mock_app.run_polling = MagicMock()
        mock_builder = MagicMock()
        mock_builder.token.return_value = mock_builder
        mock_builder.build.return_value = mock_app
        mock_application_class.builder.return_value = mock_builder
        
        if 'main' in sys.modules:
            del sys.modules['main']
        
        runpy.run_path('main.py', run_name='__main__')
        
        calls = [str(call) for call in mock_app.method_calls]
        
        add_handler_calls = [i for i, call in enumerate(calls) if 'add_handler' in call]
        run_polling_calls = [i for i, call in enumerate(calls) if 'run_polling' in call]
        
        assert len(add_handler_calls) > 0
        assert len(run_polling_calls) > 0
        assert max(add_handler_calls) < min(run_polling_calls)

