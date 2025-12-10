# 12/09 anton061311
'''
"""
콘텐츠 및 리뷰 관리 Blueprint
"""
from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from app.utils.decorators import login_required
from app.db import db
import oracledb

content_bp = Blueprint('content', __name__, url_prefix='/content')


@content_bp.route('/movies')
def movies():
    """
    영화 목록 페이지 (ContentID: 2001 ~ 3000)
    """
    return _get_contents_by_theme(2001, 3000, '영화')


@content_bp.route('/games')
def games():
    """
    게임 목록 페이지 (ContentID: 301 ~ 1000)
    """
    return _get_contents_by_theme(301, 1000, '게임')


@content_bp.route('/books')
def books():
    """
    도서 목록 페이지 (ContentID: 1001 ~ 2000)
    """
    return _get_contents_by_theme(1001, 2000, '도서')


def _get_contents_by_theme(min_id, max_id, theme_name):
    """
    테마별 콘텐츠 목록 조회 헬퍼 함수 (ContentID 범위 기반)
    
    Args:
        min_id: ContentID 최소값
        max_id: ContentID 최대값
        theme_name: 테마 이름 (한글)
    """
    conn = db.get_db()
    cursor = conn.cursor()
    
    page = request.args.get('page', 1, type=int)
    per_page = 20
    offset = (page - 1) * per_page
    
    try:
        sql_list = """
            SELECT c.ContentID, c.Title, 
                   TO_CHAR(c.ReleaseDate, 'YYYY-MM-DD') as ReleaseDate,
                   p.Prodname, s.SName,
                   (SELECT ROUND(AVG(r.Rating), 1) FROM RATING r WHERE r.CID = c.ContentID) as AvgRating,
                   (SELECT COUNT(*) FROM RATING r WHERE r.CID = c.ContentID) as ReviewCount
            FROM CONTENT c
            JOIN PRODUCT_CO p ON c.PID = p.ProdcoID
            LEFT JOIN SERIES s ON c.SID = s.SeriesID
            WHERE c.ContentID >= :min_id AND c.ContentID <= :max_id
            ORDER BY c.ReleaseDate DESC
        """
        cursor.execute(sql_list, min_id=min_id, max_id=max_id)
        columns = [col[0].lower() for col in cursor.description]
        cursor.rowfactory = lambda *args: dict(zip(columns, args))
        all_contents = cursor.fetchall()
        
        total = len(all_contents)
        contents = all_contents[offset:offset + per_page]
        
    except Exception as e:
        flash(f'데이터 조회 중 오류 발생: {str(e)}', 'danger')
        contents = []
        total = 0
    finally:
        cursor.close()
    
    return render_template('content/theme_list.html',
                         theme_name=theme_name,
                         contents=contents,
                         page=page,
                         per_page=per_page,
                         total=total,
                         has_prev=page > 1,
                         has_next=offset + per_page < total)


@content_bp.route('/search', methods=['GET', 'POST'])
def search():
    """
    콘텐츠 검색 페이지 및 검색 처리
    
    GET: 검색 폼 표시
    POST: 검색 결과 표시
    """
    if request.method == 'POST':
        search_term = request.form.get('search_term', '').strip()
        tag = request.form.get('tag', '').strip() or None
        
        # 둘 다 비어있으면 에러
        if not search_term and not tag:
            flash('검색어 또는 태그를 입력해주세요.', 'error')
            return render_template('content/search.html')
        
        # ContentService를 통한 검색
        from app.services import content_service
        results = content_service.search_content(
            search_term=search_term if search_term else None,
            tag=tag
        )
        
        if len(results) > 0:
            flash(f'검색 결과: {len(results)}개', 'success')
        else:
            flash('검색 결과가 없습니다.', 'info')
        
        return render_template('content/search_results.html', 
                             results=results, 
                             search_term=search_term,
                             tag=tag)
    
    return render_template('content/search.html')


@content_bp.route('/<int:content_id>/review', methods=['GET', 'POST'])
@login_required
def create_review(content_id):
    """
    리뷰 등록 페이지 및 등록 처리
    
    Args:
        content_id: 콘텐츠 ID
    
    GET: 리뷰 등록 폼 표시
    POST: 리뷰 등록 처리
    """
    user_id = session.get('user_id')
    conn = db.get_db()
    cursor = conn.cursor()
    
    # 콘텐츠 정보 조회
    try:
        sql_content = """
            SELECT c.ContentID, c.Title
            FROM CONTENT c
            WHERE c.ContentID = :cid
        """
        cursor.execute(sql_content, cid=content_id)
        content_row = cursor.fetchone()
        
        if not content_row:
            flash('존재하지 않는 콘텐츠입니다.', 'danger')
            return redirect(url_for('main.index'))
        
        content = {
            'content_id': content_row[0],
            'title': content_row[1]
        }
        
        # 이미 리뷰가 있는지 확인
        sql_check = "SELECT COUNT(*) FROM RATING WHERE MID = :mid AND CID = :cid"
        cursor.execute(sql_check, mid=user_id, cid=content_id)
        if cursor.fetchone()[0] > 0:
            flash('이미 리뷰를 작성하셨습니다. 수정 기능을 이용해주세요.', 'warning')
            return redirect(url_for('content.detail', content_id=content_id))
        
    except Exception as e:
        flash(f'콘텐츠 조회 중 오류 발생: {str(e)}', 'danger')
        return redirect(url_for('main.index'))
    finally:
        cursor.close()
    
    if request.method == 'POST':
        conn = db.get_db()
        cursor = conn.cursor()
        
        try:
            rating = int(request.form.get('rating', 0))
            comment = request.form.get('comment', '').strip()
            
            if rating < 1 or rating > 5:
                flash('평점은 1-5 사이의 값이어야 합니다.', 'error')
                return render_template('content/review_form.html', content=content, action='create')
            
            # 리뷰 등록
            sql_insert = """
                INSERT INTO RATING (MID, CID, Rating, Comm, Likes)
                VALUES (:mid, :cid, :rating, :comm, 0)
            """
            cursor.execute(sql_insert, 
                         mid=user_id, 
                         cid=content_id, 
                         rating=rating, 
                         comm=comment if comment else None)
            conn.commit()
            
            flash('리뷰가 성공적으로 등록되었습니다.', 'success')
            return redirect(url_for('content.detail', content_id=content_id))
            
        except oracledb.IntegrityError:
            conn.rollback()
            flash('이미 리뷰를 작성하셨습니다. 수정 기능을 이용해주세요.', 'warning')
            return redirect(url_for('content.detail', content_id=content_id))
        except ValueError:
            flash('평점은 숫자로 입력해주세요.', 'error')
        except Exception as e:
            conn.rollback()
            flash(f'리뷰 등록 중 오류 발생: {str(e)}', 'danger')
        finally:
            cursor.close()
    
    return render_template('content/review_form.html', content=content, action='create')


@content_bp.route('/<int:content_id>')
def detail(content_id):
    """
    콘텐츠 상세 페이지
    
    Args:
        content_id: 콘텐츠 ID
    
    Returns:
        콘텐츠 상세 페이지 템플릿
    """
    conn = db.get_db()
    cursor = conn.cursor()
    user_id = session.get('user_id')
    
    try:
        # 1. 콘텐츠 기본 정보 조회
        sql_content = """
            SELECT c.ContentID, c.Title, 
                   TO_CHAR(c.ReleaseDate, 'YYYY-MM-DD') as ReleaseDate,
                   p.ProdcoID, p.Prodname, p.ProdInfo,
                   s.SeriesID, s.SName
            FROM CONTENT c
            JOIN PRODUCT_CO p ON c.PID = p.ProdcoID
            LEFT JOIN SERIES s ON c.SID = s.SeriesID
            WHERE c.ContentID = :cid
        """
        cursor.execute(sql_content, cid=content_id)
        content_row = cursor.fetchone()
        
        if not content_row:
            flash('존재하지 않는 콘텐츠입니다.', 'danger')
            return redirect(url_for('main.index'))
        
        columns = [col[0].lower() for col in cursor.description]
        content = dict(zip(columns, content_row))
        
        # 2. 태그 정보 조회 (카테고리별)
        sql_tags = """
            SELECT t.Category, LISTAGG(t.Tag, ', ') WITHIN GROUP (ORDER BY t.Tag) as Tags
            FROM TAG t
            JOIN TAG_TO tt ON t.TagCode = tt.TCode
            WHERE tt.CID = :cid
            GROUP BY t.Category
        """
        cursor.execute(sql_tags, cid=content_id)
        tags_by_category = {}
        for row in cursor.fetchall():
            tags_by_category[row[0]] = row[1]
        
        # 3. 구매처 정보 조회
        sql_shops = "SELECT MainURL, SubURL FROM SHOP WHERE CID = :cid ORDER BY MainURL"
        cursor.execute(sql_shops, cid=content_id)
        shops = []
        for row in cursor.fetchall():
            shops.append({'main_url': row[0], 'sub_url': row[1]})
        
        # 4. 리뷰 통계 조회
        sql_stats = """
            SELECT ROUND(AVG(Rating), 1) as AvgRating, 
                   COUNT(*) as ReviewCount,
                   COUNT(CASE WHEN Rating = 5 THEN 1 END) as Rating5,
                   COUNT(CASE WHEN Rating = 4 THEN 1 END) as Rating4,
                   COUNT(CASE WHEN Rating = 3 THEN 1 END) as Rating3,
                   COUNT(CASE WHEN Rating = 2 THEN 1 END) as Rating2,
                   COUNT(CASE WHEN Rating = 1 THEN 1 END) as Rating1
            FROM RATING
            WHERE CID = :cid
        """
        cursor.execute(sql_stats, cid=content_id)
        stats_row = cursor.fetchone()
        stats_columns = [col[0].lower() for col in cursor.description]
        stats = dict(zip(stats_columns, stats_row)) if stats_row else {
            'avgrating': None, 'reviewcount': 0, 'rating5': 0, 'rating4': 0, 
            'rating3': 0, 'rating2': 0, 'rating1': 0
        }
        
        # 5. 리뷰 목록 조회
        sql_reviews = """
            SELECT r.Rating, r.Comm, r.Likes, 
                   m.Name as MemberName, m.ID as MemberID
            FROM RATING r
            JOIN MEMBER m ON r.MID = m.ID
            WHERE r.CID = :cid
            ORDER BY r.Likes DESC NULLS LAST, r.Rating DESC, m.ID
        """
        cursor.execute(sql_reviews, cid=content_id)
        columns_review = [col[0].lower() for col in cursor.description]
        cursor.rowfactory = lambda *args: dict(zip(columns_review, args))
        reviews = cursor.fetchall()
        
        # 사용자가 작성한 리뷰 확인
        user_review = None
        if user_id:
            for review in reviews:
                if review['memberid'] == user_id:
                    user_review = review
                    break
        
    except Exception as e:
        flash(f'데이터 조회 중 오류 발생: {str(e)}', 'danger')
        content = None
        tags_by_category = {}
        shops = []
        stats = {'avgrating': None, 'reviewcount': 0}
        reviews = []
        user_review = None
    finally:
        cursor.close()
    
    if not content:
        return redirect(url_for('main.index'))
    
    return render_template('content/detail.html', 
                         content=content, 
                         tags_by_category=tags_by_category,
                         shops=shops,
                         stats=stats,
                         reviews=reviews,
                         user_review=user_review,
                         user_id=user_id)


@content_bp.route('/<int:content_id>/review/edit', methods=['GET', 'POST'])
@login_required
def update_review(content_id):
    """
    리뷰 수정 페이지 및 수정 처리
    
    Args:
        content_id: 콘텐츠 ID
    
    GET: 리뷰 수정 폼 표시
    POST: 리뷰 수정 처리
    """
    user_id = session.get('user_id')
    conn = db.get_db()
    cursor = conn.cursor()
    
    # 콘텐츠 정보 조회
    try:
        sql_content = """
            SELECT c.ContentID, c.Title
            FROM CONTENT c
            WHERE c.ContentID = :cid
        """
        cursor.execute(sql_content, cid=content_id)
        content_row = cursor.fetchone()
        
        if not content_row:
            flash('존재하지 않는 콘텐츠입니다.', 'danger')
            return redirect(url_for('main.index'))
        
        content = {
            'content_id': content_row[0],
            'title': content_row[1]
        }
        
        # 기존 리뷰 조회
        sql_review = """
            SELECT Rating, Comm
            FROM RATING
            WHERE MID = :mid AND CID = :cid
        """
        cursor.execute(sql_review, mid=user_id, cid=content_id)
        review_row = cursor.fetchone()
        
        if not review_row:
            flash('작성한 리뷰가 없습니다.', 'warning')
            return redirect(url_for('content.detail', content_id=content_id))
        
        review = {
            'rating': review_row[0],
            'comment': review_row[1] if review_row[1] else ''
        }
        
    except Exception as e:
        flash(f'데이터 조회 중 오류 발생: {str(e)}', 'danger')
        return redirect(url_for('content.detail', content_id=content_id))
    finally:
        cursor.close()
    
    if request.method == 'POST':
        conn = db.get_db()
        cursor = conn.cursor()
        
        try:
            rating = int(request.form.get('rating', 0))
            comment = request.form.get('comment', '').strip()
            
            if rating < 1 or rating > 5:
                flash('평점은 1-5 사이의 값이어야 합니다.', 'error')
                return render_template('content/review_form.html', 
                                    content=content, 
                                    review=review, 
                                    action='update')
            
            # 리뷰 수정
            sql_update = """
                UPDATE RATING 
                SET Rating = :rating, Comm = :comm
                WHERE MID = :mid AND CID = :cid
            """
            cursor.execute(sql_update, 
                         rating=rating, 
                         comm=comment if comment else None,
                         mid=user_id, 
                         cid=content_id)
            conn.commit()
            
            flash('리뷰가 성공적으로 수정되었습니다.', 'success')
            return redirect(url_for('content.detail', content_id=content_id))
            
        except ValueError:
            flash('평점은 숫자로 입력해주세요.', 'error')
        except Exception as e:
            conn.rollback()
            flash(f'리뷰 수정 중 오류 발생: {str(e)}', 'danger')
        finally:
            cursor.close()
    
    return render_template('content/review_form.html', 
                         content=content, 
                         review=review, 
                         action='update')


@content_bp.route('/<int:content_id>/review/delete', methods=['POST'])
@login_required
def delete_review(content_id):
    """
    리뷰 삭제 처리
    
    Args:
        content_id: 콘텐츠 ID
    """
    user_id = session.get('user_id')
    conn = db.get_db()
    cursor = conn.cursor()
    
    try:
        # 리뷰 삭제
        sql_delete = "DELETE FROM RATING WHERE MID = :mid AND CID = :cid"
        cursor.execute(sql_delete, mid=user_id, cid=content_id)
        
        if cursor.rowcount == 0:
            flash('삭제할 리뷰가 없습니다.', 'warning')
        else:
            conn.commit()
            flash('리뷰가 성공적으로 삭제되었습니다.', 'success')
        
    except Exception as e:
        conn.rollback()
        flash(f'리뷰 삭제 중 오류 발생: {str(e)}', 'danger')
    finally:
        cursor.close()
    
    return redirect(url_for('content.detail', content_id=content_id))
'''
"""
콘텐츠 및 리뷰 관리 Blueprint
"""

from flask import (
    Blueprint,
    render_template,
    request,
    session,
    redirect,
    url_for,
    flash,
)
from app.utils.decorators import login_required
from app.db import db
from app.services import review_service
import oracledb


content_bp = Blueprint("content", __name__, url_prefix="/content")


@content_bp.route("/movies")
def movies():
    """
    영화 목록 페이지 (ContentID: 2001 ~ 3000)
    """
    return _get_contents_by_theme(2001, 3000, "영화")


@content_bp.route("/games")
def games():
    """
    게임 목록 페이지 (ContentID: 301 ~ 1000)
    """
    return _get_contents_by_theme(301, 1000, "게임")


@content_bp.route("/books")
def books():
    """
    도서 목록 페이지 (ContentID: 1001 ~ 2000)
    """
    return _get_contents_by_theme(1001, 2000, "도서")


def _get_contents_by_theme(min_id, max_id, theme_name):
    """
    테마별 콘텐츠 목록 조회 헬퍼 함수 (ContentID 범위 기반)

    Args:
        min_id: ContentID 최소값
        max_id: ContentID 최대값
        theme_name: 테마 이름 (한글)
    """
    conn = db.get_db()
    cursor = conn.cursor()

    page = request.args.get("page", 1, type=int)
    per_page = 20
    offset = (page - 1) * per_page

    try:
        sql_list = """
            SELECT c.ContentID, c.Title, 
                   TO_CHAR(c.ReleaseDate, 'YYYY-MM-DD') as ReleaseDate,
                   p.Prodname, s.SName,
                   (SELECT ROUND(AVG(r.Rating), 1) FROM RATING r WHERE r.CID = c.ContentID) as AvgRating,
                   (SELECT COUNT(*) FROM RATING r WHERE r.CID = c.ContentID) as ReviewCount
            FROM CONTENT c
            JOIN PRODUCT_CO p ON c.PID = p.ProdcoID
            LEFT JOIN SERIES s ON c.SID = s.SeriesID
            WHERE c.ContentID >= :min_id AND c.ContentID <= :max_id
            ORDER BY c.ReleaseDate DESC
        """
        cursor.execute(sql_list, min_id=min_id, max_id=max_id)
        columns = [col[0].lower() for col in cursor.description]
        cursor.rowfactory = lambda *args: dict(zip(columns, args))
        all_contents = cursor.fetchall()

        total = len(all_contents)
        contents = all_contents[offset : offset + per_page]

    except Exception as e:
        flash(f"데이터 조회 중 오류 발생: {str(e)}", "danger")
        contents = []
        total = 0
    finally:
        cursor.close()

    return render_template(
        "content/theme_list.html",
        theme_name=theme_name,
        contents=contents,
        page=page,
        per_page=per_page,
        total=total,
        has_prev=page > 1,
        has_next=offset + per_page < total,
    )


@content_bp.route("/search", methods=["GET", "POST"])
def search():
    """
    콘텐츠 검색 페이지 및 검색 처리

    GET: 검색 폼 표시
    POST: 검색 결과 표시 (추후 ReviewService 연동)
    """
    if request.method == "POST":
        search_term = request.form.get("search_term", "").strip()

        if not search_term:
            flash("검색어를 입력해주세요.", "error")
            return render_template("content/search.html")

        # TODO: ReviewService를 통한 콘텐츠 검색
        results = []
        flash(
            f'"{search_term}" 검색 결과: {len(results)}개 (검색 기능은 추후 구현 예정)',
            "info",
        )

        return render_template(
            "content/search_results.html",
            results=results,
            search_term=search_term,
        )

    return render_template("content/search.html")


@content_bp.route("/<int:content_id>/review", methods=["GET", "POST"])
@login_required
def create_review(content_id):
    """
    리뷰 등록 페이지 및 등록 처리

    Args:
        content_id: 콘텐츠 ID

    GET: 리뷰 등록 폼 표시
    POST: 리뷰 등록 처리 (ReviewService 사용)
    """
    user_id = session.get("user_id")
    conn = db.get_db()
    cursor = conn.cursor()

    # 콘텐츠 정보 조회 + 기존 리뷰 존재 여부 확인
    try:
        sql_content = """
            SELECT c.ContentID, c.Title
            FROM CONTENT c
            WHERE c.ContentID = :cid
        """
        cursor.execute(sql_content, cid=content_id)
        content_row = cursor.fetchone()

        if not content_row:
            flash("존재하지 않는 콘텐츠입니다.", "danger")
            return redirect(url_for("main.index"))

        content = {
            "content_id": content_row[0],
            "title": content_row[1],
        }

        # 이미 리뷰가 있는지 확인 (뷰 단에서 한 번 더 안내용)
        sql_check = "SELECT COUNT(*) FROM RATING WHERE MID = :mid AND CID = :cid"
        cursor.execute(sql_check, mid=user_id, cid=content_id)
        if cursor.fetchone()[0] > 0 and request.method == "GET":
            flash("이미 리뷰를 작성하셨습니다. 수정 기능을 이용해주세요.", "warning")
            return redirect(url_for("content.detail", content_id=content_id))

    except Exception as e:
        flash(f"콘텐츠 조회 중 오류 발생: {str(e)}", "danger")
        return redirect(url_for("main.index"))
    finally:
        cursor.close()

    if request.method == "POST":
        try:
            rating = int(request.form.get("rating", 0))
        except ValueError:
            flash("평점은 숫자로 입력해주세요.", "error")
            return render_template(
                "content/review_form.html",
                content=content,
                action="create",
            )

        comment = request.form.get("comment", "").strip()

        if rating < 1 or rating > 5:
            flash("평점은 1-5 사이의 값이어야 합니다.", "error")
            return render_template(
                "content/review_form.html",
                content=content,
                action="create",
            )

        # ✅ 동시성 제어 포함된 ReviewService 사용
        try:
            review_service.create_review(user_id, content_id, rating, comment)
            flash("리뷰가 성공적으로 등록되었습니다.", "success")
            return redirect(url_for("content.detail", content_id=content_id))
        except review_service.ReviewAlreadyExistsError as e:
            flash(str(e), "warning")
            return redirect(url_for("content.detail", content_id=content_id))
        except review_service.ReviewServiceError as e:
            flash(str(e), "danger")
        except Exception as e:
            flash(f"리뷰 등록 중 오류 발생: {str(e)}", "danger")

    return render_template("content/review_form.html", content=content, action="create")


@content_bp.route("/<int:content_id>")
def detail(content_id):
    """
    콘텐츠 상세 페이지

    Args:
        content_id: 콘텐츠 ID

    Returns:
        콘텐츠 상세 페이지 템플릿
    """
    conn = db.get_db()
    cursor = conn.cursor()
    user_id = session.get("user_id")

    try:
        # 1. 콘텐츠 기본 정보 조회
        sql_content = """
            SELECT c.ContentID, c.Title, 
                   TO_CHAR(c.ReleaseDate, 'YYYY-MM-DD') as ReleaseDate,
                   p.ProdcoID, p.Prodname, p.ProdInfo,
                   s.SeriesID, s.SName
            FROM CONTENT c
            JOIN PRODUCT_CO p ON c.PID = p.ProdcoID
            LEFT JOIN SERIES s ON c.SID = s.SeriesID
            WHERE c.ContentID = :cid
        """
        cursor.execute(sql_content, cid=content_id)
        content_row = cursor.fetchone()

        if not content_row:
            flash("존재하지 않는 콘텐츠입니다.", "danger")
            return redirect(url_for("main.index"))

        columns = [col[0].lower() for col in cursor.description]
        content = dict(zip(columns, content_row))

        # 2. 태그 정보 조회 (카테고리별)
        sql_tags = """
            SELECT t.Category, LISTAGG(t.Tag, ', ') WITHIN GROUP (ORDER BY t.Tag) as Tags
            FROM TAG t
            JOIN TAG_TO tt ON t.TagCode = tt.TCode
            WHERE tt.CID = :cid
            GROUP BY t.Category
        """
        cursor.execute(sql_tags, cid=content_id)
        tags_by_category = {}
        for row in cursor.fetchall():
            tags_by_category[row[0]] = row[1]

        # 3. 구매처 정보 조회
        sql_shops = "SELECT MainURL, SubURL FROM SHOP WHERE CID = :cid ORDER BY MainURL"
        cursor.execute(sql_shops, cid=content_id)
        shops = []
        for row in cursor.fetchall():
            shops.append({"main_url": row[0], "sub_url": row[1]})

        # 4. 리뷰 통계 조회
        sql_stats = """
            SELECT ROUND(AVG(Rating), 1) as AvgRating, 
                   COUNT(*) as ReviewCount,
                   COUNT(CASE WHEN Rating = 5 THEN 1 END) as Rating5,
                   COUNT(CASE WHEN Rating = 4 THEN 1 END) as Rating4,
                   COUNT(CASE WHEN Rating = 3 THEN 1 END) as Rating3,
                   COUNT(CASE WHEN Rating = 2 THEN 1 END) as Rating2,
                   COUNT(CASE WHEN Rating = 1 THEN 1 END) as Rating1
            FROM RATING
            WHERE CID = :cid
        """
        cursor.execute(sql_stats, cid=content_id)
        stats_row = cursor.fetchone()
        stats_columns = [col[0].lower() for col in cursor.description]
        stats = (
            dict(zip(stats_columns, stats_row))
            if stats_row
            else {
                "avgrating": None,
                "reviewcount": 0,
                "rating5": 0,
                "rating4": 0,
                "rating3": 0,
                "rating2": 0,
                "rating1": 0,
            }
        )

        # 5. 리뷰 목록 조회
        sql_reviews = """
            SELECT r.Rating, r.Comm, r.Likes, 
                   m.Name as MemberName, m.ID as MemberID, r.MID, r.CID
            FROM RATING r
            JOIN MEMBER m ON r.MID = m.ID
            WHERE r.CID = :cid
            ORDER BY r.Likes DESC NULLS LAST, r.Rating DESC, m.ID
        """
        cursor.execute(sql_reviews, cid=content_id)
        columns_review = [col[0].lower() for col in cursor.description]
        cursor.rowfactory = lambda *args: dict(zip(columns_review, args))
        reviews = cursor.fetchall()

        # 사용자가 작성한 리뷰 확인
        user_review = None
        if user_id:
            for review in reviews:
                if review["memberid"] == user_id:
                    user_review = review
                    break

    except Exception as e:
        flash(f"데이터 조회 중 오류 발생: {str(e)}", "danger")
        content = None
        tags_by_category = {}
        shops = []
        stats = {"avgrating": None, "reviewcount": 0}
        reviews = []
        user_review = None
    finally:
        cursor.close()

    if not content:
        return redirect(url_for("main.index"))

    return render_template(
        "content/detail.html",
        content=content,
        tags_by_category=tags_by_category,
        shops=shops,
        stats=stats,
        reviews=reviews,
        user_review=user_review,
        user_id=user_id,
    )


@content_bp.route("/<int:content_id>/review/edit", methods=["GET", "POST"])
@login_required
def update_review(content_id):
    """
    리뷰 수정 페이지 및 수정 처리

    Args:
        content_id: 콘텐츠 ID

    GET: 리뷰 수정 폼 표시
    POST: 리뷰 수정 처리
    """
    user_id = session.get("user_id")
    conn = db.get_db()
    cursor = conn.cursor()

    # 콘텐츠 정보 조회
    try:
        sql_content = """
            SELECT c.ContentID, c.Title
            FROM CONTENT c
            WHERE c.ContentID = :cid
        """
        cursor.execute(sql_content, cid=content_id)
        content_row = cursor.fetchone()

        if not content_row:
            flash("존재하지 않는 콘텐츠입니다.", "danger")
            return redirect(url_for("main.index"))

        content = {
            "content_id": content_row[0],
            "title": content_row[1],
        }

        # 기존 리뷰 조회
        sql_review = """
            SELECT Rating, Comm
            FROM RATING
            WHERE MID = :mid AND CID = :cid
        """
        cursor.execute(sql_review, mid=user_id, cid=content_id)
        review_row = cursor.fetchone()

        if not review_row:
            flash("작성한 리뷰가 없습니다.", "warning")
            return redirect(url_for("content.detail", content_id=content_id))

        review = {
            "rating": review_row[0],
            "comment": review_row[1] if review_row[1] else "",
        }

    except Exception as e:
        flash(f"데이터 조회 중 오류 발생: {str(e)}", "danger")
        return redirect(url_for("content.detail", content_id=content_id))
    finally:
        cursor.close()

    if request.method == "POST":
        conn = db.get_db()
        cursor = conn.cursor()

        try:
            rating = int(request.form.get("rating", 0))
            comment = request.form.get("comment", "").strip()

            if rating < 1 or rating > 5:
                flash("평점은 1-5 사이의 값이어야 합니다.", "error")
                return render_template(
                    "content/review_form.html",
                    content=content,
                    review=review,
                    action="update",
                )

            # 리뷰 수정
            sql_update = """
                UPDATE RATING 
                SET Rating = :rating, Comm = :comm
                WHERE MID = :mid AND CID = :cid
            """
            cursor.execute(
                sql_update,
                rating=rating,
                comm=comment if comment else None,
                mid=user_id,
                cid=content_id,
            )
            conn.commit()

            flash("리뷰가 성공적으로 수정되었습니다.", "success")
            return redirect(url_for("content.detail", content_id=content_id))

        except ValueError:
            flash("평점은 숫자로 입력해주세요.", "error")
        except Exception as e:
            conn.rollback()
            flash(f"리뷰 수정 중 오류 발생: {str(e)}", "danger")
        finally:
            cursor.close()

    return render_template(
        "content/review_form.html",
        content=content,
        review=review,
        action="update",
    )


@content_bp.route("/<int:content_id>/review/delete", methods=["POST"])
@login_required
def delete_review(content_id):
    """
    리뷰 삭제 처리

    Args:
        content_id: 콘텐츠 ID
    """
    user_id = session.get("user_id")
    conn = db.get_db()
    cursor = conn.cursor()

    try:
        # 리뷰 삭제
        sql_delete = "DELETE FROM RATING WHERE MID = :mid AND CID = :cid"
        cursor.execute(sql_delete, mid=user_id, cid=content_id)

        if cursor.rowcount == 0:
            flash("삭제할 리뷰가 없습니다.", "warning")
        else:
            conn.commit()
            flash("리뷰가 성공적으로 삭제되었습니다.", "success")

    except Exception as e:
        conn.rollback()
        flash(f"리뷰 삭제 중 오류 발생: {str(e)}", "danger")
    finally:
        cursor.close()

    return redirect(url_for("content.detail", content_id=content_id))


@content_bp.route("/<int:content_id>/review/<string:review_member_id>/like", methods=["POST"])
@login_required
def like_review(content_id, review_member_id):
    """
    리뷰 좋아요 처리 (동시성 제어 포인트)

    Args:
        content_id: 콘텐츠 ID
        review_member_id: 해당 리뷰를 작성한 사용자 ID (MID)
    """
    actor_id = session.get("user_id")

    try:
        review_service.like_review(actor_id, review_member_id, content_id)
        flash("좋아요가 반영되었습니다.", "success")
    except review_service.ReviewNotFoundError as e:
        flash(str(e), "danger")
    except review_service.ReviewServiceError as e:
        flash(str(e), "danger")
    except Exception as e:
        flash(f"좋아요 처리 중 오류 발생: {str(e)}", "danger")

    return redirect(url_for("content.detail", content_id=content_id))
