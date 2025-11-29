# Team13-Phase4 Flask 웹 애플리케이션 구현 계획서

## 📋 개요

이 문서는 Phase 3 콘솔 애플리케이션을 Flask 기반 웹 애플리케이션으로 전환하기 위한 **구체적인 단계별 구현 계획**을 제시합니다.

---

## 🎯 Phase 3 → Phase 4 전환 전략

### 핵심 전환 포인트

| Phase 3 (Java 콘솔) | Phase 4 (Flask 웹) | 전환 방법 |
|:---|:---|:---|
| `MainMenu.java` (메뉴 라우팅) | `controllers/*_bp.py` (Blueprint 라우팅) | URL 기반 라우팅으로 전환 |
| `static` 변수 (세션 관리) | Flask Session | `session['user_id']`, `session['is_admin']` |
| `Scanner` (콘솔 입력) | HTML Form + Flask Request | `request.form`, `request.args` |
| `System.out.println()` (콘솔 출력) | Jinja2 템플릿 | HTML 템플릿 렌더링 |
| 단일 `Connection` | Connection Pool | `cx_Oracle.ConnectionPool` |
| 트랜잭션 없음 | 명시적 트랜잭션 | `conn.commit()`, `conn.rollback()` |

---

## 📅 단계별 구현 계획

### Phase 1: 프로젝트 초기 설정 (1-2일)

#### 1.1 프로젝트 구조 생성
```bash
team13-phase4/
├── app/
│   ├── __init__.py
│   ├── app.py
│   ├── config.py
│   ├── controllers/
│   ├── services/
│   ├── models/
│   ├── utils/
│   ├── templates/
│   └── static/
├── venv/
├── requirements.txt
└── README.md
```

**작업 내용**:
- [x] 프로젝트 폴더 구조 생성 ✅ (2024년 완료)
- [ ] Python 가상 환경 설정 (`python -m venv venv`)
- [x] `requirements.txt` 작성 (Flask, cx_Oracle, python-dotenv 등) ✅
- [x] `.gitignore` 파일 생성 ✅ (기존 파일 활용)
- [x] Git 저장소 초기화 ✅ (기존 저장소 활용)

**필요 패키지** (`requirements.txt`):
```
Flask==3.0.0
cx_Oracle==8.3.0
python-dotenv==1.0.0
Werkzeug==3.0.1
Jinja2==3.1.2
```

#### 1.2 데이터베이스 연결 설정
**파일**: `app/models/database.py`

**구현 내용**:
```python
import cx_Oracle
from contextlib import contextmanager

class Database:
    def __init__(self):
        self.pool = None
    
    def init_pool(self, dsn, user, password, min=2, max=10):
        """Connection Pool 초기화"""
        self.pool = cx_Oracle.ConnectionPool(
            user=user,
            password=password,
            dsn=dsn,
            min=min,
            max=max,
            increment=1
        )
    
    @contextmanager
    def get_connection(self):
        """Connection 가져오기 (Context Manager)"""
        conn = self.pool.acquire()
        try:
            yield conn
        finally:
            self.pool.release(conn)
    
    @contextmanager
    def transaction(self):
        """트랜잭션 컨텍스트 매니저"""
        conn = self.pool.acquire()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            self.pool.release(conn)
```

**작업 내용**:
- [ ] `database.py` 파일 생성
- [ ] Connection Pool 구현
- [ ] 트랜잭션 컨텍스트 매니저 구현
- [ ] 환경 변수 설정 (`.env` 파일)

---

### Phase 2: 공통 인프라 구축 (2-3일)

#### 2.1 Flask 앱 초기화
**파일**: `app/__init__.py`

**구현 내용**:
```python
from flask import Flask
from app.models.database import Database
from app.controllers import auth_bp, member_bp, content_bp, admin_bp

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    
    # DB 초기화
    db = Database()
    db.init_pool(
        dsn="localhost:1521/orcl",
        user="university",
        password="comp322"
    )
    app.db = db
    
    # Blueprint 등록
    app.register_blueprint(auth_bp)
    app.register_blueprint(member_bp)
    app.register_blueprint(content_bp)
    app.register_blueprint(admin_bp)
    
    return app
```

**작업 내용**:
- [x] Flask 앱 팩토리 함수 구현 ✅ (`app/__init__.py`)
- [ ] 데이터베이스 인스턴스 앱에 연결 (추후 구현)
- [x] Blueprint 등록 구조 준비 ✅ (모든 Blueprint 등록 완료)

#### 2.2 공통 레이아웃 템플릿
**파일**: `app/templates/layout/base.html`

**구현 내용**:
- [x] Bootstrap 또는 Tailwind CSS 적용 ✅ (Bootstrap 5 적용)
- [x] 네비게이션 바 (로그인 상태에 따른 동적 메뉴) ✅ (`templates/layout/base.html`)
- [x] Flash 메시지 표시 영역 ✅
- [x] 공통 CSS/JS 포함 ✅ (`static/css/style.css`, `static/js/main.js`)

**핵심 기능**:
```jinja2
{% if session.get('user_id') %}
    <li><a href="/profile/edit">회원정보 수정</a></li>
    <li><a href="/contents/review">리뷰 등록</a></li>
    {% if session.get('is_admin') %}
        <li><a href="/admin">관리자</a></li>
    {% endif %}
{% else %}
    <li><a href="/login">로그인</a></li>
    <li><a href="/register">회원가입</a></li>
{% endif %}
```

#### 2.3 유틸리티 함수
**파일**: `app/utils/validators.py`

**구현 내용**:
- [ ] 날짜 형식 검증 (`validate_date()`)
- [ ] ID 중복 검사 헬퍼 함수
- [ ] 입력값 정제 함수 (`sanitize_input()`)

---

### Phase 3: 인증 및 회원 관리 구현 (팀원 1 담당, 3-4일)

#### 3.1 DAO 계층
**파일**: `app/models/member_dao.py`

**Phase 3 매핑**: `MemberService.java`의 DB 작업 부분

**구현 메서드**:
```python
class MemberDAO:
    def __init__(self, db):
        self.db = db
    
    def find_by_id(self, user_id):
        """ID로 회원 조회"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT ID, Password, Name, Address, Sex, Birthday, IsAdmin FROM MEMBER WHERE ID = :id",
                id=user_id
            )
            row = cursor.fetchone()
            # DTO로 변환하여 반환
    
    def check_id_exists(self, user_id):
        """ID 중복 확인"""
    
    def insert_member(self, member_data):
        """회원가입"""
    
    def update_member(self, user_id, password, address):
        """회원정보 수정"""
```

**작업 내용**:
- [ ] `MemberDAO` 클래스 구현
- [ ] Phase 3의 SQL 쿼리 이식
- [ ] DTO 변환 로직 구현

#### 3.2 Service 계층
**파일**: `app/services/member_service.py`

**Phase 3 매핑**: `MemberService.java`의 비즈니스 로직

**구현 메서드**:
```python
class MemberService:
    def __init__(self, member_dao):
        self.member_dao = member_dao
    
    def register_member(self, form_data):
        """회원가입 처리"""
        # 1. ID 중복 확인
        if self.member_dao.check_id_exists(form_data['id']):
            raise ValueError("이미 사용 중인 ID입니다.")
        
        # 2. 필수 필드 검증
        # 3. 날짜 형식 검증
        # 4. DB에 INSERT
        with self.db.transaction():
            self.member_dao.insert_member(member_data)
    
    def modify_profile(self, user_id, form_data):
        """회원정보 수정"""
        # 1. 현재 정보 조회
        # 2. 변경사항만 업데이트
        with self.db.transaction():
            self.member_dao.update_member(user_id, ...)
```

**작업 내용**:
- [ ] `MemberService` 클래스 구현
- [ ] Phase 3의 비즈니스 로직 이식
- [ ] 트랜잭션 적용
- [ ] 예외 처리

#### 3.3 Controller 계층
**파일**: `app/controllers/auth_bp.py`, `app/controllers/member_bp.py`

**Phase 3 매핑**: `MainMenu.java`의 로그인/회원가입 처리

**구현 라우트**:
```python
from flask import Blueprint, render_template, request, session, redirect, url_for, flash

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['id']
        password = request.form['password']
        
        # MemberService를 통해 로그인 처리
        member = member_service.authenticate(user_id, password)
        if member:
            session['user_id'] = member['id']
            session['is_admin'] = (member['is_admin'] == 'T')
            return redirect(url_for('main.index'))
        else:
            flash('아이디 또는 비밀번호가 일치하지 않습니다.')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.index'))
```

**작업 내용**:
- [x] `auth_bp.py` 구현 (로그인/로그아웃) ✅ (임시 구현 완료)
- [x] `member_bp.py` 구현 (회원가입/회원정보 수정) ✅ (임시 구현 완료)
- [x] 세션 관리 ✅ (Flask Session 사용)
- [x] Flash 메시지 처리 ✅

#### 3.4 템플릿
**파일**: 
- `app/templates/auth/login.html`
- `app/templates/auth/register.html`
- `app/templates/member/profile_edit.html`

**작업 내용**:
- [x] 로그인 폼 구현 ✅ (`templates/auth/login.html`)
- [x] 회원가입 폼 구현 (필수/선택 필드 구분) ✅ (`templates/member/register.html`)
- [x] 회원정보 수정 폼 구현 ✅ (`templates/member/profile_edit.html`)
- [x] 폼 검증 (HTML5 + JavaScript) ✅ (HTML5 required 속성 + JS 검증)

---

### Phase 4: 콘텐츠 및 리뷰 관리 구현 (팀원 2 담당, 3-4일)

#### 4.1 DAO 계층
**파일**: `app/models/content_dao.py`

**Phase 3 매핑**: `ReviewService.java`, `ContentTab.java`의 DB 작업

**구현 메서드**:
```python
class ContentDAO:
    def search_by_title(self, search_term):
        """콘텐츠 제목으로 검색 (LIKE)"""
    
    def find_by_id(self, content_id):
        """콘텐츠 ID로 조회"""
    
    def insert_review(self, mid, cid, rating, comment):
        """리뷰 등록"""
```

**작업 내용**:
- [ ] `ContentDAO` 클래스 구현
- [ ] 콘텐츠 검색 쿼리 이식
- [ ] 리뷰 등록 쿼리 이식

#### 4.2 Service 계층
**파일**: `app/services/review_service.py`

**Phase 3 매핑**: `ReviewService.java`

**구현 메서드**:
```python
class ReviewService:
    def search_content(self, search_term):
        """콘텐츠 검색"""
        results = self.content_dao.search_by_title(search_term)
        return results
    
    def register_review(self, user_id, content_id, rating, comment):
        """리뷰 등록 (트랜잭션 필수)"""
        # 중복 리뷰 방지 (PK 제약조건)
        with self.db.transaction():
            try:
                self.content_dao.insert_review(user_id, content_id, rating, comment)
            except cx_Oracle.IntegrityError:
                raise ValueError("이미 해당 콘텐츠에 리뷰를 등록했습니다.")
```

**작업 내용**:
- [ ] `ReviewService` 클래스 구현
- [ ] 콘텐츠 검색 로직 이식
- [ ] 리뷰 등록 로직 이식
- [ ] 트랜잭션 적용 (중복 방지)

#### 4.3 Controller 계층
**파일**: `app/controllers/content_bp.py`

**구현 라우트**:
```python
content_bp = Blueprint('content', __name__, url_prefix='/contents')

@content_bp.route('/search', methods=['GET', 'POST'])
def search_content():
    """콘텐츠 검색"""
    if request.method == 'POST':
        search_term = request.form['search_term']
        results = review_service.search_content(search_term)
        return render_template('content/search_results.html', results=results)
    return render_template('content/search.html')

@content_bp.route('/<int:content_id>/review', methods=['GET', 'POST'])
@login_required  # 데코레이터로 로그인 확인
def create_review(content_id):
    """리뷰 등록"""
    if request.method == 'POST':
        rating = int(request.form['rating'])
        comment = request.form.get('comment', '')
        
        try:
            review_service.register_review(
                session['user_id'],
                content_id,
                rating,
                comment
            )
            flash('리뷰가 성공적으로 등록되었습니다.')
            return redirect(url_for('content.detail', content_id=content_id))
        except ValueError as e:
            flash(str(e))
    
    content = content_dao.find_by_id(content_id)
    return render_template('content/review_form.html', content=content)
```

**작업 내용**:
- [x] `content_bp.py` 구현 ✅
- [x] 콘텐츠 검색 라우트 ✅
- [x] 리뷰 등록 라우트 ✅
- [x] 로그인 데코레이터 구현 (`@login_required`) ✅ (`utils/decorators.py`)

#### 4.4 템플릿
**파일**:
- `app/templates/content/search.html`
- `app/templates/content/search_results.html`
- `app/templates/content/review_form.html`

**작업 내용**:
- [x] 콘텐츠 검색 폼 (자동완성 기능 추가 가능) ✅ (`templates/content/search.html`)
- [x] 검색 결과 목록 (여러 개일 경우 선택 UI) ✅ (`templates/content/search_results.html`)
- [x] 리뷰 등록 폼 (평점 1-5, 코멘트) ✅ (`templates/content/review_form.html`)

---

### Phase 5: 관리자 기능 및 쿼리 구현 (팀원 3 담당, 4-5일)

#### 5.1 DAO 계층
**파일**: `app/models/query_dao.py`

**Phase 3 매핑**: `QueryDAO.java` (10개 쿼리)

**구현 메서드**:
```python
class QueryDAO:
    def select_members_by_sex(self, sex):
        """Q 1-1: 특정 성별 회원 조회"""
    
    def select_recent_contents(self, release_date):
        """Q 1-2: 최신 콘텐츠 목록"""
    
    def select_reviews_by_prodco(self, prod_name):
        """Q 2-1: 제작사별 리뷰 조회"""
    
    def aggregate_rating_by_tag(self):
        """Q 3-1: 태그별 평점 통계"""
    
    # ... 나머지 6개 쿼리
```

**작업 내용**:
- [ ] `QueryDAO` 클래스 구현
- [ ] Phase 3의 10개 쿼리 모두 이식
- [ ] 결과를 딕셔너리/객체로 매핑

#### 5.2 Service 계층
**파일**: `app/services/admin_service.py`

**Phase 3 매핑**: `ContentTab.java`

**구현 메서드**:
```python
class AdminService:
    def insert_producer(self, producer_data):
        """제작사 등록"""
        with self.db.transaction():
            # ID 중복 확인
            # 외래키 참조 확인
            self.admin_dao.insert_producer(producer_data)
    
    def update_producer(self, producer_id, updates):
        """제작사 수정"""
    
    def delete_producer(self, producer_id):
        """제작사 삭제 (참조 확인)"""
        with self.db.transaction():
            if self.admin_dao.check_producer_referenced(producer_id):
                raise ValueError("콘텐츠가 등록되어있는 제작사입니다.")
            self.admin_dao.delete_producer(producer_id)
    
    # 콘텐츠, 시리즈 CRUD도 동일한 패턴
```

**작업 내용**:
- [ ] `AdminService` 클래스 구현
- [ ] 제작사/콘텐츠/시리즈 CRUD 로직 이식
- [ ] 외래키 참조 무결성 검사
- [ ] 트랜잭션 적용

#### 5.3 Controller 계층
**파일**: `app/controllers/admin_bp.py`

**구현 라우트**:
```python
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.before_request
def check_admin():
    """모든 관리자 라우트에 대해 권한 확인"""
    if not session.get('is_admin'):
        flash('관리자만 접근 가능합니다.')
        return redirect(url_for('main.index'))

@admin_bp.route('/producers', methods=['GET', 'POST'])
def manage_producers():
    """제작사 관리"""
    if request.method == 'POST':
        # INSERT/UPDATE/DELETE 처리
    producers = admin_service.list_producers()
    return render_template('admin/producers.html', producers=producers)

@admin_bp.route('/queries')
def query_menu():
    """쿼리 메뉴"""
    return render_template('admin/query_menu.html')

@admin_bp.route('/queries/<int:query_id>')
def execute_query(query_id):
    """쿼리 실행"""
    # query_id에 따라 다른 쿼리 실행
    result = query_dao.execute_query(query_id, **request.args)
    return render_template('admin/query_result.html', result=result)
```

**작업 내용**:
- [x] `admin_bp.py` 구현 ✅
- [x] 관리자 권한 확인 데코레이터 ✅ (`@admin_required`)
- [x] 제작사/콘텐츠/시리즈 CRUD 라우트 ✅ (템플릿 및 라우팅 완료)
- [x] 10개 쿼리 실행 라우트 ✅ (`query_menu`, `execute_query`)

#### 5.4 템플릿
**파일**:
- `app/templates/admin/producers.html`
- `app/templates/admin/contents.html`
- `app/templates/admin/series.html`
- `app/templates/admin/query_menu.html`
- `app/templates/admin/query_result.html`

**작업 내용**:
- [x] 관리자 대시보드 ✅ (`templates/admin/dashboard.html`)
- [x] CRUD 폼 (제작사/콘텐츠/시리즈) ✅ (템플릿 완료)
- [x] 쿼리 메뉴 페이지 ✅ (`templates/admin/query_menu.html`)
- [x] 쿼리 결과 테이블/차트 표시 ✅ (`templates/admin/query_result.html`)

---

### Phase 6: 동시성 제어 구현 (공동 작업, 2-3일)

#### 6.1 트랜잭션 격리 수준 설정
**파일**: `app/models/database.py` 수정

**구현 내용**:
```python
@contextmanager
def transaction(self, isolation_level='READ_COMMITTED'):
    """트랜잭션 컨텍스트 매니저 (격리 수준 설정)"""
    conn = self.pool.acquire()
    try:
        # 격리 수준 설정
        cursor = conn.cursor()
        cursor.execute(f"ALTER SESSION SET ISOLATION_LEVEL = {isolation_level}")
        
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        self.pool.release(conn)
```

#### 6.2 비관적 잠금 구현
**파일**: `app/services/review_service.py` 수정

**구현 내용**:
```python
def like_review(self, review_id, user_id):
    """리뷰 좋아요 증가 (동시성 제어)"""
    with self.db.transaction():
        # SELECT FOR UPDATE로 행 잠금
        cursor = conn.cursor()
        cursor.execute(
            "SELECT Likes FROM RATING WHERE MID = :mid AND CID = :cid FOR UPDATE",
            mid=review_mid,
            cid=review_cid
        )
        current_likes = cursor.fetchone()[0]
        
        # 좋아요 증가
        cursor.execute(
            "UPDATE RATING SET Likes = :likes WHERE MID = :mid AND CID = :cid",
            likes=current_likes + 1,
            mid=review_mid,
            cid=review_cid
        )
```

#### 6.3 낙관적 잠금 구현 (선택사항)
**파일**: `app/services/admin_service.py`

**구현 내용**:
```python
def update_content(self, content_id, updates, version):
    """콘텐츠 수정 (버전 기반 낙관적 잠금)"""
    with self.db.transaction():
        # 현재 버전 확인
        current_version = self.admin_dao.get_version(content_id)
        if current_version != version:
            raise ValueError("다른 사용자가 수정했습니다. 새로고침 후 다시 시도하세요.")
        
        # 업데이트 및 버전 증가
        self.admin_dao.update_content(content_id, updates, version + 1)
```

#### 6.4 동시성 테스트
**파일**: `tests/test_concurrency.py`

**테스트 시나리오**:
1. 여러 사용자가 동시에 리뷰 등록
2. 동일 콘텐츠에 중복 리뷰 방지 확인
3. 리뷰 좋아요 동시 증가 시 데이터 일관성 확인

**작업 내용**:
- [ ] 트랜잭션 격리 수준 설정
- [ ] 비관적 잠금 구현 (SELECT FOR UPDATE)
- [ ] 동시성 테스트 코드 작성
- [ ] `TeamX-Additional_task1.txt` 작성 (해결 방안 문서화)

---

### Phase 7: 통합 및 테스트 (공동 작업, 2-3일)

#### 7.1 통합 테스트
**작업 내용**:
- [ ] 전체 플로우 테스트 (회원가입 → 로그인 → 리뷰 등록)
- [ ] 관리자 기능 테스트
- [ ] 10개 쿼리 실행 테스트
- [ ] 에러 처리 테스트

#### 7.2 UI/UX 개선
**작업 내용**:
- [ ] 반응형 디자인 적용
- [ ] 로딩 인디케이터 추가
- [ ] 에러 메시지 개선
- [ ] 사용자 피드백 개선

#### 7.3 성능 최적화
**작업 내용**:
- [ ] Connection Pool 크기 조정
- [ ] 쿼리 최적화 (인덱스 확인)
- [ ] 템플릿 캐싱

---

### Phase 8: 문서화 및 제출 준비 (1일)

#### 8.1 보고서 작성
**파일**: `TeamX-task1.txt`

**내용**:
- 프로젝트 개요
- 구현한 기능 목록
- 아키텍처 설명
- 주요 기술 스택

#### 8.2 동시성 제어 문서
**파일**: `TeamX-Additional_task1.txt`

**내용**:
- 동시성 제어 구현 방법
- 트랜잭션 격리 수준 선택 이유
- 잠금 메커니즘 설명
- 테스트 결과

#### 8.3 제출물 준비
**작업 내용**:
- [ ] `TeamX-Phase4.zip` 압축
- [ ] README.md 작성
- [ ] 실행 방법 문서화
- [ ] Git 커밋 로그 정리

---

## 🔄 Phase 3 → Phase 4 코드 매핑 상세

### 인증 및 세션 관리

| Phase 3 | Phase 4 | 구현 방법 |
|:---|:---|:---|
| `static String currentUserId` | `session['user_id']` | Flask Session 사용 |
| `static boolean isAdmin` | `session['is_admin']` | Flask Session 사용 |
| `handleLoginOrLogout()` | `auth_bp.login()`, `auth_bp.logout()` | Blueprint 라우트 |

### 회원 관리

| Phase 3 | Phase 4 | 구현 방법 |
|:---|:---|:---|
| `MemberService.registerMember()` | `member_service.register_member()` | Service 계층 이식 |
| `MemberService.modifyMemberProfile()` | `member_service.modify_profile()` | Service 계층 이식 |
| `isIdDuplicated()` | `member_dao.check_id_exists()` | DAO 계층 이식 |

### 리뷰 관리

| Phase 3 | Phase 4 | 구현 방법 |
|:---|:---|:---|
| `ReviewService.registerReview()` | `review_service.register_review()` | Service 계층 이식 |
| `searchContentByTitle()` | `content_dao.search_by_title()` | DAO 계층 이식 |
| 콘솔 입력 (Scanner) | HTML Form + AJAX | 프론트엔드 구현 |

### 콘텐츠 관리

| Phase 3 | Phase 4 | 구현 방법 |
|:---|:---|:---|
| `ContentTab.insertProd()` | `admin_service.insert_producer()` | Service 계층 이식 |
| `ContentTab.updateProd()` | `admin_service.update_producer()` | Service 계층 이식 |
| `ContentTab.deleteProd()` | `admin_service.delete_producer()` | Service 계층 이식 |
| `checkPId()`, `checkSId()` | 외래키 참조 검사 | DAO 계층 이식 |

### 쿼리 실행

| Phase 3 | Phase 4 | 구현 방법 |
|:---|:---|:---|
| `QueryDAO.selectMembersBySex()` | `query_dao.select_members_by_sex()` | DAO 계층 이식 |
| `QueryUI.displayQueryMenu()` | `admin_bp.query_menu()` | Blueprint 라우트 |
| `QueryUI.executeSelectedQuery()` | `admin_bp.execute_query()` | Blueprint 라우트 |

---

## 🛠️ 기술 스택 상세

### 백엔드
- **Flask 3.0**: 웹 프레임워크
- **cx_Oracle 8.3**: Oracle DB 연결
- **Python 3.x**: 프로그래밍 언어

### 프론트엔드
- **Jinja2**: 템플릿 엔진
- **Bootstrap 5** (또는 Tailwind CSS): CSS 프레임워크
- **JavaScript**: 클라이언트 사이드 로직

### 데이터베이스
- **Oracle Database 21c**: 데이터베이스
- **Connection Pool**: 동시성 제어

---

## 📊 작업 일정 (3인 팀 기준)

| 주차 | Phase | 담당 | 작업 내용 |
|:---|:---|:---|:---|
| 1주차 | Phase 1-2 | 전체 | 프로젝트 설정, 공통 인프라 |
| 2주차 | Phase 3 | 팀원 1 | 인증 및 회원 관리 |
| 2주차 | Phase 4 | 팀원 2 | 콘텐츠 및 리뷰 관리 |
| 2주차 | Phase 5 | 팀원 3 | 관리자 기능 및 쿼리 |
| 3주차 | Phase 6 | 전체 | 동시성 제어 구현 |
| 3주차 | Phase 7-8 | 전체 | 통합 테스트 및 문서화 |

**총 예상 기간**: 3주 (15일)

---

## ✅ 체크리스트 요약

### 필수 구현 항목
- [ ] Flask 프로젝트 초기 설정
- [ ] Connection Pool 구현
- [ ] 트랜잭션 관리 구현
- [ ] 인증/회원가입/로그아웃
- [ ] 리뷰 등록 및 콘텐츠 검색
- [ ] 관리자 CRUD (제작사/콘텐츠/시리즈)
- [ ] 10개 쿼리 실행 기능
- [ ] 동시성 제어 구현
- [ ] 보고서 작성

### 개선 사항 (선택)
- [ ] 리뷰 좋아요 기능 (동시성 제어 예시)
- [ ] 콘텐츠 검색 자동완성
- [ ] 쿼리 결과 차트 시각화
- [ ] 페이지네이션
- [ ] 파일 업로드 (이미지 등)

---

## 🎓 학습 포인트

### Phase 3에서 배울 점
1. **계층 분리**: Service-DAO 패턴의 중요성
2. **비즈니스 로직**: ID 중복 확인, 외래키 검사 등
3. **SQL 쿼리**: 다양한 조인, 집계, 서브쿼리

### Phase 4에서 새로 배울 점
1. **웹 아키텍처**: MVC 패턴, Blueprint 모듈화
2. **세션 관리**: Flask Session 사용법
3. **트랜잭션**: 동시성 제어, 격리 수준
4. **프론트엔드**: HTML/CSS/JavaScript 기초

---

## 📝 참고사항

### Git 협업 전략
1. **브랜치 전략**: `main` (프로덕션), `develop` (개발), `feature/*` (기능별)
2. **커밋 메시지**: 명확한 메시지 작성 (예: "feat: 회원가입 기능 구현")
3. **코드 리뷰**: Pull Request를 통한 코드 리뷰

### 디버깅 팁
1. Flask Debug 모드 활성화 (`app.run(debug=True)`)
2. Oracle DB 로그 확인
3. 브라우저 개발자 도구 활용

### 성능 고려사항
1. Connection Pool 크기 조정 (동시 접속자 수 고려)
2. 쿼리 최적화 (인덱스 활용)
3. 템플릿 캐싱

---

## 📝 실제 구현 진행 상황 (2024년 업데이트)

### ✅ 완료된 작업 (Phase 1-2, 부분 Phase 3-5)

#### Phase 1: 프로젝트 초기 설정
- ✅ 프로젝트 폴더 구조 생성 완료 (`project/app/` 디렉토리)
- ✅ `requirements.txt` 작성 완료
- ✅ Flask 앱 기본 구조 생성 (`app/__init__.py`, `app/app.py`, `app/config.py`)

#### Phase 2: 공통 인프라 구축
- ✅ Flask 앱 팩토리 함수 구현 (`app/__init__.py`)
- ✅ 설정 파일 구현 (`app/config.py` - Development/Production 환경 분리)
- ✅ 공통 레이아웃 템플릿 구현 (`templates/layout/base.html`)
  - Bootstrap 5 적용
  - 동적 네비게이션 바 (로그인 상태에 따른 메뉴 변경)
  - Flash 메시지 표시 영역
- ✅ 유틸리티 데코레이터 구현 (`app/utils/decorators.py`)
  - `@login_required` 데코레이터
  - `@admin_required` 데코레이터

#### Phase 3-5: 모든 Blueprint 및 템플릿 구현 완료
- ✅ 인증 및 회원 관리 (`auth_bp.py`, `member_bp.py`)
- ✅ 콘텐츠 및 리뷰 관리 (`content_bp.py`)
- ✅ 관리자 기능 및 쿼리 (`admin_bp.py`)
- ✅ 모든 템플릿 파일 구현 완료 (총 15개 템플릿)

### ⏳ 추후 구현 예정
- [ ] 데이터베이스 연결 (`app/models/database.py`)
- [ ] DAO 계층 구현 (`app/models/*_dao.py`)
- [ ] Service 계층 구현 (`app/services/*_service.py`)
- [ ] 실제 비즈니스 로직 연동
- [ ] 동시성 제어 구현

**작성일**: 2024년  
**목적**: Phase 3 → Phase 4 전환을 위한 구체적인 구현 계획서  
**최종 업데이트**: 2024년 - 초기 프로젝트 구조 및 템플릿 구현 완료

