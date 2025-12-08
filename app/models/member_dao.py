# app/models/member_dao.py
# 2025.12.05 이태호

from typing import Optional, Dict, Any, List

MEMBER_TABLE = "MEMBER"

COL_ID = "ID"
COL_PASSWORD = "Password"
COL_NAME = "Name"
COL_ADDRESS = "Address"
COL_SEX = "Sex"
COL_BIRTHDAY = "Birthday"


def _row_to_member_dict(row) -> Dict[str, Any]:
    if row is None:
        return {}
    return {
        "id": row[0],
        "password": row[1],
        "name": row[2],
        "address": row[3],
        "sex": row[4],
        "birthday": row[5],
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


def is_id_exists(conn, user_id: str) -> bool:
    cursor = conn.cursor()
    sql = f"""
        SELECT 1
        FROM {MEMBER_TABLE}
        WHERE {COL_ID} = :id
    """
    cursor.execute(sql, {"id": user_id})
    return cursor.fetchone() is not None


def create_member(conn, member_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    member_data 예:
    {
        "id": "testuser1",
        "password": "1234",
        "name": "홍길동",
        "address": "대구시 어딘가",
        "sex": "M" 또는 "F" 또는 None,
        "birthday": "2000-01-01" 또는 None
    }
    """
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
            CASE
                WHEN :birthday IS NULL THEN NULL
                ELSE TO_DATE(:birthday, 'YYYY-MM-DD')
            END
        )
    """
    cursor.execute(
        sql,
        {
            "id": member_data["id"],
            "password": member_data["password"],
            "name": member_data["name"],
            "address": member_data.get("address"),
            "sex": member_data.get("sex"),
            "birthday": member_data.get("birthday"),
        },
    )

    return get_member_by_id(conn, member_data["id"])


def update_member(conn, user_id: str, member_data: Dict[str, Any]) -> None:
    """
    비밀번호/주소만 수정 (템플릿 구조에 맞춤)
    member_data:
    {
        "password": "새비번 또는 기존비번",
        "address": "새주소 또는 None"
    }
    """
    cursor = conn.cursor()
    sql = f"""
        UPDATE {MEMBER_TABLE}
        SET
            {COL_PASSWORD} = :password,
            {COL_ADDRESS} = :address
        WHERE {COL_ID} = :id
    """
    cursor.execute(
        sql,
        {
            "password": member_data["password"],
            "address": member_data.get("address"),
            "id": user_id,
        },
    )


def list_members(conn) -> List[Dict[str, Any]]:
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
        ORDER BY {COL_ID}
    """
    cursor.execute(sql)
    rows = cursor.fetchall()
    return [_row_to_member_dict(row) for row in rows]
