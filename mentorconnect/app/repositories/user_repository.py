"""
app/repositories/user_repository.py
---------------------------------------
Data access methods specific to User/Role entities, beyond generic CRUD.
"""

from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.orm import Session, joinedload

from app.models.user import User, Role
from app.models.enums import RoleName, UserStatus
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email).options(joinedload(User.role))
        return self.db.execute(stmt).unique().scalar_one_or_none()

    def get_by_mobile(self, mobile_number: str) -> Optional[User]:
        stmt = select(User).where(User.mobile_number == mobile_number)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_with_role(self, user_id: int) -> Optional[User]:
        stmt = select(User).where(User.id == user_id).options(joinedload(User.role))
        return self.db.execute(stmt).unique().scalar_one_or_none()

    def email_exists(self, email: str) -> bool:
        stmt = select(func.count()).select_from(User).where(User.email == email)
        return self.db.execute(stmt).scalar_one() > 0

    def mobile_exists(self, mobile_number: str) -> bool:
        stmt = select(func.count()).select_from(User).where(User.mobile_number == mobile_number)
        return self.db.execute(stmt).scalar_one() > 0

    def list_by_status(self, status: UserStatus, skip: int = 0, limit: int = 20) -> List[User]:
        stmt = select(User).where(User.status == status).offset(skip).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def count_by_status(self, status: UserStatus) -> int:
        stmt = select(func.count()).select_from(User).where(User.status == status)
        return self.db.execute(stmt).scalar_one()

    def count_all(self) -> int:
        stmt = select(func.count()).select_from(User)
        return self.db.execute(stmt).scalar_one()


class RoleRepository(BaseRepository[Role]):
    def __init__(self, db: Session):
        super().__init__(Role, db)

    def get_by_name(self, name: RoleName) -> Optional[Role]:
        stmt = select(Role).where(Role.name == name)
        return self.db.execute(stmt).scalar_one_or_none()
