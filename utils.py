
from objects import ApiError

def raise_api_error(code=34, message="Raises programmatically"):

    raise ApiError([{'code': code, 'message': message}])