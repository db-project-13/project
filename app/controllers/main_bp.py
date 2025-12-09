"""
메인 페이지 Blueprint
"""
from flask import Blueprint, render_template, session, request, flash
from app.db import db
import oracledb

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """
    메인 페이지 - 전체 콘텐츠 목록 표시
    
    Returns:
        메인 페이지 템플릿
    """
    conn = db.get_db()
    cursor = conn.cursor()
    user_id = session.get('user_id')
    is_admin = session.get('is_admin', False)
    
    # 페이지네이션 (선택사항)
    page = request.args.get('page', 1, type=int)
    per_page = 20
    offset = (page - 1) * per_page
    
    try:
        # 전체 콘텐츠 목록 조회
        sql_list = """
            SELECT c.ContentID, c.Title, 
                   TO_CHAR(c.ReleaseDate, 'YYYY-MM-DD') as ReleaseDate,
                   p.Prodname, s.SName,
                   CASE 
                       WHEN c.ContentID >= 2001 AND c.ContentID <= 3000 THEN 'Movie'
                       WHEN c.ContentID >= 301 AND c.ContentID <= 1000 THEN 'Video Game'
                       WHEN c.ContentID >= 1001 AND c.ContentID <= 2000 THEN 'Book'
                       ELSE 'Unknown'
                   END as MediaType,
                   (SELECT ROUND(AVG(r.Rating), 1) FROM RATING r WHERE r.CID = c.ContentID) as AvgRating,
                   (SELECT COUNT(*) FROM RATING r WHERE r.CID = c.ContentID) as ReviewCount
            FROM CONTENT c
            JOIN PRODUCT_CO p ON c.PID = p.ProdcoID
            LEFT JOIN SERIES s ON c.SID = s.SeriesID
            ORDER BY c.ReleaseDate DESC
        """
        cursor.execute(sql_list)
        columns = [col[0].lower() for col in cursor.description]
        cursor.rowfactory = lambda *args: dict(zip(columns, args))
        all_contents = cursor.fetchall()
        
        # 페이지네이션 적용
        total = len(all_contents)
        contents = all_contents[offset:offset + per_page]
        
        # 테마별 통계 (ContentID 범위 기반)
        # 영화: 2001 ~ 3000, 게임: 301 ~ 1000, 도서: 1001 ~ 2000
        theme_stats = {}
        
        # 영화 개수
        sql_movies = "SELECT COUNT(*) FROM CONTENT WHERE ContentID >= 2001 AND ContentID <= 3000"
        cursor.execute(sql_movies)
        theme_stats['Movie'] = cursor.fetchone()[0]
        
        # 게임 개수
        sql_games = "SELECT COUNT(*) FROM CONTENT WHERE ContentID >= 301 AND ContentID <= 1000"
        cursor.execute(sql_games)
        theme_stats['Video Game'] = cursor.fetchone()[0]
        
        # 도서 개수
        sql_books = "SELECT COUNT(*) FROM CONTENT WHERE ContentID >= 1001 AND ContentID <= 2000"
        cursor.execute(sql_books)
        theme_stats['Book'] = cursor.fetchone()[0]
        
    except Exception as e:
        flash(f'데이터 조회 중 오류 발생: {str(e)}', 'danger')
        contents = []
        theme_stats = {}
        total = 0
    finally:
        cursor.close()
    
    return render_template(
        'main/index.html',
        user_id=user_id,
        is_admin=is_admin,
        contents=contents,
        theme_stats=theme_stats,
        page=page,
        per_page=per_page,
        total=total,
        has_prev=page > 1,
        has_next=offset + per_page < total
    )

