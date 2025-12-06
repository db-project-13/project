"""
관리자 기능 Blueprint (콘텐츠 관리, 쿼리 실행)
"""
from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from app.utils.decorators import admin_required
from app.db import db
import oracledb

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.before_request
def check_admin():
    """
    모든 관리자 라우트에 대해 권한 확인
    (개별 라우트에 @admin_required 데코레이터 사용 권장)
    """
    # 로그인 확인은 개별 데코레이터에서 처리
    pass


@admin_bp.route('/')
@admin_required
def dashboard():
    """
    관리자 대시보드
    
    Returns:
        관리자 대시보드 템플릿
    """
    return render_template('admin/dashboard.html')


@admin_bp.route('/producers', methods=['GET', 'POST'])
@admin_required
def manage_producers():
    """
    제작사 관리 페이지
    
    GET: 제작사 목록 표시
    POST: 제작사 등록/수정/삭제 처리 (추후 AdminService 연동)
    """
    if request.method == 'POST':
        action = request.form.get('action')
        
        # TODO: AdminService를 통한 제작사 관리
        # admin_service = AdminService(admin_dao)
        # if action == 'insert':
        #     admin_service.insert_producer(...)
        # elif action == 'update':
        #     admin_service.update_producer(...)
        # elif action == 'delete':
        #     admin_service.delete_producer(...)
        
        flash(f'제작사 관리 기능은 추후 구현 예정입니다. (작업: {action})', 'info')
        return redirect(url_for('admin.manage_producers'))
    
    # TODO: 제작사 목록 조회
    # admin_dao = AdminDAO(current_app.db)
    # producers = admin_dao.list_producers()
    
    producers = []
    return render_template('admin/producers.html', producers=producers)


@admin_bp.route('/contents', methods=['GET', 'POST'])
@admin_required
def manage_contents():
    """
    콘텐츠 관리 페이지
    Schema: ContentID, Title, ReleaseDate, PID(FK), SID(FK)
    """
    conn = db.get_db()
    cursor = conn.cursor()

    # 1. POST 요청 처리 (등록/수정/삭제)
    if request.method == 'POST':
        action = request.form.get('action')
        
        try:
            if action == 'insert':
                title = request.form.get('title')
                release_date = request.form.get('release_date')
                pid = request.form.get('pid') # 필수
                sid = request.form.get('sid') # 선택 (없으면 None)

                # SID가 빈 문자열이면 None(NULL)으로 처리
                if not sid:
                    sid = None

                # 시퀀스 이름은 CONTENT_SEQ라고 가정 (없으면 생성 필요)
                sql = """
                    INSERT INTO CONTENT (ContentID, Title, ReleaseDate, PID, SID)
                    VALUES (CONTENT_SEQ.NEXTVAL, :title, TO_DATE(:r_date, 'YYYY-MM-DD'), :pid, :sid)
                """
                cursor.execute(sql, title=title, r_date=release_date, pid=pid, sid=sid)
                flash('콘텐츠가 성공적으로 등록되었습니다.', 'success')

            elif action == 'update':
                content_id = request.form.get('content_id')
                title = request.form.get('title')
                release_date = request.form.get('release_date')
                pid = request.form.get('pid')
                sid = request.form.get('sid')

                if not sid:
                    sid = None

                sql = """
                    UPDATE CONTENT 
                    SET Title = :title, 
                        ReleaseDate = TO_DATE(:r_date, 'YYYY-MM-DD'),
                        PID = :pid,
                        SID = :sid
                    WHERE ContentID = :cid
                """
                cursor.execute(sql, title=title, r_date=release_date, pid=pid, sid=sid, cid=content_id)
                flash('콘텐츠 정보가 수정되었습니다.', 'success')

            elif action == 'delete':
                content_id = request.form.get('content_id')
                
                # 자식 테이블(TAG_TO, SHOP, RATING)이 있다면 먼저 지워야 할 수도 있음 (CASCADE 설정 여부에 따라 다름)
                # 제공된 SQL에는 CASCADE CONSTRAINTS로 DROP만 되어 있으므로, 안전하게 삭제 시도
                sql = "DELETE FROM CONTENT WHERE ContentID = :cid"
                cursor.execute(sql, cid=content_id)
                flash('콘텐츠가 삭제되었습니다.', 'warning')

            conn.commit()

        except oracledb.Error as e:
            conn.rollback()
            error_obj, = e.args
            flash(f'DB 오류 발생: {error_obj.message}', 'danger')
        except Exception as e:
            conn.rollback()
            flash(f'오류 발생: {str(e)}', 'danger')
            
        return redirect(url_for('admin.manage_contents'))

    # 2. GET 요청 처리 (조회)
    try:
        # A. 콘텐츠 목록 조회 (제작사명, 시리즈명 조인)
        sql_list = """
            SELECT c.ContentID, c.Title, 
                   TO_CHAR(c.ReleaseDate, 'YYYY-MM-DD') as ReleaseDate,
                   c.PID, p.Prodname,
                   c.SID, s.SName
            FROM CONTENT c
            JOIN PRODUCT_CO p ON c.PID = p.ProdcoID
            LEFT JOIN SERIES s ON c.SID = s.SeriesID
            ORDER BY c.ContentID DESC
        """
        cursor.execute(sql_list)
        columns = [col[0].lower() for col in cursor.description]
        cursor.rowfactory = lambda *args: dict(zip(columns, args))
        contents = cursor.fetchall()

        # B. 제작사 목록 조회 (드롭다운용)
        cursor.execute("SELECT ProdcoID, Prodname FROM PRODUCT_CO ORDER BY Prodname")
        # 튜플 리스트 그대로 사용하거나 딕셔너리로 변환
        producers = [{'id': row[0], 'name': row[1]} for row in cursor.fetchall()]

        # C. 시리즈 목록 조회 (드롭다운용)
        cursor.execute("SELECT SeriesID, SName FROM SERIES ORDER BY SName")
        series_list = [{'id': row[0], 'name': row[1]} for row in cursor.fetchall()]

    except Exception as e:
        flash(f'데이터 조회 중 오류: {str(e)}', 'danger')
        contents = []
        producers = []
        series_list = []
    finally:
        cursor.close()

    return render_template('admin/contents.html', 
                           contents=contents, 
                           producers=producers, 
                           series_list=series_list)


@admin_bp.route('/series', methods=['GET', 'POST'])
@admin_required
def manage_series():
    """
    시리즈 관리 페이지
    
    GET: 시리즈 목록 표시
    POST: 시리즈 등록/수정/삭제 처리 (추후 AdminService 연동)
    """
    if request.method == 'POST':
        action = request.form.get('action')
        flash(f'시리즈 관리 기능은 추후 구현 예정입니다. (작업: {action})', 'info')
        return redirect(url_for('admin.manage_series'))
    
    series_list = []
    return render_template('admin/series.html', series_list=series_list)


@admin_bp.route('/queries')
@admin_required
def query_menu():
    """
    쿼리 메뉴 페이지
    
    Returns:
        쿼리 메뉴 템플릿
    """
    queries = [
        {'id': 1, 'title': 'Q 1-1: 회원 목록 (특정 성별 필터링)'},
        {'id': 2, 'title': 'Q 1-2: 최신 콘텐츠 목록 (특정 날짜 이후 출시)'},
        {'id': 3, 'title': 'Q 2-1: 제작사별 리뷰 조회 (특정 제작사명)'},
        {'id': 4, 'title': 'Q 3-1: 태그별 평점 통계 (전체 집계 랭킹)'},
        {'id': 5, 'title': 'Q 4-2: 평균 평점보다 높은 리뷰 하이라이트'},
        {'id': 6, 'title': 'Q 6-1: 기간 출시 콘텐츠의 SHOP 구매처 조회'},
        {'id': 7, 'title': 'Q 7-1: 특정 제작사 고평점 콘텐츠 목록 (인라인 뷰)'},
        {'id': 8, 'title': 'Q 8-1: 시리즈 콘텐츠 출시일 순 정렬'},
        {'id': 9, 'title': 'Q 9-1: 활동 우수 TOP 5 멤버 랭킹'},
        {'id': 10, 'title': 'Q 9-2: 제작사별 평균 평점 랭킹'}
    ]
    
    return render_template('admin/query_menu.html', queries=queries)


@admin_bp.route('/queries/<int:query_id>')
@admin_required
def execute_query(query_id):
    """
    쿼리 실행 및 결과 표시
    
    Args:
        query_id: 쿼리 ID (1-10)
    
    Returns:
        쿼리 결과 템플릿
    """
    # TODO: QueryDAO를 통한 쿼리 실행
    # query_dao = QueryDAO(current_app.db)
    # result = query_dao.execute_query(query_id, **request.args)
    
    # 임시 데이터
    result = {
        'query_id': query_id,
        'query_title': f'Q {query_id}: 쿼리 실행 (추후 구현 예정)',
        'data': [],
        'message': '쿼리 실행 기능은 추후 구현 예정입니다.'
    }
    
    return render_template('admin/query_result.html', result=result)

