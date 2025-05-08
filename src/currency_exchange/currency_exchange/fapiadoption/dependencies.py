from typing import Annotated

from fastapi import Depends

from currency_exchange.auth import get_user_from_bearer_token
from currency_exchange.auth.schemas import UserDbOut


user_dependency = Annotated[UserDbOut, Depends(get_user_from_bearer_token)]
