"""Служебные команды. Роль выдаётся только отсюда либо действующим админом.

    python manage.py set-role admin@shop.com admin
    python manage.py list-users
"""
import sys

from app.database import SessionLocal
from app.auth.models.user import User
from app.auth.schemas.user import Role
from typing import get_args

ROLES = get_args(Role)


def set_role(email: str, role: str) -> int:
    if role not in ROLES:
        print(f"Роль должна быть одной из: {', '.join(ROLES)}")
        return 1

    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    if not user:
        print(f"Пользователь {email} не найден. Сначала зарегистрируйтесь через сайт.")
        return 1

    user.role = role
    db.commit()
    print(f"{email}: роль теперь {role}")
    return 0


def list_users() -> int:
    db = SessionLocal()
    users = db.query(User).order_by(User.id).all()
    if not users:
        print("Пользователей нет")
        return 0

    for u in users:
        print(f"{u.id:>4}  {u.role:<7} {u.email}")
    return 0


if __name__ == "__main__":
    match sys.argv[1:]:
        case ["set-role", email, role]:
            sys.exit(set_role(email, role))
        case ["list-users"]:
            sys.exit(list_users())
        case _:
            print(__doc__)
            sys.exit(1)
