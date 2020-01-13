from mycroft import MycroftSkill, intent_file_handler


class BookDialog(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('dialog.book.intent')
    def handle_dialog_book(self, message):
        self.speak_dialog('dialog.book')


def create_skill():
    return BookDialog()

