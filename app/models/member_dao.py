# app/models/member_dao.py
# 2025.12.05 이태호
from typing import Dict, Any, Optional

MEMBER_TABLE = "MEMBER"

COL_ID = "ID"
COL_PASSWORD = "PASSWORD"
COL_NAME = "NAME"
COL_ADDRESS = "ADDRESS"
COL_SEX = "SEX"
COL_BIRTHDAY = "BIRTHDAY"
# 현재 스키마에는 관리자 컬럼이 없으므로 ISADMIN 관련 상수는 사용하지 않음


def _row_to_member_dict(row) -> Dict[str, Any]:
    """
    MEMBER 한 행(row)을 파이썬 dict로 변환
    순서는 get_member_by_id 의 SELECT 순서를 따른다.
    """
    return {
        "id": row[0],
        "password": row[1],
        "name": row[2],
        "address": row[3],
        "sex": row[4],
        "birthday": row[5],
        # DB에 컬럼은 없지만, 코드에서 안전하게 쓰도록 기본값 넣어줌
        "is_admin": False,
    }


def get_member_by_id(conn, user_id: str) -> Optional[Dict[str, Any]]:
    cursor = conn.cursor()
    sql = f"""
        SELECT
            {COL_ID},
            {COL_PASSWORD},
            {COL_NAME},
            {COL_ADDRESS},
            {COL_SEX},
            {COL_BIRTHDAY}
        FROM {MEMBER_TABLE}
        WHERE {COL_ID} = :id
    """
    cursor.execute(sql, {"id": user_id})
    row = cursor.fetchone()
    if row is None:
        return None
    return _row_to_member_dict(row)


def insert_member(conn, member: Dict[str, Any]) -> None:
    cursor = conn.cursor()
    sql = f"""
        INSERT INTO {MEMBER_TABLE} (
            {COL_ID},
            {COL_PASSWORD},
            {COL_NAME},
            {COL_ADDRESS},
            {COL_SEX},
            {COL_BIRTHDAY}
        ) VALUES (
            :id,
            :password,
            :name,
            :address,
            :sex,
            TO_DATE(:birthday, 'YYYY-MM-DD')
        )
    """
    cursor.execute(
        sql,
        {
            "id": member["id"],
            "password": member["password"],
            "name": member["name"],
            "address": member.get("address"),
            "sex": member.get("sex"),
            "birthday": member.get("birthday"),
        },
    )


def update_member(conn, user_id: str, updates: Dict[str, Any]) -> None:
    cursor = conn.cursor()

    set_parts = []
    params = {"id": user_id}

    if updates.get("password"):
        set_parts.append(f"{COL_PASSWORD} = :password")
        params["password"] = updates["password"]

    if "address" in updates:
        set_parts.append(f"{COL_ADDRESS} = :address")
        params["address"] = updates["address"]

    if "sex" in updates:
        set_parts.append(f"{COL_SEX} = :sex")
        params["sex"] = updates["sex"]

    if "birthday" in updates:
        set_parts.append(f"{COL_BIRTHDAY} = TO_DATE(:birthday,'YYYY-MM-DD')")
        params["birthday"] = updates["birthday"]

    if not set_parts:
        return  # 변경할 값이 없으면 그냥 리턴

    sql = f"""
        UPDATE {MEMBER_TABLE}
        SET {', '.join(set_parts)}
        WHERE {COL_ID} = :id
    """
    cursor.execute(sql, params)
