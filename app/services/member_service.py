# 2025.12.08 이태호
from app.db import db
from app.models import member_dao


class MemberServiceError(Exception):
    """일반 회원 서비스 에러"""
    pass


class InvalidLoginError(MemberServiceError):
    """로그인 실패 에러"""
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
    """
    form: {
        "id": str,
        "password": str,
        "name": str,
        "address": str | None,
        "sex": str | None,
        "birthday": str (YYYY-MM-DD) | None
    }
    """
    conn = db.get_db()
    if conn is None:
        raise MemberServiceError("데이터베이스 연결에 실패했습니다. 관리자에게 문의하세요.")

    user_id = form.get("id")
    password = form.get("password")
    name = form.get("name")
    address = form.get("address")
    sex = form.get("sex")
    birthday = form.get("birthday")

    if not user_id or not password or not name:
        raise MemberServiceError("아이디, 비밀번호, 이름은 필수 입력값입니다.")

    # 아이디 중복 체크
    existing = member_dao.get_member_by_id(conn, user_id)
    if existing is not None:
        raise MemberServiceError("이미 존재하는 아이디입니다.")

    member = {
        "id": user_id,
        "password": password,
        "name": name,
        "address": address,
        "sex": sex,
        "birthday": birthday,
    }

    member_dao.insert_member(conn, member)
    conn.commit()  # 실제 DB 반영

    return True


def get_profile(user_id: str):
    conn = db.get_db()
    if conn is None:
        raise MemberServiceError("데이터베이스 연결에 실패했습니다. 관리자에게 문의하세요.")

    member = member_dao.get_member_by_id(conn, user_id)
    if member is None:
        raise MemberServiceError("회원 정보를 찾을 수 없습니다.")

    return member


def update_profile(user_id: str, form):
    """
    form: {
        "password": str | None,
        "address": str | None,
        "sex": str | None,
        "birthday": str (YYYY-MM-DD) | None
    }
    """
    conn = db.get_db()
    if conn is None:
        raise MemberServiceError("데이터베이스 연결에 실패했습니다. 관리자에게 문의하세요.")

    updates = {}
    if form.get("password"):
        updates["password"] = form["password"]
    if "address" in form:
        updates["address"] = form["address"]
    if "sex" in form:
        updates["sex"] = form["sex"]
    if "birthday" in form:
        updates["birthday"] = form["birthday"]

    if not updates:
        # 바꿀 것이 없으면 그냥 반환
        return

    member_dao.update_member(conn, user_id, updates)
    conn.commit()
