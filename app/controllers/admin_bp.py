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
    콘텐츠 관리 페이지 (태그 연동 포함)
    Schema: ContentID, Title, ReleaseDate, PID, SID
    Relation: TAG_TO (Many-to-Many with TAG)
    """
    conn = db.get_db()
    cursor = conn.cursor()

    # 1. POST 요청 처리 (등록/수정/삭제)
    if request.method == 'POST':
        action = request.form.get('action')
        
        try:
            # 체크박스로 선택된 태그 코드 리스트 가져오기
            selected_tags = request.form.getlist('tags') # ['1', '3', '5'] 형태

            if action == 'insert':
                title = request.form.get('title')
                release_date = request.form.get('release_date')
                pid = request.form.get('pid')
                sid = request.form.get('sid')
                if not sid: sid = None

                # [중요] TAG_TO에 넣으려면 생성될 ContentID를 미리 알아야 함
                # 시퀀스 값을 먼저 가져옵니다.
                cursor.execute("SELECT CONTENT_SEQ.NEXTVAL FROM DUAL")
                new_id = cursor.fetchone()[0]

                # 1) 콘텐츠 저장
                sql_content = """
                    INSERT INTO CONTENT (ContentID, Title, ReleaseDate, PID, SID)
                    VALUES (:nid, :title, TO_DATE(:r_date, 'YYYY-MM-DD'), :pid, :sid)
                """
                cursor.execute(sql_content, nid=new_id, title=title, r_date=release_date, pid=pid, sid=sid)

                # 2) 태그 연결 저장 (반복문)
                if selected_tags:
                    sql_tag = "INSERT INTO TAG_TO (TCode, CID) VALUES (:tcode, :cid)"
                    # executemany가 성능이 좋지만, 간단하게 반복문 사용
                    for tag_code in selected_tags:
                        cursor.execute(sql_tag, tcode=tag_code, cid=new_id)

                flash(f'콘텐츠가 등록되었습니다. (태그 {len(selected_tags)}개)', 'success')

            elif action == 'update':
                content_id = request.form.get('content_id')
                title = request.form.get('title')
                release_date = request.form.get('release_date')
                pid = request.form.get('pid')
                sid = request.form.get('sid')
                if not sid: sid = None

                # 1) 콘텐츠 정보 업데이트
                sql_update = """
                    UPDATE CONTENT 
                    SET Title = :title, 
                        ReleaseDate = TO_DATE(:r_date, 'YYYY-MM-DD'),
                        PID = :pid,
                        SID = :sid
                    WHERE ContentID = :cid
                """
                cursor.execute(sql_update, title=title, r_date=release_date, pid=pid, sid=sid, cid=content_id)

                # 2) 태그 정보 업데이트 (기존 매핑 삭제 -> 새 매핑 추가)
                cursor.execute("DELETE FROM TAG_TO WHERE CID = :cid", cid=content_id)
                
                if selected_tags:
                    sql_tag = "INSERT INTO TAG_TO (TCode, CID) VALUES (:tcode, :cid)"
                    for tag_code in selected_tags:
                        cursor.execute(sql_tag, tcode=tag_code, cid=content_id)

                flash('콘텐츠 정보가 수정되었습니다.', 'success')

            elif action == 'delete':
                content_id = request.form.get('content_id')
                
                # 자식 데이터 삭제 (태그 매핑, 상점, 리뷰)
                cursor.execute("DELETE FROM TAG_TO WHERE CID = :cid", cid=content_id)
                cursor.execute("DELETE FROM SHOP WHERE CID = :cid", cid=content_id)
                cursor.execute("DELETE FROM RATING WHERE CID = :cid", cid=content_id)
                
                # 본체 삭제
                cursor.execute("DELETE FROM CONTENT WHERE ContentID = :cid", cid=content_id)
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
        # A. 콘텐츠 목록 + 태그 목록 조회 (기존 코드 유지)
        sql_list = """
            SELECT c.ContentID, c.Title, 
                   TO_CHAR(c.ReleaseDate, 'YYYY-MM-DD') as ReleaseDate,
                   c.PID, p.Prodname,
                   c.SID, s.SName,
                   (SELECT LISTAGG(t.Tag, ', ') WITHIN GROUP (ORDER BY t.Tag)
                    FROM TAG_TO tt JOIN TAG t ON tt.TCode = t.TagCode
                    WHERE tt.CID = c.ContentID) as TagNames,
                   (SELECT LISTAGG(t.TagCode, ',') WITHIN GROUP (ORDER BY t.TagCode)
                    FROM TAG_TO tt JOIN TAG t ON tt.TCode = t.TagCode
                    WHERE tt.CID = c.ContentID) as TagCodes
            FROM CONTENT c
            JOIN PRODUCT_CO p ON c.PID = p.ProdcoID
            LEFT JOIN SERIES s ON c.SID = s.SeriesID
            ORDER BY c.ContentID DESC
        """
        cursor.execute(sql_list)
        columns = [col[0].lower() for col in cursor.description]
        cursor.rowfactory = lambda *args: dict(zip(columns, args))
        contents = cursor.fetchall()

        # B. 제작사 & 시리즈 목록 (기존 코드 유지)
        cursor.execute("SELECT ProdcoID, Prodname FROM PRODUCT_CO ORDER BY Prodname")
        producers = [{'id': row[0], 'name': row[1]} for row in cursor.fetchall()]
        cursor.execute("SELECT SeriesID, SName FROM SERIES ORDER BY SName")
        series_list = [{'id': row[0], 'name': row[1]} for row in cursor.fetchall()]
        
        # C. 태그 목록 (기존 코드 유지)
        cursor.execute("SELECT TagCode, Category, Tag FROM TAG ORDER BY Category, Tag")
        all_tags = []
        for row in cursor.fetchall():
            all_tags.append({'code': row[0], 'category': row[1], 'name': row[2]})
            
        tags_by_category = {}
        for tag in all_tags:
            cat = tag['category']
            if cat not in tags_by_category: tags_by_category[cat] = []
            tags_by_category[cat].append(tag)
            
        # D. 모든 구매처(SHOP) 정보 조회 및 매핑
        # 콘텐츠별로 어떤 구매처가 있는지 미리 다 가져옵니다.
        sql_shops = "SELECT CID, MainURL, SubURL FROM SHOP ORDER BY CID"
        cursor.execute(sql_shops)
        
        # 콘텐츠 ID를 키로 하는 딕셔너리로 변환
        shops_by_content = {}
        for row in cursor.fetchall():
            cid, main_url, sub_url = row
            if cid not in shops_by_content:
                shops_by_content[cid] = []
            shops_by_content[cid].append({'main': main_url, 'sub': sub_url})

    except Exception as e:
        flash(f'데이터 조회 중 오류: {str(e)}', 'danger')
        contents = []
        producers = []
        series_list = []
        tags_by_category = {}
        shops_by_content = {}
    finally:
        cursor.close()

    return render_template('admin/contents.html', 
                           contents=contents, 
                           producers=producers, 
                           series_list=series_list,
                           tags_by_category=tags_by_category,
                           shops_by_content=shops_by_content) # [NEW] 템플릿으로 전달

# 구매처(SHOP) 추가/삭제 처리 라우트
@admin_bp.route('/contents/shops', methods=['POST'])
@admin_required
def manage_shops():
    conn = db.get_db()
    cursor = conn.cursor()
    
    action = request.form.get('action')
    content_id = request.form.get('content_id')
    
    try:
        if action == 'insert':
            main_url = request.form.get('main_url')
            sub_url = request.form.get('sub_url')
            
            # PK 중복 체크는 DB 에러로 처리
            sql = "INSERT INTO SHOP (MainURL, SubURL, CID) VALUES (:main, :sub, :cid)"
            cursor.execute(sql, main=main_url, sub=sub_url, cid=content_id)
            flash('구매처가 추가되었습니다.', 'success')
            
        elif action == 'delete':
            main_url = request.form.get('main_url')
            sub_url = request.form.get('sub_url')
            
            # 복합키(Main, Sub)로 삭제
            sql = "DELETE FROM SHOP WHERE MainURL = :main AND SubURL = :sub AND CID = :cid"
            cursor.execute(sql, main=main_url, sub=sub_url, cid=content_id)
            flash('구매처가 삭제되었습니다.', 'warning')
            
        conn.commit()
        
    except oracledb.IntegrityError:
        conn.rollback()
        flash('이미 등록된 URL입니다.', 'danger')
    except Exception as e:
        conn.rollback()
        flash(f'오류 발생: {str(e)}', 'danger')
    finally:
        cursor.close()
        
    return redirect(url_for('admin.manage_contents'))

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