
from Core.database import save_command_history

class CommandHistory:
    def __init__(self, question, response, timestamp):
        self.question = question
        self.response = response
        self.timestamp = timestamp

    def save(self):
        save_command_history(self.question, self.response)