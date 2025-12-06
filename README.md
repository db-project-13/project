# Team13-Phase4 Flask 웹 애플리케이션

Phase 3 콘솔 애플리케이션을 Flask 기반 웹 애플리케이션으로 전환한 프로젝트입니다.

## 📋 프로젝트 개요

- **프로젝트명**: Team13-Phase4
- **유형**: Flask 기반 웹 애플리케이션 (BE: Flask, FE: Jinja2/HTML/CSS/JS)
- **데이터베이스**: Oracle Database 21c
- **목표**: Phase 3의 필수 기능 탑재 및 트랜잭션을 활용한 사용자 동시성 제어를 지원하는 데이터베이스 웹 사이트 구축

## 🏗️ 프로젝트 구조

```
project/
├── app/                          # Flask 애플리케이션 모듈
│   ├── __init__.py              # Flask 앱 팩토리
│   ├── config.py                # 설정 파일 (Development/Production)
│   ├── controllers/             # Blueprint 컨트롤러 (URL 라우팅)
│   │   ├── main_bp.py          # 메인 페이지
│   │   ├── auth_bp.py          # 인증 (로그인/로그아웃)
│   │   ├── member_bp.py        # 회원 관리
│   │   ├── content_bp.py       # 콘텐츠 및 리뷰
│   │   └── admin_bp.py         # 관리자 기능
│   ├── services/                # 비즈니스 로직 계층 (추후 구현)
│   ├── models/                  # 데이터 접근 계층 (추후 구현)
│   ├── utils/                   # 유틸리티 함수
│   │   └── decorators.py       # @login_required, @admin_required
│   ├── templates/               # Jinja2 템플릿 (View 계층)
│   │   ├── layout/
│   │   │   └── base.html       # 공통 레이아웃
│   │   ├── main/                # 메인 페이지
│   │   ├── auth/                # 로그인/회원가입
│   │   ├── member/              # 회원 정보
│   │   ├── content/             # 콘텐츠 및 리뷰
│   │   └── admin/               # 관리자 기능
│   └── static/                  # 정적 파일 (CSS, JS)
│       ├── css/
│       └── js/
├── plans/                       # 프로젝트 계획 및 문서화 자료
│   ├── mid_plan.md              # 최종 구현 계획서
│   ├── team13-phase3-readme.md  # Phase 3 분석 문서
│   └── archive/                 # 히스토리 문서
├── venv/                        # Python 가상 환경 (Git 제외)
├── requirements.txt             # Python 의존성
├── run.py                       # 애플리케이션 진입점
├── .env.sample                  # 환경 변수 설정 예제 파일
├── .gitignore                   # Git 제외 파일 목록
└── README.md                    # 프로젝트 설명 (이 파일)
```

## ✅ 현재 구현 상태

### 완료된 작업 (프론트엔드 구조)

#### 1. 프로젝트 기본 구조
- ✅ Flask 앱 팩토리 함수 (`app/__init__.py`)
- ✅ 설정 파일 (`app/config.py` - Development/Production 분리)
- ✅ 공통 레이아웃 템플릿 (`templates/layout/base.html`)
- ✅ Bootstrap 5 적용 및 동적 네비게이션 바
- ✅ Flash 메시지 표시 영역
- ✅ 유틸리티 데코레이터 (`@login_required`, `@admin_required`)

#### 2. Blueprint 및 라우팅 (5개)
- ✅ `main_bp.py` - 메인 페이지 (`/`)
- ✅ `auth_bp.py` - 로그인/로그아웃 (`/auth/login`, `/auth/logout`)
- ✅ `member_bp.py` - 회원가입/회원정보 수정 (`/member/register`, `/member/profile/edit`)
- ✅ `content_bp.py` - 콘텐츠 검색/상세/리뷰 등록 (`/content/*`)
- ✅ `admin_bp.py` - 관리자 기능 (`/admin/*`)

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

#### 3. 추가 기능
- ❌ 회원정보 조회 페이지 (마이페이지)
- ❌ 태그 관리 페이지
- ❌ 테마별 분류 기능 (영화/게임/도서)
- ❌ 메인 페이지 콘텐츠 목록 표시
- ❌ 일반 사용자 콘텐츠 등록 기능
- ❌ 동시성 제어 구현

## 🚀 실행 방법

### 1. 사전 요구사항
- Python 3.11 이상 (oracledb 요구사항)
- Oracle Database 19c or 21c 등 (로컬 또는 Docker)
- Oracle Instant Client (oracledb 사용 시, 선택사항 - Thin 모드 사용 가능)

### 2. 가상 환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정 (권장사항)
`.env.sample` 파일을 참고하여 `.env` 파일을 생성하세요:

```bash
# .env.sample 파일을 복사하여 .env 파일 생성
cp .env.sample .env

# .env 파일을 열어 실제 값으로 수정
# - DB_USER: 실제 데이터베이스 사용자명
# - DB_PASSWORD: 실제 데이터베이스 비밀번호
# - SECRET_KEY: 프로덕션에서는 강력한 랜덤 문자열로 변경
```

`.env` 파일 예시:
```bash
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here
DB_DSN=localhost:1521/orcl
DB_USER=your-db-username
DB_PASSWORD=your-db-password
DB_POOL_MIN=2
DB_POOL_MAX=10
```

**주의**: `.env` 파일은 Git에 커밋되지 않습니다 (`.gitignore`에 포함됨). 실제 비밀번호나 민감한 정보를 포함하므로 주의하세요.

### 4-1. db초기화
```bash
python app\init_db.py
```

### 5. 애플리케이션 실행
```bash
python run.py
```

### 6. 브라우저에서 접속
```
http://localhost:8000
```

## 🎯 주요 기능

### 현재 구현된 기능 (템플릿/라우팅)
- **인증**: 로그인/로그아웃 (임시 구현)
- **회원 관리**: 회원가입, 회원정보 수정 (템플릿만 구현)
- **콘텐츠 검색**: 콘텐츠 검색 및 리뷰 등록 (템플릿만 구현)
- **관리자 기능**: 제작사/콘텐츠/시리즈 관리, 쿼리 실행 (템플릿만 구현)

### 계획된 기능 (미구현)
- 실제 데이터베이스 연동
- 회원정보 조회 페이지 (마이페이지)
- 태그 관리 페이지
- 테마별 콘텐츠 분류 (영화/게임/도서)
- 메인 페이지 콘텐츠 목록 표시
- 일반 사용자 콘텐츠 등록 기능
- 동시성 제어 (트랜잭션, 잠금)

## 📚 문서 구조

프로젝트의 상세한 계획 및 문서는 `plans/` 폴더에 있습니다:

- **`plans/mid_plan.md`** - 최종 구현 계획서
  - 현재 구현 상태 상세 분석
  - 새로운 요구사항 분석
  - 우선순위별 구현 계획
  - 데이터베이스 스키마 활용 방안
  - 동시성 제어 구현 방안

- **`plans/team13-phase3-readme.md`** - Phase 3 분석 문서
  - Phase 3 콘솔 애플리케이션 구조 및 로직 분석
  - Phase 4 전환 시 참고 자료

- **`plans/archive/`** - 히스토리 문서
  - 개발 과정에서 생성된 중간 문서들

자세한 내용은 [`plans/README.md`](plans/README.md)를 참고하세요.

## 🔧 개발 가이드

### 폴더 구조 확인
프로젝트의 전체 구조는 위의 "프로젝트 구조" 섹션을 참고하세요.

### 라우팅 확인
각 Blueprint 파일(`app/controllers/*_bp.py`)에서 URL 라우팅을 확인할 수 있습니다.

### 템플릿 확인
모든 템플릿은 `app/templates/` 디렉토리에 있으며, `layout/base.html`을 상속받습니다.

### 코드 스타일
- Python 코드는 PEP 8 스타일 가이드를 따릅니다.
- 템플릿 파일은 Jinja2 문법을 사용합니다.
- HTML은 Bootstrap 5를 사용합니다.

### 데이터베이스 접근
_bp.py 파일에
```python
from app.db import db
```
추가 후 함수 내부에서
```python
  conn = db.get_db()
  cursor = conn.cursor()
```
선언하여 사용

## 📋 다음 단계

### 높은 우선순위
1. 데이터베이스 연결 구현 (`app/models/database.py`)
2. 회원정보 조회 페이지 (`/member/profile`)
3. 태그 관리 페이지 (`/admin/tags`)
4. 메인 페이지 콘텐츠 목록 표시

### 중간 우선순위
5. DAO 계층 구현 (`app/models/*_dao.py`)
6. Service 계층 구현 (`app/services/*_service.py`)
7. 테마별 분류 기능 (영화/게임/도서)
8. 일반 사용자 콘텐츠 등록 기능

### 낮은 우선순위
9. 동시성 제어 구현 (트랜잭션, 잠금)
10. 유틸리티 함수 구현 (`app/utils/validators.py`)

자세한 구현 계획은 [`plans/mid_plan.md`](plans/mid_plan.md)를 참고하세요.

## 👥 팀 정보

- **팀명**: Team13
- **프로젝트**: Phase 4 - Flask 웹 애플리케이션

---

**마지막 업데이트**: 2025-11-29
