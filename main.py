from bot.chat_bot import ChatBot


if __name__ == '__main__':
    print("Starting bot...")
    chatbot = ChatBot()
    chatbot.setup()
    chatbot.start_app()