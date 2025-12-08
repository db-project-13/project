# 2025.12.08 이태호
from app.db import db
from app.models import member_dao

class MemberServiceError(Exception):
    pass

class InvalidLoginError(MemberServiceError):
    pass


def login(user_id: str, password: str):
    conn = db.get_db()
    if conn is None:
        raise MemberServiceError("데이터베이스 연결에 실패했습니다. 관리자에게 문의하세요.")

    member = member_dao.get_member_by_id(conn, user_id)

    if member is None or member["password"] != password:
        raise InvalidLoginError("아이디 또는 비밀번호가 올바르지 않습니다.")

    return member


def register(form):
    conn = db.get_db()
    if conn is None:
        raise MemberServiceError("데이터베이스 연결에 실패했습니다. 관리자에게 문의하세요.")

    user_id = form.get("user_id")
    password = form.get("password")
    name = form.get("name")
    email = form.get("email")

    if not user_id or not password or not name or not email:
        raise MemberServiceError("필수 입력값이 누락되었습니다.")

    existing = member_dao.get_member_by_id(conn, user_id)
    if existing is not None:
        raise MemberServiceError("이미 존재하는 아이디입니다.")

    member_dao.insert_member(conn, user_id, password, name, email)

    return True
