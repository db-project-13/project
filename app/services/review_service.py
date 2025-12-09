# 12/09 anton061311
# ----------------------------------------------------
from app.db import db
from app.models import review_dao
import oracledb

'''
class ReviewServiceError(Exception):
    pass


class ReviewAlreadyExistsError(ReviewServiceError):
    pass


class ReviewNotFoundError(ReviewServiceError):
    pass


def create_review(member_id: str, content_id: int, score: int, comment: str) -> None:
    """
    리뷰 작성.
    - 같은 사용자가 같은 콘텐츠에 중복 리뷰 못 쓰게 막기
    - 트랜잭션 안에서 INSERT 수행
    - (DB에 UNIQUE (MEMBER_ID, CONTENT_ID) 제약 있으면 ORA-00001 잡아도 OK)
    """
    with db.transaction() as conn:
        # 1) 이미 리뷰가 있는지 체크
        existing = review_dao.get_review_by_member_and_content(conn, member_id, content_id)
        if existing is not None:
            raise ReviewAlreadyExistsError("이미 이 콘텐츠에 작성한 리뷰가 있습니다.")

        # 2) 신규 리뷰 INSERT
        try:
            review_dao.insert_review(conn, member_id, content_id, score, comment)
        except oracledb.IntegrityError as e:
            # UNIQUE 제약 위반 등
            if "ORA-00001" in str(e):
                raise ReviewAlreadyExistsError("이미 이 콘텐츠에 작성한 리뷰가 있습니다.")
            raise


def like_review(member_id: str, rating_id: int) -> None:
    """
    리뷰 좋아요.
    - SELECT ... FOR UPDATE 로 해당 리뷰 행을 잠그고
    - 현재 Likes 값을 읽은 뒤 +1 해서 UPDATE
    - 동시에 여러 사용자가 좋아요 눌러도 Likes 값이 꼬이지 않게 보장
    """
    with db.transaction() as conn:
        # 1) 대상 리뷰 행을 락 걸고 읽기
        row = review_dao.get_review_for_update(conn, rating_id)
        if row is None:
            raise ReviewNotFoundError("해당 리뷰를 찾을 수 없습니다.")

        current_likes = row["likes"]
        new_likes = current_likes + 1

        # 2) 좋아요 수 업데이트
        review_dao.update_likes(conn, rating_id, new_likes)
        # with 블록을 빠져나가면 commit
'''

from app.db import db
from app.models import review_dao
import oracledb


class ReviewServiceError(Exception):
    """리뷰 서비스 공통 예외"""
    pass


class ReviewAlreadyExistsError(ReviewServiceError):
    """이미 리뷰가 존재할 때"""
    pass


class ReviewNotFoundError(ReviewServiceError):
    """대상 리뷰를 찾을 수 없을 때"""
    pass


def create_review(member_id: str, content_id: int, rating: int, comment: str) -> None:
    """
    리뷰 작성 서비스.

    - 같은 사용자가 같은 콘텐츠에 중복 리뷰 못 쓰게 막기
    - 트랜잭션 안에서 INSERT 수행
    """
    with db.transaction() as conn:
        # 1) 기존 리뷰 존재 여부 검사
        existing = review_dao.get_review_by_member_and_content(conn, member_id, content_id)
        if existing is not None:
            raise ReviewAlreadyExistsError("이미 이 콘텐츠에 작성한 리뷰가 있습니다.")

        # 2) 신규 리뷰 INSERT
        try:
            review_dao.insert_review(conn, member_id, content_id, rating, comment)
        except oracledb.IntegrityError as e:
            # UNIQUE (MID, CID) 제약 등을 걸어놨다면 여기서도 중복 잡힘
            if "ORA-00001" in str(e):
                raise ReviewAlreadyExistsError("이미 이 콘텐츠에 작성한 리뷰가 있습니다.")
            raise


def like_review(actor_member_id: str, review_member_id: str, content_id: int) -> None:
    """
    리뷰 좋아요 서비스.

    - SELECT ... FOR UPDATE 로 해당 리뷰 행을 잠그고
    - 현재 Likes 값을 읽은 뒤 +1 해서 UPDATE
    - 동시에 여러 사용자가 좋아요 눌러도 Likes 값이 꼬이지 않게 보장
    """
    # actor_member_id(눌러주는 사람)는 과제에서 따로 쓰지 않지만,
    # 나중에 '자기 리뷰는 좋아요 못 누르게' 같은 검증에 활용 가능.
    with db.transaction() as conn:
        # 1) 대상 리뷰 행을 락 걸고 읽기
        row = review_dao.get_review_for_update(conn, review_member_id, content_id)
        if row is None:
            raise ReviewNotFoundError("해당 리뷰를 찾을 수 없습니다.")

        current_likes = row["likes"]
        new_likes = current_likes + 1

        # 2) 좋아요 수 업데이트
        review_dao.update_likes(conn, review_member_id, content_id, new_likes)
        # with 블록을 빠져나가면 commit
