from telegram.ext.filters import MessageFilter
from telegram import Update

class NotSupportedDocument(MessageFilter):
    name = "not_supported_document"

    def filter(self, message) -> bool:
        doc = message.document
        if not doc or not doc.file_name:
            return False

        fname = doc.file_name.lower()
        return not (fname.endswith(".json") or fname.endswith(".html") or fname.endswith(".htm"))
