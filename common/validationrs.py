from rest_framework.exceptions import ParseError


class Time15MinutesValidator:
    message = 'Время доллжно быть кратно 15 минутам.'

    def __call__(self, value):
        if not value:
            return
        if value.minute % 15 > 0:
            raise ParseError(self.message)
