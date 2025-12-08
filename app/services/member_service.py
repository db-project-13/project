# app/services/member_service.py
# 2025.12.05 이태호

from typing import Optional, Dict, Any

from app.db import db
from app.models import member_dao


class MemberServiceError(Exception):
    """일반적인 회원 관련 예외."""
    pass


class DuplicateIdError(MemberServiceError):
    """아이디 중복 예외."""
    pass


class InvalidLoginError(MemberServiceError):
    """로그인 실패 예외."""
    pass


def login(user_id: str, password: str) -> Dict[str, Any]:
    """
    로그인 처리:
    - 성공: 회원 dict 리턴
    - 실패: InvalidLoginError 발생
    """
    conn = db.get_db()
    member = member_dao.get_member_by_id(conn, user_id)

    if member is None or member["password"] != password:
        raise InvalidLoginError("아이디 또는 비밀번호가 올바르지 않습니다.")

    return member


def register_member(form_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    회원가입 처리.
    register.html의 form name 기준:
    - id, password, name, address, sex, birthday
    """
    user_id = (form_data.get("id") or "").strip()
    password = (form_data.get("password") or "").strip()
    name = (form_data.get("name") or "").strip()
    address = (form_data.get("address") or "").strip()
    sex = (form_data.get("sex") or "").strip()
    birthday = (form_data.get("birthday") or "").strip()

    if not user_id or not password or not name:
        raise MemberServiceError("아이디, 비밀번호, 이름은 필수입니다.")

    if sex == "":
        sex = None
    if birthday == "":
        birthday = None

    conn = db.get_db()
    try:
        if member_dao.is_id_exists(conn, user_id):
            raise DuplicateIdError("이미 사용 중인 아이디입니다.")

        member_data = {
            "id": user_id,
            "password": password,
            "name": name,
            "address": address if address else None,
            "sex": sex,
            "birthday": birthday,
        }

        new_member = member_dao.create_member(conn, member_data)
        conn.commit()
        return new_member

    except Exception:
        conn.rollback()
        raise


def get_profile(user_id: str) -> Optional[Dict[str, Any]]:
    conn = db.get_db()
    return member_dao.get_member_by_id(conn, user_id)


def update_profile(user_id: str, form_data: Dict[str, Any]) -> None:
    """
    profile_edit.html 기준:
    - password(비워두면 유지), address
    """
    new_password = (form_data.get("password") or "").strip()
    new_address = (form_data.get("address") or "").strip()

    conn = db.get_db()
    try:
        current = member_dao.get_member_by_id(conn, user_id)
        if current is None:
            raise MemberServiceError("회원 정보를 찾을 수 없습니다.")

        if not new_password:
            new_password = current["password"]

        member_data = {
            "password": new_password,
            "address": new_address if new_address else None,
        }

        member_dao.update_member(conn, user_id, member_data)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
