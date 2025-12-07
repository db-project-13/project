"""
관리자 기능 Blueprint (콘텐츠 관리, 회원 관리, 태그 관리 등)
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
    """
    # 로그인 확인은 개별 데코레이터에서 처리
    pass


@admin_bp.route('/')
@admin_required
def dashboard():
    """
    관리자 대시보드
    """
    return render_template('admin/dashboard.html')


@admin_bp.route('/members', methods=['GET', 'POST'])
@admin_required
def manage_members():
    """
    회원 관리 페이지 (일반 회원 목록 조회 및 삭제)
    Schema: ID, Password, Name, Address, Sex, Birthday, IsAdmin
    """
    conn = db.get_db()
    cursor = conn.cursor()

    # 1. POST 요청 처리 (삭제)
    if request.method == 'POST':
        action = request.form.get('action')
        
        try:
            if action == 'delete':
                member_id = request.form.get('member_id')
                
                # 1) RATING 테이블의 자식 레코드를 먼저 삭제
                # 회원 탈퇴 시 작성한 리뷰도 함께 삭제하는 것이 일반적입니다.
                sql_delete_rating = "DELETE FROM RATING WHERE MID = :mid"
                cursor.execute(sql_delete_rating, mid=member_id)
                
                # 2) MEMBER 삭제
                sql_delete_member = "DELETE FROM MEMBER WHERE ID = :mid"
                cursor.execute(sql_delete_member, mid=member_id)
                
                flash(f'회원 [{member_id}]가 성공적으로 삭제되었습니다.', 'warning')
                
            conn.commit()

        except oracledb.Error as e:
            conn.rollback()
            error_obj, = e.args
            # ORA-02292: integrity constraint (xxx) violated - child record found (혹시 RATING 외 다른 테이블이 참조한다면)
            if error_obj.code == 2292:
                flash(f'DB 오류 발생: 회원 [{member_id}]에게 연결된 데이터가 있어 삭제할 수 없습니다. 관련 데이터를 먼저 정리해야 합니다.', 'danger')
            else:
                flash(f'DB 오류 발생: {error_obj.message}', 'danger')
        except Exception as e:
            conn.rollback()
            flash(f'오류 발생: {str(e)}', 'danger')
            
        return redirect(url_for('admin.manage_members'))

    # 2. GET 요청 처리 (조회)
    try:
        # IsAdmin이 'F'인 일반 회원만 조회
        sql_list = """
            SELECT ID, Name, Address, Sex, TO_CHAR(Birthday, 'YYYY-MM-DD') AS Birthday
            FROM MEMBER
            WHERE IsAdmin = 'F'
            ORDER BY ID
        """
        cursor.execute(sql_list)
        columns = [col[0].lower() for col in cursor.description]
        cursor.rowfactory = lambda *args: dict(zip(columns, args))
        members = cursor.fetchall()
        
    except Exception as e:
        flash(f'데이터 조회 중 오류: {str(e)}', 'danger')
        members = []
    finally:
        cursor.close()

    return render_template('admin/members.html', members=members)


@admin_bp.route('/producers', methods=['GET', 'POST'])
@admin_required
def manage_producers():
    """
    제작사 관리 페이지
    Schema: ProdcoID(PK), Prodname, ProdInfo
    """
    conn = db.get_db()
    cursor = conn.cursor()

    # 1. POST 요청 처리
    if request.method == 'POST':
        action = request.form.get('action')
        
        try:
            if action == 'insert':
                prod_name = request.form.get('prod_name')
                prod_info = request.form.get('prod_info')
                
                sql = """
                    INSERT INTO PRODUCT_CO (ProdcoID, Prodname, ProdInfo)
                    VALUES (PRODUCT_CO_SEQ.NEXTVAL, :name, :info)
                """
                cursor.execute(sql, name=prod_name, info=prod_info)
                flash('제작사가 추가되었습니다.', 'success')

            elif action == 'update':
                prod_id = request.form.get('prod_id')
                prod_name = request.form.get('prod_name')
                prod_info = request.form.get('prod_info')

                sql = """
                    UPDATE PRODUCT_CO 
                    SET Prodname = :name, ProdInfo = :info
                    WHERE ProdcoID = :pid
                """
                cursor.execute(sql, name=prod_name, info=prod_info, pid=prod_id)
                flash('제작사 정보가 수정되었습니다.', 'success')

            elif action == 'delete':
                prod_id = request.form.get('prod_id')
                
                try:
                    sql = "DELETE FROM PRODUCT_CO WHERE ProdcoID = :pid"
                    cursor.execute(sql, pid=prod_id)
                    flash('제작사가 삭제되었습니다.', 'warning')
                except oracledb.IntegrityError:
                    conn.rollback()
                    flash('이 제작사에 등록된 콘텐츠가 있어 삭제할 수 없습니다. 연결된 콘텐츠를 먼저 삭제하거나 수정해야 합니다.', 'danger')
                    return redirect(url_for('admin.manage_producers'))

            conn.commit()

        except Exception as e:
            conn.rollback()
            error_obj, = e.args[0] if isinstance(e.args[0], oracledb.Error) else (None, str(e))
            flash(f'DB 오류 발생: {error_obj.message if error_obj else str(e)}', 'danger')
            
        return redirect(url_for('admin.manage_producers'))

    # 2. GET 요청 처리 (목록 조회)
    try:
        sql = "SELECT ProdcoID, Prodname, ProdInfo FROM PRODUCT_CO ORDER BY ProdcoID DESC"
        cursor.execute(sql)
        
        columns = [col[0].lower() for col in cursor.description]
        cursor.rowfactory = lambda *args: dict(zip(columns, args))
        
        producers = cursor.fetchall()
        
    except Exception as e:
        flash(f'데이터 조회 실패: {str(e)}', 'danger')
        producers = []
    finally:
        cursor.close()

    return render_template('admin/producers.html', producers=producers)


@admin_bp.route('/series', methods=['GET', 'POST'])
@admin_required
def manage_series():
    """
    시리즈 관리 페이지
    Schema: SeriesID(PK), SName
    """
    conn = db.get_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        action = request.form.get('action')
        
        try:
            if action == 'insert':
                sname = request.form.get('sname')
                
                sql = "INSERT INTO SERIES (SeriesID, SName) VALUES (SERIES_SEQ.NEXTVAL, :name)"
                cursor.execute(sql, name=sname)
                flash('시리즈가 추가되었습니다.', 'success')

            elif action == 'update':
                series_id = request.form.get('series_id')
                sname = request.form.get('sname')

                sql = "UPDATE SERIES SET SName = :name WHERE SeriesID = :sid"
                cursor.execute(sql, name=sname, sid=series_id)
                flash('시리즈 정보가 수정되었습니다.', 'success')

            elif action == 'delete':
                series_id = request.form.get('series_id')
                
                try:
                    sql = "DELETE FROM SERIES WHERE SeriesID = :sid"
                    cursor.execute(sql, sid=series_id)
                    flash('시리즈가 삭제되었습니다.', 'warning')
                except oracledb.IntegrityError:
                    conn.rollback()
                    flash('이 시리즈에 포함된 콘텐츠가 있어 삭제할 수 없습니다. 연결된 콘텐츠를 먼저 수정하거나 삭제해야 합니다.', 'danger')
                    return redirect(url_for('admin.manage_series'))

            conn.commit()

        except Exception as e:
            conn.rollback()
            error_obj, = e.args[0] if isinstance(e.args[0], oracledb.Error) else (None, str(e))
            flash(f'DB 오류 발생: {error_obj.message if error_obj else str(e)}', 'danger')
            
        return redirect(url_for('admin.manage_series'))
    
    # 목록 조회
    try:
        sql = "SELECT SeriesID, SName FROM SERIES ORDER BY SName"
        cursor.execute(sql)
        
        columns = [col[0].lower() for col in cursor.description]
        cursor.rowfactory = lambda *args: dict(zip(columns, args))
        
        series_list = cursor.fetchall()
        
    except Exception as e:
        flash(f'데이터 조회 실패: {str(e)}', 'danger')
        series_list = []
    finally:
        cursor.close()

    return render_template('admin/series.html', series_list=series_list)


@admin_bp.route('/contents', methods=['GET', 'POST'])
@admin_required
def manage_contents():
    """
    콘텐츠 관리 페이지
    (이전 단계에서 구현된 함수 그대로 사용)
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

                # 시퀀스 이름은 CONTENT_SEQ라고 가정
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
                
                # 자식 테이블(TAG_TO, SHOP, RATING)이 있다면 먼저 지워야 함
                # 제공된 SQL 스키마는 CASCADE DELETE가 아니므로 수동 삭제 로직이 필요하지만,
                # 현재는 테스트를 위해 DB의 FK 설정을 믿고 삭제 시도
                sql_delete_tag_to = "DELETE FROM TAG_TO WHERE CID = :cid"
                cursor.execute(sql_delete_tag_to, cid=content_id)
                sql_delete_shop = "DELETE FROM SHOP WHERE CID = :cid"
                cursor.execute(sql_delete_shop, cid=content_id)
                sql_delete_rating = "DELETE FROM RATING WHERE CID = :cid"
                cursor.execute(sql_delete_rating, cid=content_id)
                
                # CONTENT 삭제
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


@admin_bp.route('/tags', methods=['GET', 'POST'])
@admin_required
def manage_tags():
    """
    태그 관리 페이지 (추가/삭제는 다음 단계에서 완성)
    Schema: TagCode, Category, Tag
    """
    conn = db.get_db()
    cursor = conn.cursor()
    
    # POST 로직 (추가/삭제)
    if request.method == 'POST':
        action = request.form.get('action')
        
        try:
            if action == 'insert':
                category = request.form.get('category')
                tag_name = request.form.get('tag_name')
                
                sql = "INSERT INTO TAG (TagCode, Category, Tag) VALUES (TAG_SEQ.NEXTVAL, :cat, :tag)"
                cursor.execute(sql, cat=category, tag=tag_name)
                flash('태그가 추가되었습니다.', 'success')
            
            elif action == 'delete':
                tag_code = request.form.get('tag_code')
                
                # 태그 사용 여부 확인 후 삭제 시도
                sql_delete_tag_to = "DELETE FROM TAG_TO WHERE TCode = :tcode"
                cursor.execute(sql_delete_tag_to, tcode=tag_code)
                
                sql_delete_tag = "DELETE FROM TAG WHERE TagCode = :tcode"
                cursor.execute(sql_delete_tag, tcode=tag_code)
                flash('태그가 삭제되었습니다.', 'warning')

            conn.commit()

        except oracledb.IntegrityError:
            conn.rollback()
            flash('DB 오류: 이 태그에 연결된 데이터가 있어 삭제할 수 없습니다.', 'danger')
        except Exception as e:
            conn.rollback()
            flash(f'오류 발생: {str(e)}', 'danger')

        return redirect(url_for('admin.manage_tags'))

    # GET 로직 (목록 조회)
    tags = []
    try:
        sql = "SELECT TagCode, Category, Tag FROM TAG ORDER BY Category, Tag"
        cursor.execute(sql)
        columns = [col[0].lower() for col in cursor.description]
        cursor.rowfactory = lambda *args: dict(zip(columns, args))
        tags = cursor.fetchall()
        
        # 카테고리 목록 추출 (드롭다운용)
        categories = sorted(list(set(tag['category'] for tag in tags)))
    except Exception as e:
        flash(f'데이터 조회 중 오류: {str(e)}', 'danger')
        categories = []
    finally:
        cursor.close()

    return render_template('admin/tags.html', tags=tags, categories=categories)