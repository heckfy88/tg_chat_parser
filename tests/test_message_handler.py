import pytest
from unittest.mock import MagicMock, AsyncMock

from bot.handlers.message_handler import CustomMessageHandler


class TestJsonMessageHandler:
    """Тесты для класса CustomMessageHandler"""

    @pytest.fixture
    def handler(self, mock_env_vars):
        """Фикстура для создания экземпляра CustomMessageHandler"""
        return CustomMessageHandler()

    def test_init_with_valid_env_vars(self, mock_env_vars):
        """Тест инициализации с валидными переменными окружения"""
        handler = CustomMessageHandler()
        assert handler._max_file_size == 20
        assert handler._max_files_amount == 5

    @pytest.mark.asyncio
    async def test_handle_file_valid_json(self, handler, mock_update, mock_context):
        """Тест обработки валидного JSON файла"""
        mock_update.message.document.file_name = "test.json"
        mock_update.message.document.file_size = 1000
        
        mock_context.user_data = {}
        
        await handler.handle_file(mock_update, mock_context)
        
        assert len(mock_context.user_data["files"]) == 1
        assert mock_context.user_data["files"][0] == mock_update.message.document
        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "Добавлен файл: test.json" in call_args
        assert "Всего файлов: 1" in call_args

    @pytest.mark.asyncio
    async def test_handle_file_invalid_extension(self, handler, mock_update, mock_context):
        """Тест обработки файла с невалидным расширением"""
        mock_update.message.document.file_name = "test.txt"
        mock_update.message.document.file_size = 1000
        
        mock_context.user_data = {}
        
        await handler.handle_file(mock_update, mock_context)
        
        # Проверка, что файл не добавлен
        assert "files" not in mock_context.user_data or len(mock_context.user_data.get("files", [])) == 0
        
        # Проверка отправки сообщения об ошибке
        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "Принимаю только JSON-файлы" in call_args

    @pytest.mark.asyncio
    async def test_handle_file_case_insensitive_extension(self, handler, mock_update, mock_context):
        """Тест обработки файла с расширением в разных регистрах"""
        mock_update.message.document.file_name = "test.JSON"
        mock_update.message.document.file_size = 1000
        
        mock_context.user_data = {}
        
        await handler.handle_file(mock_update, mock_context)
        
        assert len(mock_context.user_data["files"]) == 1

    @pytest.mark.asyncio
    async def test_handle_file_too_large(self, handler, mock_update, mock_context):
        """Тест обработки файла, превышающего максимальный размер"""
        mock_update.message.document.file_name = "test.json"
        mock_update.message.document.file_size = 21 * 1000 * 1000
        
        mock_context.user_data = {}
        
        await handler.handle_file(mock_update, mock_context)
        
        assert "files" not in mock_context.user_data or len(mock_context.user_data.get("files", [])) == 0
        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "Размер файла превышает максимально допустимый" in call_args

    @pytest.mark.asyncio
    async def test_handle_file_exact_max_size(self, handler, mock_update, mock_context):
        """Тест обработки файла с максимально допустимым размером"""
        mock_update.message.document.file_name = "test.json"
        mock_update.message.document.file_size = 20 * 1000 * 1000
        
        mock_context.user_data = {}
        
        await handler.handle_file(mock_update, mock_context)
        
        assert len(mock_context.user_data["files"]) == 1

    @pytest.mark.asyncio
    async def test_handle_file_max_files_reached(self, handler, mock_update, mock_context):
        """Тест обработки файла при достижении максимального количества"""
        handler._max_files_amount = 2
        
        mock_update.message.document.file_name = "test2.json"
        mock_update.message.document.file_size = 1000
        
        mock_context.user_data = {
            "files": [MagicMock(), MagicMock()]
        }
        
        await handler.handle_file(mock_update, mock_context)
        
        assert len(mock_context.user_data["files"]) == 2
        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "Превышено максимально допустимое количество файлов" in call_args

    @pytest.mark.asyncio
    async def test_handle_file_at_max_files_amount(self, handler, mock_update, mock_context):
        """Тест обработки файла, когда достигнуто максимальное количество"""
        handler._max_files_amount = 3
        
        mock_update.message.document.file_name = "test3.json"
        mock_update.message.document.file_size = 1000
        
        mock_context.user_data = {
            "files": [MagicMock(), MagicMock()]
        }
        
        await handler.handle_file(mock_update, mock_context)
        
        assert len(mock_context.user_data["files"]) == 3
        calls = mock_update.message.reply_text.call_args_list
        call_texts = [call[0][0] for call in calls]
        assert any("введите команду обработки" in text for text in call_texts)

    @pytest.mark.asyncio
    async def test_handle_file_multiple_files(self, handler, mock_update, mock_context):
        """Тест обработки нескольких файлов подряд"""
        handler._max_files_amount = 5
        
        mock_update.message.document.file_name = "test1.json"
        mock_update.message.document.file_size = 1000
        mock_context.user_data = {}
        
        await handler.handle_file(mock_update, mock_context)
        assert len(mock_context.user_data["files"]) == 1
        
        mock_doc2 = MagicMock()
        mock_doc2.file_name = "test2.json"
        mock_doc2.file_size = 2000
        mock_update.message.document = mock_doc2
        
        await handler.handle_file(mock_update, mock_context)
        assert len(mock_context.user_data["files"]) == 2

    @pytest.mark.asyncio
    async def test_handle_file_with_existing_files(self, handler, mock_update, mock_context):
        """Тест обработки файла, когда уже есть другие файлы"""
        mock_update.message.document.file_name = "test2.json"
        mock_update.message.document.file_size = 1000
        
        existing_file = MagicMock()
        mock_context.user_data = {"files": [existing_file]}
        
        await handler.handle_file(mock_update, mock_context)
        
        assert len(mock_context.user_data["files"]) == 2
        assert mock_context.user_data["files"][0] == existing_file
        assert mock_context.user_data["files"][1] == mock_update.message.document

    @pytest.mark.asyncio
    async def test_handle_file_empty_user_data(self, handler, mock_update, mock_context):
        """Тест обработки файла с пустым user_data"""
        mock_update.message.document.file_name = "test.json"
        mock_update.message.document.file_size = 1000
        
        mock_context.user_data = {}
        
        await handler.handle_file(mock_update, mock_context)
        
        assert len(mock_context.user_data["files"]) == 1

    @pytest.mark.asyncio
    async def test_handle_file_no_files_key_in_user_data(self, handler, mock_update, mock_context):
        """Тест обработки файла, когда в user_data нет ключа files"""
        mock_update.message.document.file_name = "test.json"
        mock_update.message.document.file_size = 1000
        
        mock_context.user_data = {"other_key": "value"}
        
        await handler.handle_file(mock_update, mock_context)
        
        assert len(mock_context.user_data["files"]) == 1

