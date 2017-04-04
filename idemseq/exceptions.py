class SequenceException(Exception):
    def __init__(self, sequence, message):
        self.sequence = sequence
        self.message = message


class SequenceCommandException(SequenceException):
    def __init__(self, sequence_command, message):
        super(SequenceCommandException, self).__init__(sequence_command._sequence, message)
        self.command = sequence_command
