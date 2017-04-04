class SequenceException(Exception):
    def __init__(self, sequence, message):
        self.sequence = sequence
        self.message = message

    def __str__(self):
        return '(message={}, sequence={})'.format(self.message, self.sequence)

    def __repr__(self):
        return '<{} {}>'.format(self.__class__.__name__, self)


class SequenceCommandException(SequenceException):
    def __init__(self, sequence_command, message):
        super(SequenceCommandException, self).__init__(sequence_command._sequence, message)
        self.command = sequence_command

    def __str__(self):
        return '(message={}, command={})'.format(self.message, self.command)
