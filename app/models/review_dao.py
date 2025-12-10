# 12.09 anton061311
# 12.10 anotn061311 리뷰 조회 DAO 추가. 
#       def get_review_by_member()
# ----------------------------------------------------

from typing import Any, Dict, Optional

TABLE = "RATING"


def insert_review(conn, member_id: str, content_id: int, rating: int, comment: str) -> None:
    """
    새 리뷰 INSERT.
    Likes는 0으로 시작.
    """
    cursor = conn.cursor()
    sql = f"""
        INSERT INTO {TABLE} (MID, CID, Rating, Comm, Likes)
        VALUES (:mid, :cid, :rating, :comm, 0)
    """
    cursor.execute(
        sql,
        {
            "mid": member_id,
            "cid": content_id,
            "rating": rating,
            "comm": comment if comment else None,
        },
    )


def get_review_by_member_and_content(conn, member_id: str, content_id: int) -> Optional[Dict[str, Any]]:
    """
    같은 사용자가 같은 콘텐츠에 리뷰를 이미 썼는지 확인.
    """
    cursor = conn.cursor()
    sql = f"""
        SELECT MID, CID, Rating, Comm, Likes
        FROM {TABLE}
        WHERE MID = :mid AND CID = :cid
    """
    cursor.execute(sql, {"mid": member_id, "cid": content_id})
    row = cursor.fetchone()
    cursor.close()

    if not row:
        return None

    return {
        "mid": row[0],
        "cid": row[1],
        "rating": row[2],
        "comm": row[3],
        "likes": row[4],
    }


def get_review_for_update(conn, review_member_id: str, content_id: int) -> Optional[Dict[str, Any]]:
    """
    좋아요 증가 시 동시성 제어용.
    해당 리뷰 행에 SELECT ... FOR UPDATE로 락을 건다.

    Args:
        review_member_id: 리뷰를 쓴 사용자 ID (MID)
        content_id: 콘텐츠 ID (CID)
    """
    cursor = conn.cursor()
    sql = f"""
        SELECT MID, CID, Likes
        FROM {TABLE}
        WHERE MID = :mid AND CID = :cid
        FOR UPDATE
    """
    cursor.execute(sql, {"mid": review_member_id, "cid": content_id})
    row = cursor.fetchone()
    cursor.close()

    if not row:
        return None

    return {
        "mid": row[0],
        "cid": row[1],
        "likes": row[2],
    }

def get_reviews_by_member(conn, member_id: str):
    cursor = conn.cursor()
    sql = """
        SELECT r.MID, r.CID, r.Rating, r.Comm, r.Likes
        FROM RATING r
        WHERE r.MID = :mid
        ORDER BY r.CID DESC
    """
    cursor.execute(sql, {"mid": member_id})

    columns = [col[0].lower() for col in cursor.description]
    rows = [dict(zip(columns, row)) for row in cursor.fetchall()]

    cursor.close()
    return rows



def update_likes(conn, review_member_id: str, content_id: int, new_likes: int) -> None:
    """
    좋아요 수 업데이트.
    """
    cursor = conn.cursor()
    sql = f"""
        UPDATE {TABLE}
        SET Likes = :likes
        WHERE MID = :mid AND CID = :cid
    """
    cursor.execute(
        sql,
        {"likes": new_likes, "mid": review_member_id, "cid": content_id},
    )
    cursor.close()
