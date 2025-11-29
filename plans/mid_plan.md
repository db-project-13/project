# Team13-Phase4 중간 계획서 (Mid-Term Plan)

**작성일**: 2025-11-29  
**목적**: 현재 구현 상태 검토 및 새로운 요구사항 반영을 통한 향후 구현 방향성 제시

---

## 📊 현재 구현 상태 요약

### ✅ 완료된 작업 (프론트엔드 구조)

#### 1. 프로젝트 기본 구조
- ✅ Flask 앱 팩토리 함수 (`app/__init__.py`)
- ✅ 설정 파일 (`app/config.py` - Development/Production 분리)
- ✅ 공통 레이아웃 템플릿 (`templates/layout/base.html`)
- ✅ Bootstrap 5 적용 및 동적 네비게이션 바
- ✅ Flash 메시지 표시 영역
- ✅ 유틸리티 데코레이터 (`@login_required`, `@admin_required`)

#### 2. Blueprint 및 라우팅 (5개)
- ✅ `main_bp.py` - 메인 페이지
- ✅ `auth_bp.py` - 로그인/로그아웃
- ✅ `member_bp.py` - 회원가입/회원정보 수정
- ✅ `content_bp.py` - 콘텐츠 검색/상세/리뷰 등록
- ✅ `admin_bp.py` - 관리자 기능 (제작사/콘텐츠/시리즈/쿼리)

#### 3. 템플릿 파일 (15개)
- ✅ `main/index.html` - 메인 페이지
- ✅ `auth/login.html` - 로그인
- ✅ `member/register.html` - 회원가입
- ✅ `member/profile_edit.html` - 회원정보 수정
- ✅ `content/search.html` - 콘텐츠 검색
- ✅ `content/search_results.html` - 검색 결과
- ✅ `content/detail.html` - 콘텐츠 상세
- ✅ `content/review_form.html` - 리뷰 등록
- ✅ `admin/dashboard.html` - 관리자 대시보드
- ✅ `admin/producers.html` - 제작사 관리
- ✅ `admin/contents.html` - 콘텐츠 관리
- ✅ `admin/series.html` - 시리즈 관리
- ✅ `admin/query_menu.html` - 쿼리 메뉴
- ✅ `admin/query_result.html` - 쿼리 결과

### ⏳ 미구현 작업 (백엔드 로직)

#### 1. 데이터베이스 계층
- ❌ `app/models/database.py` - Connection Pool 구현
- ❌ `app/models/member_dao.py` - 회원 DAO
- ❌ `app/models/content_dao.py` - 콘텐츠 DAO
- ❌ `app/models/query_dao.py` - 쿼리 DAO
- ❌ `app/models/admin_dao.py` - 관리자 DAO

#### 2. 서비스 계층
- ❌ `app/services/member_service.py` - 회원 서비스
- ❌ `app/services/review_service.py` - 리뷰 서비스
- ❌ `app/services/admin_service.py` - 관리자 서비스

#### 3. 유틸리티 함수
- ❌ `app/utils/validators.py` - 입력값 검증 함수

---

## 🎯 새로운 요구사항 분석

### 1. 메인 화면 개선 요구사항

#### 현재 상태
- ✅ 메인 페이지 존재 (`main/index.html`)
- ✅ 로그인/회원가입 링크 존재
- ⚠️ 콘텐츠 목록 표시 없음
- ⚠️ 테마별(영화/게임/도서) 탭 없음

#### 요구사항
1. **메인 화면에서 로그인/회원가입 가능**
   - ✅ 현재: 네비게이션 바에 로그인/회원가입 링크 존재
   - ⚠️ 개선 필요: 메인 페이지 본문에 더 명확한 로그인/회원가입 버튼 추가

2. **완료 후 메인으로 복귀**
   - ✅ 현재: `auth_bp.py`에서 로그인 성공 시 `redirect(url_for('main.index'))` 구현됨
   - ✅ 현재: `member_bp.py`에서 회원가입 성공 시 `redirect(url_for('auth.login'))` 구현됨
   - ⚠️ 개선 필요: 회원가입 성공 후 메인으로 복귀하도록 변경 권장

3. **메인 상단에 홈, 콘텐츠 검색(영화/게임/도서 탭)**
   - ✅ 현재: 네비게이션 바에 "홈", "콘텐츠 검색" 링크 존재
   - ❌ 누락: 영화/게임/도서 테마별 탭 없음
   - **필요 작업**: 테마별 필터링 기능 추가

4. **메인 페이지 하단에 전체 내용 정렬된 리스트**
   - ❌ 누락: 콘텐츠 목록 표시 기능 없음
   - **필요 작업**: 메인 페이지에 최신 콘텐츠 목록 표시

### 2. 회원 관련 페이지 개선 요구사항

#### 현재 상태
- ✅ 회원가입 페이지 존재 (`member/register.html`)
- ✅ 회원정보 수정 페이지 존재 (`member/profile_edit.html`)
- ❌ 회원정보 조회 페이지 없음

#### 요구사항
1. **로그인 후 마이페이지 형태로 수정/반영 가능**
   - ✅ 현재: 회원정보 수정 페이지 존재
   - ❌ 누락: 회원정보 조회 페이지(마이페이지) 없음
   - **필요 작업**: 
     - `member_bp.py`에 `/profile` 라우트 추가
     - `templates/member/profile.html` 템플릿 생성
     - 회원정보 조회 + 수정 페이지로 이동 링크

### 3. 콘텐츠 관련 페이지 개선 요구사항

#### 현재 상태
- ✅ 콘텐츠 검색 페이지 존재 (`content/search.html`)
- ✅ 콘텐츠 상세 페이지 존재 (`content/detail.html`)
- ✅ 리뷰 등록 페이지 존재 (`content/review_form.html`)
- ⚠️ 테마별 분류 없음
- ⚠️ 일반 사용자 콘텐츠 등록 기능 없음

#### 요구사항
1. **세부 화면에서 각 테마(영화/게임/도서)별 콘텐츠 등록 가능**
   - ✅ 현재: 관리자만 콘텐츠 등록 가능 (`admin/contents.html`)
   - ❌ 누락: 일반 사용자도 테마별 콘텐츠 등록 기능 없음
   - **필요 작업**:
     - 일반 사용자용 콘텐츠 등록 페이지 추가
     - 테마 선택 기능 (영화/게임/도서)
     - `content_bp.py`에 `/create` 라우트 추가

2. **콘텐츠 클릭 시 상세 항목 표시 및 리뷰 등록**
   - ✅ 현재: 콘텐츠 상세 페이지 존재 (`content/detail.html`)
   - ✅ 현재: 리뷰 등록 페이지 존재 (`content/review_form.html`)
   - ✅ 현재: 상세 페이지에서 리뷰 작성 버튼 존재
   - ⚠️ 개선 필요: 상세 페이지에서 리뷰 목록 표시 개선

### 4. 관리자 기능 요구사항

#### 현재 상태
- ✅ 제작사 관리 페이지 존재 (`admin/producers.html`)
- ✅ 콘텐츠 관리 페이지 존재 (`admin/contents.html`)
- ✅ 시리즈 관리 페이지 존재 (`admin/series.html`)
- ❌ 태그 관리 페이지 없음

#### 요구사항
1. **제작사, 태그, 시리즈는 admin 계정으로 관리**
   - ✅ 현재: 제작사, 시리즈 관리 페이지 존재
   - ❌ 누락: 태그 관리 페이지 없음
   - **필요 작업**:
     - `admin_bp.py`에 `/tags` 라우트 추가
     - `templates/admin/tags.html` 템플릿 생성
     - 태그 CRUD 기능 구현

### 5. 동시성 제어 요구사항

#### 현재 상태
- ❌ 동시성 제어 구현 없음
- ❌ Connection Pool 없음
- ❌ 트랜잭션 관리 없음

#### 요구사항
1. **여러 사용자가 동시에 접속 가능**
   - ❌ 현재: Connection Pool 미구현
   - **필요 작업**: `app/models/database.py`에 Connection Pool 구현

2. **수정된 내용들이 적절히 DB에 crash 없이 (dirty update 방지) 진행**
   - ❌ 현재: 트랜잭션 관리 없음
   - ❌ 현재: 잠금 메커니즘 없음
   - **필요 작업**:
     - 트랜잭션 격리 수준 설정
     - 비관적 잠금 구현 (SELECT FOR UPDATE)
     - 리뷰 등록 시 중복 방지 (PK 제약조건 활용)

---

## 📋 우선순위별 구현 계획

### 🔴 높은 우선순위 (즉시 구현 필요)

#### 1. 데이터베이스 연결 및 기본 인프라
**목표**: 백엔드 로직 구현의 기반 마련

**작업 내용**:
- [ ] `app/models/database.py` 구현
  - Connection Pool 초기화 (`cx_Oracle.ConnectionPool`)
  - `get_connection()` 컨텍스트 매니저
  - `transaction()` 컨텍스트 매니저 (트랜잭션 관리)
- [ ] `app/__init__.py`에서 데이터베이스 초기화 연동
- [ ] 환경 변수 설정 (`.env` 파일)

**예상 소요 시간**: 1-2일

#### 2. 회원정보 조회 페이지 (마이페이지)
**목표**: 사용자 요구사항 충족

**작업 내용**:
- [ ] `member_bp.py`에 `/profile` 라우트 추가
- [ ] `templates/member/profile.html` 템플릿 생성
- [ ] 회원정보 조회 기능 구현
- [ ] 회원정보 수정 페이지로 이동 링크 추가

**예상 소요 시간**: 0.5일

#### 3. 태그 관리 페이지
**목표**: 관리자 기능 완성

**작업 내용**:
- [ ] `admin_bp.py`에 `/tags` 라우트 추가
- [ ] `templates/admin/tags.html` 템플릿 생성
- [ ] 태그 CRUD 기능 구현 (등록/수정/삭제)

**예상 소요 시간**: 1일

#### 4. 메인 페이지 콘텐츠 목록 표시
**목표**: 사용자 요구사항 충족

**작업 내용**:
- [ ] `main_bp.py`에서 최신 콘텐츠 목록 조회
- [ ] `templates/main/index.html`에 콘텐츠 목록 섹션 추가
- [ ] 정렬 기능 (최신순, 인기순 등)

**예상 소요 시간**: 1일

### 🟡 중간 우선순위 (단계별 구현)

#### 5. 테마별(영화/게임/도서) 분류 기능
**목표**: 콘텐츠 분류 체계 구축

**작업 내용**:
- [ ] 데이터베이스 스키마 확인 (TAG 테이블 활용 가능 여부 확인)
- [ ] 콘텐츠 검색 페이지에 테마 필터 추가
- [ ] 네비게이션 바에 테마별 탭 추가
- [ ] 메인 페이지에 테마별 콘텐츠 섹션 추가

**예상 소요 시간**: 2일

#### 6. 일반 사용자 콘텐츠 등록 기능
**목표**: 사용자 요구사항 충족

**작업 내용**:
- [ ] `content_bp.py`에 `/create` 라우트 추가
- [ ] `templates/content/create.html` 템플릿 생성
- [ ] 테마 선택 기능 (영화/게임/도서)
- [ ] 콘텐츠 등록 폼 구현

**예상 소요 시간**: 1-2일

#### 7. DAO 계층 구현
**목표**: 데이터 접근 로직 구현

**작업 내용**:
- [ ] `app/models/member_dao.py` 구현
- [ ] `app/models/content_dao.py` 구현
- [ ] `app/models/query_dao.py` 구현
- [ ] `app/models/admin_dao.py` 구현

**예상 소요 시간**: 3-4일

#### 8. Service 계층 구현
**목표**: 비즈니스 로직 구현

**작업 내용**:
- [ ] `app/services/member_service.py` 구현
- [ ] `app/services/review_service.py` 구현
- [ ] `app/services/admin_service.py` 구현

**예상 소요 시간**: 3-4일

### 🟢 낮은 우선순위 (추가 개선)

#### 9. 동시성 제어 구현
**목표**: 동시 접속 환경 대응

**작업 내용**:
- [ ] 트랜잭션 격리 수준 설정
- [ ] 비관적 잠금 구현 (SELECT FOR UPDATE)
- [ ] 리뷰 좋아요 동시 증가 시나리오 테스트
- [ ] 동시성 제어 테스트 페이지 생성

**예상 소요 시간**: 2-3일

#### 10. 유틸리티 함수 구현
**목표**: 코드 재사용성 향상

**작업 내용**:
- [ ] `app/utils/validators.py` 구현
  - 날짜 형식 검증
  - ID 중복 검사 헬퍼
  - 입력값 정제 함수

**예상 소요 시간**: 0.5일

---

## 🔄 기존 계획서와의 차이점

### 추가된 요구사항

1. **테마별 분류 (영화/게임/도서)**
   - 기존 계획서: 명시되지 않음
   - 새로운 요구사항: 테마별 콘텐츠 분류 및 필터링 필요

2. **일반 사용자 콘텐츠 등록**
   - 기존 계획서: 관리자만 콘텐츠 등록 가능
   - 새로운 요구사항: 일반 사용자도 테마별 콘텐츠 등록 가능

3. **메인 페이지 콘텐츠 목록**
   - 기존 계획서: 메인 페이지에 콘텐츠 목록 표시 명시되지 않음
   - 새로운 요구사항: 메인 페이지 하단에 전체 콘텐츠 정렬된 리스트 표시

4. **회원정보 조회 페이지 (마이페이지)**
   - 기존 계획서: 회원정보 수정 페이지만 존재
   - 새로운 요구사항: 마이페이지 형태의 회원정보 조회 페이지 필요

### 유지된 요구사항

1. ✅ 로그인/회원가입 후 메인으로 복귀
2. ✅ 콘텐츠 상세 및 리뷰 등록 기능
3. ✅ 관리자 기능 (제작사/태그/시리즈 관리)
4. ✅ 동시성 제어 (트랜잭션, 잠금)

---

## 📐 페이지 흐름도 (Page Flow)

### 비로그인 사용자 흐름
```
메인 페이지 (/)
  ├─ 로그인 (/auth/login) → 메인으로 복귀
  ├─ 회원가입 (/member/register) → 메인으로 복귀
  ├─ 콘텐츠 검색 (/content/search)
  │   └─ 검색 결과 (/content/search_results)
  │       └─ 콘텐츠 상세 (/content/<id>) → 로그인 필요 안내
  └─ 콘텐츠 목록 (메인 페이지 하단)
```

### 로그인 사용자 흐름
```
메인 페이지 (/)
  ├─ 마이페이지 (/member/profile)
  │   └─ 회원정보 수정 (/member/profile/edit)
  ├─ 콘텐츠 검색 (/content/search)
  │   ├─ 검색 결과 (/content/search_results)
  │   └─ 테마별 필터 (영화/게임/도서)
  ├─ 콘텐츠 상세 (/content/<id>)
  │   ├─ 리뷰 등록 (/content/<id>/review)
  │   └─ 리뷰 목록 표시
  ├─ 콘텐츠 등록 (/content/create) [새로 추가]
  │   └─ 테마 선택 (영화/게임/도서)
  └─ 콘텐츠 목록 (메인 페이지 하단)
```

### 관리자 흐름
```
관리자 대시보드 (/admin)
  ├─ 제작사 관리 (/admin/producers)
  ├─ 콘텐츠 관리 (/admin/contents)
  ├─ 시리즈 관리 (/admin/series)
  ├─ 태그 관리 (/admin/tags) [새로 추가]
  └─ 쿼리 실행 (/admin/queries)
      └─ 쿼리 결과 (/admin/queries/<id>)
```

---

## 🗂️ 데이터베이스 스키마 활용 방안

### TAG 테이블을 활용한 테마 분류

**현재 스키마**:
```sql
CREATE TABLE TAG(
    TagCode INT NOT NULL,
    Category VARCHAR(15) NOT NULL,
    Tag VARCHAR(30) NOT NULL,
    PRIMARY KEY (TagCode)
);

CREATE TABLE TAG_TO(
    TCode INT NOT NULL,
    CID INT NOT NULL,
    PRIMARY KEY (TCode, CID),
    FOREIGN KEY (TCode) REFERENCES TAG(TagCode),
    FOREIGN KEY (CID) REFERENCES CONTENT(ContentID)
);
```

**활용 방안**:
1. **테마 분류**: TAG 테이블의 `Category` 컬럼을 "Theme"로 사용
   - 예: `Category='Theme'`, `Tag='Movie'` (영화)
   - 예: `Category='Theme'`, `Tag='Game'` (게임)
   - 예: `Category='Theme'`, `Tag='Book'` (도서)

2. **장르 분류**: TAG 테이블의 `Category` 컬럼을 "Genre"로 사용
   - 예: `Category='Genre'`, `Tag='Fantasy'` (판타지)
   - 예: `Category='Genre'`, `Tag='Action'` (액션)

3. **콘텐츠-태그 연결**: TAG_TO 테이블을 통해 콘텐츠와 태그 연결

**구현 예시**:
```python
# 테마별 콘텐츠 조회
def get_contents_by_theme(theme):
    """테마별 콘텐츠 조회 (영화/게임/도서)"""
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.ContentID, c.Title, c.ReleaseDate
            FROM CONTENT c
            JOIN TAG_TO tt ON c.ContentID = tt.CID
            JOIN TAG t ON tt.TCode = t.TagCode
            WHERE t.Category = 'Theme' AND t.Tag = :theme
            ORDER BY c.ReleaseDate DESC
        """, theme=theme)
        return cursor.fetchall()
```

---

## 🎨 UI/UX 개선 사항

### 1. 메인 페이지 개선

**현재 구조**:
- 시스템 상태 표시
- 주요 기능 링크
- 개발 상태 표시

**개선 방안**:
- 상단: 로그인/회원가입 버튼 (비로그인 시)
- 중간: 테마별 탭 (영화/게임/도서)
- 하단: 전체 콘텐츠 목록 (카드 형태)
  - 최신순 정렬
  - 인기순 정렬 옵션
  - 페이지네이션

### 2. 네비게이션 바 개선

**현재 구조**:
- 홈
- 콘텐츠 검색

**개선 방안**:
- 홈
- 영화
- 게임
- 도서
- 콘텐츠 검색

### 3. 콘텐츠 상세 페이지 개선

**현재 구조**:
- 콘텐츠 정보 표시
- 리뷰 작성 버튼
- 리뷰 목록 표시

**개선 방안**:
- 콘텐츠 정보 (제목, 출시일, 제작사, 시리즈, 태그)
- 리뷰 통계 (평균 평점, 총 리뷰 수)
- 리뷰 목록 (평점순, 최신순 정렬)
- 리뷰 작성 폼 (인라인 또는 별도 페이지)

---

## 🔐 동시성 제어 구현 방안

### 1. Connection Pool 설정

```python
# app/models/database.py
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
        """Connection 가져오기"""
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

### 2. 리뷰 등록 시 중복 방지

```python
# app/services/review_service.py
def register_review(self, user_id, content_id, rating, comment):
    """리뷰 등록 (트랜잭션 필수)"""
    with self.db.transaction() as conn:
        # 중복 리뷰 확인
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM RATING 
            WHERE MID = :mid AND CID = :cid
        """, mid=user_id, cid=content_id)
        
        if cursor.fetchone()[0] > 0:
            raise ValueError("이미 해당 콘텐츠에 리뷰를 등록했습니다.")
        
        # 리뷰 등록 (PK 제약조건으로도 중복 방지)
        try:
            cursor.execute("""
                INSERT INTO RATING (MID, CID, Rating, Comm, Likes)
                VALUES (:mid, :cid, :rating, :comment, 0)
            """, mid=user_id, cid=content_id, rating=rating, comment=comment)
        except cx_Oracle.IntegrityError:
            raise ValueError("이미 해당 콘텐츠에 리뷰를 등록했습니다.")
```

### 3. 리뷰 좋아요 동시 증가 방지

```python
# app/services/review_service.py
def like_review(self, user_id, content_id, review_user_id):
    """리뷰 좋아요 증가 (비관적 잠금)"""
    with self.db.transaction() as conn:
        cursor = conn.cursor()
        # SELECT FOR UPDATE로 행 잠금
        cursor.execute("""
            SELECT Likes FROM RATING 
            WHERE MID = :mid AND CID = :cid 
            FOR UPDATE
        """, mid=review_user_id, cid=content_id)
        
        current_likes = cursor.fetchone()[0]
        
        # 좋아요 증가
        cursor.execute("""
            UPDATE RATING 
            SET Likes = :likes 
            WHERE MID = :mid AND CID = :cid
        """, likes=current_likes + 1, mid=review_user_id, cid=content_id)
```

---

## 📅 구현 일정 (3인 팀 기준)

### 1주차: 데이터베이스 연결 및 기본 기능
- **팀원 1**: 데이터베이스 연결 (`database.py`), 회원정보 조회 페이지
- **팀원 2**: 메인 페이지 콘텐츠 목록, 태그 관리 페이지
- **팀원 3**: 테마별 분류 기능, 일반 사용자 콘텐츠 등록

### 2주차: DAO/Service 계층 구현
- **팀원 1**: `MemberDAO`, `MemberService` 구현
- **팀원 2**: `ContentDAO`, `ReviewService` 구현
- **팀원 3**: `AdminDAO`, `QueryDAO`, `AdminService` 구현

### 3주차: 통합 및 동시성 제어
- **전체**: Controller와 Service 연동
- **전체**: 동시성 제어 구현 및 테스트
- **전체**: UI/UX 개선 및 버그 수정

---

## ✅ 체크리스트

### 즉시 구현 필요
- [ ] 데이터베이스 연결 (`app/models/database.py`)
- [ ] 회원정보 조회 페이지 (`/member/profile`)
- [ ] 태그 관리 페이지 (`/admin/tags`)
- [ ] 메인 페이지 콘텐츠 목록 표시

### 단계별 구현
- [ ] 테마별 분류 기능 (영화/게임/도서)
- [ ] 일반 사용자 콘텐츠 등록 기능
- [ ] DAO 계층 구현
- [ ] Service 계층 구현
- [ ] Controller와 Service 연동

### 추가 개선
- [ ] 동시성 제어 구현
- [ ] 유틸리티 함수 구현
- [ ] UI/UX 개선
- [ ] 성능 최적화

---

## 📌 결론 및 권장 사항

### 현재 상태
- **프론트엔드 구조**: 약 95% 완료 (템플릿/라우팅)
- **백엔드 로직**: 약 0% 완료 (DAO/Service 미구현)
- **요구사항 충족도**: 약 60% (누락된 페이지 및 기능 존재)

### 다음 단계
1. **즉시 시작**: 데이터베이스 연결 구현 (`database.py`)
2. **우선 구현**: 회원정보 조회 페이지, 태그 관리 페이지
3. **단계적 구현**: DAO/Service 계층 구현 후 Controller 연동
4. **최종 구현**: 동시성 제어 및 통합 테스트

### 주의사항
- 데이터베이스 스키마 확인 필요 (TAG 테이블을 테마 분류에 활용)
- 동시성 제어는 트랜잭션과 잠금 메커니즘을 적절히 활용
- 사용자 경험을 고려한 UI/UX 개선 지속 필요

---

**작성자**: AI Assistant  
**최종 업데이트**: 2024년

