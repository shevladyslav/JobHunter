from aiogram.types import Message
from sqlalchemy.orm import Session

from models import User


class BaseService:
    def __init__(self, db_session: Session) -> None:
        self.db_session = db_session


class UserService(BaseService):
    def __init__(self, db_session: Session) -> None:
        super().__init__(db_session)

    def get_user_by_telegram_id(self, telegram_id: int) -> [User, None]:
        return (
            self.db_session.query(User).filter(User.telegram_id == telegram_id).first()
        )

    def _create_user(self, message: Message) -> User:
        user = User(
            telegram_id=message.from_user.id,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            username=message.from_user.username,
        )
        self.db_session.add(user)
        self.db_session.commit()
        return user

    def create_user(self, message: Message) -> User:
        existing_user = self.get_user_by_telegram_id(message.from_user.id)
        if not existing_user:
            return self._create_user(message)
        return existing_user
