# Описание тестов

## test_command_handler.py

### TestExtractText

- `test_extract_text_from_string` - извлечение текста из строки
- `test_extract_text_from_list_of_strings` - извлечение текста из списка строк
- `test_extract_text_from_list_with_dicts` - извлечение текста из списка со словарями
- `test_extract_text_from_mixed_list` - извлечение текста из смешанного списка
- `test_extract_text_from_empty_string` - обработка пустой строки
- `test_extract_text_from_empty_list` - обработка пустого списка
- `test_extract_text_from_invalid_type` - обработка невалидного типа
- `test_extract_text_from_dict_without_text_key` - обработка словаря без ключа text

### TestGenerateExcel

- `test_generate_excel_basic` - генерация Excel с базовыми данными
- `test_generate_excel_empty_participants` - генерация Excel с пустым списком участников
- `test_generate_excel_with_missing_username` - генерация Excel с отсутствующим username

### TestBotCommandHandler

- `test_init_with_valid_threshold` - инициализация с валидным порогом
- `test_init_with_negative_threshold` - инициализация с отрицательным порогом (должна выбрасывать исключение)
- `test_start_command` - команда /start (инициализация files, отправка инструкций)
- `test_extract_participants_from_files_basic` - извлечение участников из файлов (базовый случай)
- `test_extract_participants_from_files_with_username_regex` - извлечение упоминаний через регулярное выражение
- `test_extract_participants_from_files_invalid_json` - обработка невалидного JSON
- `test_extract_participants_from_files_empty_messages` - обработка файла с пустым списком сообщений
- `test_extract_participants_from_files_missing_from_id` - обработка сообщений без from_id
- `test_process_command_text_output` - команда /process с текстовым выводом (мало участников)
- `test_process_command_excel_output` - команда /process с выводом в Excel (много участников)
- `test_process_command_no_participants` - команда /process без участников
- `test_extract_participants_multiple_files` - извлечение участников из нескольких файлов

## test_message_handler.py

### TestJsonMessageHandler

- `test_init_with_valid_env_vars` - инициализация с валидными переменными окружения
- `test_handle_file_valid_json` - обработка валидного JSON файла
- `test_handle_file_invalid_extension` - обработка файла с невалидным расширением
- `test_handle_file_case_insensitive_extension` - обработка файла с расширением в разных регистрах
- `test_handle_file_too_large` - обработка файла, превышающего максимальный размер
- `test_handle_file_exact_max_size` - обработка файла с максимально допустимым размером
- `test_handle_file_max_files_reached` - обработка файла при достижении максимального количества
- `test_handle_file_at_max_files_amount` - обработка файла, когда достигнуто максимальное количество
- `test_handle_file_multiple_files` - обработка нескольких файлов подряд
- `test_handle_file_with_existing_files` - обработка файла, когда уже есть другие файлы
- `test_handle_file_empty_user_data` - обработка файла с пустым user_data
- `test_handle_file_no_files_key_in_user_data` - обработка файла, когда в user_data нет ключа files

## test_chat_bot.py

### TestChatBot

- `test_init_with_valid_token` - инициализация с валидным токеном
- `test_init_without_token` - инициализация без токена (должна выбрасывать исключение)
- `test_init_with_empty_token` - инициализация с пустым токеном (должна выбрасывать исключение)
- `test_setup_adds_handlers` - настройка обработчиков (проверка количества вызовов add_handler)
- `test_setup_adds_message_handler` - добавление обработчика сообщений
- `test_setup_adds_command_handlers` - добавление обработчиков команд
- `test_start_app_calls_run_polling` - запуск приложения (проверка вызова run_polling)
- `test_chatbot_initializes_handlers` - инициализация обработчиков
- `test_chatbot_application_is_private` - проверка, что application является приватным атрибутом
- `test_load_dotenv_called` - проверка вызова load_dotenv при импорте

## test_main.py

### TestMain

- `test_main_creates_chatbot` - создание экземпляра ChatBot в main
- `test_main_calls_setup` - вызов setup в main
- `test_main_calls_start_app` - вызов start_app в main
- `test_main_execution_order` - порядок выполнения в main (setup перед start_app)

