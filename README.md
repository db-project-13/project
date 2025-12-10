# Team13-Phase4 Flask 웹 애플리케이션

Phase 3 콘솔 애플리케이션을 Flask 기반 웹 애플리케이션으로 전환한 프로젝트입니다.

## 📋 프로젝트 개요

- **프로젝트명**: Team13-Phase4
- **유형**: Flask 기반 웹 애플리케이션 (BE: Flask, FE: Jinja2/HTML/CSS/JS)
- **데이터베이스**: Oracle Database 21c
- **목표**: Phase 3의 필수 기능 탑재 및 트랜잭션을 활용한 사용자 동시성 제어를 지원하는 데이터베이스 웹 사이트 구축

## 🛠️ 제작 환경

### 기술 스택

- **Backend**: Flask 3.0.0 (Python)
- **Frontend**: Jinja2, Bootstrap 5, JavaScript
- **Database**: Oracle Database 21c
- **Database Driver**: oracledb 3.4.0
- **기타**: python-dotenv 1.0.0

### 시스템 요구사항

- Python 3.11 이상
- Oracle Database 19c 이상 (로컬 또는 Docker)
- Oracle Instant Client (oracledb 사용 시, 선택사항 - Thin 모드 사용 가능)

## 🚀 실행 방법

### 1. 프로젝트 클론 및 가상 환경 설정

```bash
# 가상 환경 생성
python -m venv venv

# 가상 환경 활성화
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정

프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 다음 내용을 작성하세요:

```bash
# Flask 환경 설정
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here-change-in-production

# 데이터베이스 연결 정보
DB_DSN=localhost:1521/orcl
DB_USER=your-db-username
DB_PASSWORD=your-db-password

# Connection Pool 설정 (선택사항)
DB_POOL_MIN=2
DB_POOL_MAX=10
```

**주의사항**:
- `.env` 파일은 Git에 커밋되지 않습니다 (`.gitignore`에 포함됨)
- 프로덕션 환경에서는 `SECRET_KEY`를 강력한 랜덤 문자열로 변경하세요
- `DB_DSN` 형식: `호스트:포트/서비스명` (예: `localhost:1521/orcl`)

### 4. 데이터베이스 초기화

데이터베이스 테이블 생성 및 초기 데이터 삽입을 위해 `init_db.py`를 실행합니다:

```bash
python app/init_db.py
```

이 스크립트는 다음 작업을 수행합니다:
1. `app/DBreset_table.sql` 실행 - 테이블 및 시퀀스 생성
2. `app/DBreset_insert.sql` 실행 - 초기 데이터 삽입

**실행 전 확인사항**:
- `.env` 파일에 올바른 데이터베이스 연결 정보가 설정되어 있어야 합니다
- 실행 시 확인 메시지가 표시되며, `y`를 입력해야 진행됩니다
- 기존 테이블이 있는 경우 데이터가 초기화될 수 있으므로 주의하세요

**init_db 실행 시 필요한 .env 설정**:
```bash
# 필수 항목
DB_USER=your-db-username          # 데이터베이스 사용자명
DB_PASSWORD=your-db-password      # 데이터베이스 비밀번호
DB_DSN=localhost:1521/orcl        # 데이터베이스 연결 문자열

# 선택 항목 (init_db에서는 사용하지 않지만, 애플리케이션 실행 시 필요)
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here
DB_POOL_MIN=2
DB_POOL_MAX=10
```

### 5. 애플리케이션 실행

```bash
python run.py
```

애플리케이션이 실행되면 다음 주소로 접속할 수 있습니다:
```
http://localhost:8000
```

## 🎯 주요 기능

### 인증 시스템
- **회원가입**: 새로운 사용자 등록
- **로그인/로그아웃**: 세션 기반 인증
- **세션 관리**: 24시간 세션 유지

### 회원 관리
- **회원정보 조회**: 마이페이지에서 본인 정보 확인
- **회원정보 수정**: 비밀번호, 주소, 성별, 생년월일 수정
- **작성한 리뷰 조회**: 본인이 작성한 모든 리뷰 목록 확인

### 콘텐츠 관리
- **메인 페이지**: 전체 콘텐츠 목록 표시 (페이지네이션 지원)
- **테마별 분류**: 영화, 게임, 도서별 콘텐츠 목록 조회
  - 영화: `/content/movies`
  - 게임: `/content/games`
  - 도서: `/content/books`
- **콘텐츠 검색**: 제목 및 태그 기반 검색
- **콘텐츠 상세**: 제목, 출시일, 제작사, 시리즈, 태그, 구매처, 리뷰 통계 등 상세 정보 표시

### 리뷰 시스템
- **리뷰 작성**: 콘텐츠에 대한 평점(1-5점) 및 코멘트 작성
- **리뷰 수정**: 본인이 작성한 리뷰 수정
- **리뷰 삭제**: 본인이 작성한 리뷰 삭제
- **좋아요 기능**: 다른 사용자의 리뷰에 좋아요 (동시성 제어 포함)
- **리뷰 통계**: 평균 평점, 평점 분포, 리뷰 수 표시

### 관리자 기능
- **대시보드**: 관리자 전용 메인 페이지
- **회원 관리**: 일반 회원 목록 조회 및 삭제
- **제작사 관리**: 제작사 추가/수정/삭제
- **콘텐츠 관리**: 콘텐츠 추가/수정/삭제, 태그 연결, 구매처 관리
- **시리즈 관리**: 시리즈 추가/수정/삭제
- **태그 관리**: 태그 추가/삭제, 카테고리별 관리

## ⚠️ 유의 사항

### 데이터베이스 연결
- Oracle Database에 대한 접근 권한이 필요합니다
- `DB_DSN` 형식이 올바른지 확인하세요: `호스트:포트/서비스명`
- 방화벽 설정으로 인해 데이터베이스 연결이 차단될 수 있습니다

### 보안
- 프로덕션 환경에서는 반드시 `SECRET_KEY`를 변경하세요
- `.env` 파일에 실제 비밀번호를 저장하므로 파일 권한을 적절히 설정하세요
- 데이터베이스 비밀번호는 강력한 비밀번호를 사용하세요

### 데이터베이스 초기화
- `init_db.py` 실행 시 기존 테이블과 데이터가 삭제될 수 있습니다
- 프로덕션 환경에서는 데이터베이스 백업을 먼저 수행하세요
- `init_db.py`는 개발/테스트 환경에서만 사용하세요

### 동시성 제어
- 리뷰 작성 시 동일 사용자의 중복 리뷰는 방지됩니다
- 좋아요 기능은 `SELECT ... FOR UPDATE`를 사용하여 동시성 제어가 구현되어 있습니다

### 세션 관리
- 기본 세션 유지 시간은 24시간입니다
- 브라우저를 닫아도 세션이 유지됩니다 (permanent session)

## 🏗️ 프로젝트 구조

```
project/
├── app/                          # Flask 애플리케이션 모듈
│   ├── __init__.py              # Flask 앱 팩토리
│   ├── config.py                # 설정 파일 (Development/Production)
│   ├── db.py                    # 데이터베이스 연결 관리
│   ├── init_db.py               # 데이터베이스 초기화 스크립트
│   ├── controllers/             # Blueprint 컨트롤러 (URL 라우팅)
│   │   ├── main_bp.py          # 메인 페이지
│   │   ├── auth_bp.py          # 인증 (로그인/로그아웃)
│   │   ├── member_bp.py        # 회원 관리
│   │   ├── content_bp.py       # 콘텐츠 및 리뷰
│   │   └── admin_bp.py         # 관리자 기능
│   ├── services/                # 비즈니스 로직 계층
│   │   ├── member_service.py   # 회원 서비스
│   │   ├── review_service.py   # 리뷰 서비스
│   │   └── content_service.py  # 콘텐츠 서비스
│   ├── models/                  # 데이터 접근 계층
│   │   ├── member_dao.py       # 회원 DAO
│   │   ├── review_dao.py       # 리뷰 DAO
│   │   └── content_dao.py     # 콘텐츠 DAO
│   ├── utils/                   # 유틸리티 함수
│   │   └── decorators.py       # @login_required, @admin_required
│   ├── templates/               # Jinja2 템플릿 (View 계층)
│   │   ├── layout/
│   │   │   └── base.html       # 공통 레이아웃
│   │   ├── main/               # 메인 페이지
│   │   ├── auth/               # 로그인/회원가입
│   │   ├── member/             # 회원 정보
│   │   ├── content/            # 콘텐츠 및 리뷰
│   │   └── admin/              # 관리자 기능
│   └── static/                  # 정적 파일 (CSS, JS)
│       ├── css/
│       └── js/
├── requirements.txt             # Python 의존성
├── run.py                       # 애플리케이션 진입점
└── README.md                    # 프로젝트 설명 (이 파일)
```

## 🔧 개발 가이드

### 데이터베이스 접근 방법

컨트롤러에서 데이터베이스 연결을 사용할 때:

```python
from app.db import db

conn = db.get_db()
cursor = conn.cursor()
# ... 쿼리 실행 ...
cursor.close()
```

트랜잭션이 필요한 경우:

```python
from app.db import db

with db.transaction() as conn:
    cursor = conn.cursor()
    # ... 쿼리 실행 ...
    cursor.close()
    # 자동으로 commit (예외 발생 시 rollback)
```

### 코드 스타일
- Python 코드는 PEP 8 스타일 가이드를 따릅니다
- 템플릿 파일은 Jinja2 문법을 사용합니다
- HTML은 Bootstrap 5를 사용합니다
