from importlib import import_module

from sqlalchemy.orm import Mapped, mapped_column
from .services.permissionsservice import UserCategory

from .config import SQLAModelBase

class User(SQLAModelBase):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    category: Mapped[UserCategory]
    is_active: Mapped[bool]
