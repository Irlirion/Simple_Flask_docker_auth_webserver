''' Wrapper for returning REST friendly error messages '''


class ApiError(dict):
    def __init__(self, status, message):
        super().__init__()
        self.update({'status': status, 'message': message})

    def __call__(self):
        return self, self['status']



UserAlreadyExist = ApiError(401, 'A user with that email already exists')

InvalidCredentials = ApiError(401, 'Invalid email or password')

UserDoesntExist = ApiError(401, 'User doesn`t exist ')
