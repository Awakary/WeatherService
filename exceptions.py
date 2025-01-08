from fastapi import HTTPException


class ExceptionWithMessage(HTTPException):
    def __init__(self, status_code=400, detail='Ошибка'):
        self.detail = detail
        self.status_code = status_code


class UsernameExistsException(ExceptionWithMessage):
    def __init__(self):
        super().__init__(status_code=400, detail='Пользователь с таким логином уже существует')
        # self.message = 'Пользователь с таким логином уже существует'


class UsernamePasswordException(ExceptionWithMessage):
    def __init__(self):
        super().__init__(status_code=400, detail='Имя пользователя и пароль '
                                                 'должны содержать только латинские буквы и цифры')


class SameLocationException(ExceptionWithMessage):
    def __init__(self):
        super().__init__(status_code=400, detail='Location already exists')


class NotSamePasswordException(ExceptionWithMessage):
    def __init__(self):
        super().__init__(status_code=400, detail='Введенные пароли должны быть одинаковыми')




