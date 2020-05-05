class WrongChatException(Exception):
    def __init__(self, dialog):
        if dialog == 2:
            self.message = 'This command is not available in a group. Use it in a private chat'
        elif dialog == 1:
            self.message = 'This command is not available in a private chat. Use it in a group'
