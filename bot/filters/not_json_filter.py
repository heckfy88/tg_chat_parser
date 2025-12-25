from telegram.ext.filters import MessageFilter
from telegram import Update

class NotJsonDocument(MessageFilter):
    name = "not_json_document"

    def filter(self, message) -> bool:
        doc = message.document
        if not doc or not doc.file_name:
            return False
        return not doc.file_name.lower().endswith(".json")