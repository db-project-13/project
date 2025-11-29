요청하신 대로, Phase 4 Flask 웹 애플리케이션 구현 계획 및 분석 문서를 **Markdown 파일(`.md`) 형식**으로 정리하여 제공합니다. 이 내용은 바로 복사하여 `team13-phase4-plan.md` 등의 파일로 저장하여 사용하시면 됩니다.

```markdown
# Team13-Phase4 Flask 웹 애플리케이션 구현 계획 및 분석 문서

## 📋 프로젝트 개요

* **프로젝트명**: Team13-Phase4 (MetaKritic 또는 ContentSphere)
* **유형**: Flask 기반 통합 웹 애플리케이션 (BE: Flask, FE: Jinja2/HTML/CSS/JS)
* **데이터베이스**: Oracle Database 21c (로컬 구동)
* **목표**: Phase 3의 필수 기능 탑재 및 **트랜잭션을 활용한 사용자 동시성 제어**를 지원하는 데이터베이스 웹 사이트 구축 및 서비스.
* **개발 환경**: Python 3.x, Flask, `cx_Oracle` (또는 `python-oracledb`), Jinja2.

---

## 🏗️ 아키텍처 및 폴더 구조 (Flask 통합 MVC 패턴)

Flask의 **Blueprint**를 사용하여 기능별 라우팅을 모듈화하고, **Service-DAO/Model** 계층 분리를 유지하여 Phase 3의 비즈니스 로직을 이식합니다. 

[Image of Flask application folder structure]


### 📁 폴더 구조

```

/team13-phase4 (프로젝트 Root - Git Repository)
├── /app                             \# Flask 애플리케이션 모듈 (BE + FE View)
│   ├── **init**.py                  \# Flask 앱 인스턴스 생성, 설정 로드 및 Blueprint 등록
│   ├── /static                      \# 🖼️ 정적 파일 (CSS, JS, 이미지)
│   ├── /templates                   \# 🖥️ Jinja2 템플릿 파일 (View 계층)
│   │   ├── /layout
│   │   │   └── base.html            \# 공통 레이아웃 (헤더, 푸터, 네비게이션)
│   │   ├── /auth                    \# 로그인, 회원가입 폼
│   │   ├── /member                  \# 회원 정보 조회/수정 폼
│   │   ├── /content                 \# 콘텐츠 목록, 세부, 리뷰 등록 폼
│   │   ├── /admin                   \# 관리자 전용 CRUD 페이지
│   │   └── /query                   \# 10개 선정 쿼리 결과 페이지
│   ├── /controllers                 \# 🌐 Flask Blueprint (Controller 계층 - URL 라우팅)
│   │   ├── auth\_bp.py               \# 인증 (로그인, 회원가입, 로그아웃) 라우트
│   │   ├── member\_bp.py             \# 회원 정보 조회/수정 라우트
│   │   ├── content\_bp.py            \# 콘텐츠/리뷰 관련 라우트
│   │   └── admin\_bp.py              \# 관리자 전용 CRUD 및 쿼리 실행 라우트
│   ├── /services                    \# ⚙️ 비즈니스 로직 (Service 계층 - Phase 3 로직 이식)
│   │   ├── member\_service.py        \# 회원가입/정보 수정
│   │   ├── review\_service.py        \# 리뷰 등록 및 콘텐츠 검색
│   │   └── admin\_service.py         \# 콘텐츠/제작사/시리즈 관리
│   ├── /models                      \# 💾 데이터 접근 객체 (DAO 계층 - Phase 3 DAO 해당)
│   │   ├── database.py              \# Oracle DB 연결 풀(`cx_Oracle`), 트랜잭션 관리
│   │   ├── member\_dao.py
│   │   ├── content\_dao.py
│   │   └── query\_dao.py             \# 10개 선정 쿼리 실행
│   ├── /utils                       \# 유틸리티 함수 (입력값/날짜 형식 검증)
│   └── app.py                       \# 메인 실행 파일 (WSGI Entry Point)
├── venv                             \# Python 가상 환경
└── requirements.txt                 \# Python 의존성 목록

```

---

## 📦 주요 컴포넌트 목적 및 Phase 3 매핑

| 파일/모듈 | 목적 | Phase 3 매핑 | 핵심 기능 |
| :--- | :--- | :--- | :--- |
| `database.py` | Oracle DB 연결 풀 초기화 및 트랜잭션 경계 설정 (커밋/롤백). | Oracle JDBC 연결 관리 | **동시성 제어** (트랜잭션) 구현 |
| `/models/*_dao.py` | SQL 쿼리 실행 및 결과 매핑 (Data Access Layer). | `QueryDAO.java` 및 기타 DB 작업 | DB 조작(삽입/삭제/변경/검색) 기능 |
| `/services/*_service.py` | 비즈니스 로직 및 규칙 구현. | `MemberService.java`, `ReviewService.java`, `ContentTab.java` | ID 중복 확인, 외래키 참조 무결성 검사 |
| `/controllers/*_bp.py` | URL 라우팅 및 요청/응답 처리 (Controller Layer). | `MainMenu.java`의 메뉴 라우팅 | 로그인 세션 관리 및 권한 확인 |
| `/templates/*/*.html` | 최종 사용자 인터페이스 (View Layer). | 콘솔 UI 출력 대체 | **Phase 3의 모든 기능에 대한 웹 UI** |

---

## 🔐 인증 및 권한 관리

| 기능 | URL 경로 (Route) | 필요 권한 | Phase 3 로직 기반 |
| :--- | :--- | :--- | :--- |
| 메인 페이지 | `/` | 모든 사용자 | 로그인 상태에 따른 동적 메뉴 표시 |
| 로그인 | `/login` | 비로그인 | `MEMBER` 테이블 조회 및 `currentUserId` 설정 |
| 회원가입 | `/register` | 비로그인 | ID 중복 확인 및 필수 필드 검증 |
| 리뷰 등록 | `/contents/<int:content_id>/review` | 일반 회원 이상 (로그인) | 콘텐츠 검색, 평점/코멘트 입력, 중복 리뷰 방지 |
| 회원 정보 수정 | `/profile/edit` | 일반 회원 이상 (로그인) | 비밀번호, 주소 등 수정 가능 필드 업데이트 |
| 관리자 기능 | `/admin/*` | 관리자 (`isAdmin=T`) | 콘텐츠, 제작사, 시리즈 CRUD |

---

## 💾 동시성 제어 및 트랜잭션 구현 (20 pts)

* **요구 사항**: 여러 사용자가 동시에 접속할 수 있도록 트랜잭션을 활용한 동시성 제어를 지원해야 합니다.
* **해결 방법**:
    1.  **Connection Pool 활용**: `cx_Oracle`을 사용하여 DB Connection Pool을 구성하고, 모든 요청은 풀에서 연결을 얻어와 사용합니다.
    2.  **Service 계층 트랜잭션**: `review_service.py` 등 데이터 무결성이 중요한 서비스 메서드에서 **명시적 트랜잭션**을 시작합니다.
    3.  **잠금 메커니즘**: 동시 업데이트 가능성이 있는 작업(예: 리뷰 좋아요 증가)에는 필요에 따라 **비관적 잠금** (`SELECT FOR UPDATE`)을 적용하거나, 데이터 일관성 오류 방지를 위한 적절한 트랜잭션 격리 수준을 설정합니다.
* **제출**: 해결 방안은 `TeamX-Additional_task1.txt`에 기술합니다.

---

## 🧑‍💻 3인 팀 협업 전략 (기능별 분담)

Flask 통합 구조를 채택하여, 팀원 3명이 모두 백엔드(Python/Flask)와 프론트엔드(Jinja2) 작업을 담당하되, 아래와 같이 **기능 단위**로 담당 구역을 나누어 병렬로 작업합니다.

| 팀원 | 담당 기능 | 주요 작업 영역 |
| :--- | :--- | :--- |
| **팀원 1** | 인증 및 회원 관리 | `auth_bp.py`, `member_bp.py`, `member_service.py`, `/templates/auth`, `/templates/member` |
| **팀원 2** | 콘텐츠 및 리뷰 관리 | `content_bp.py`, `review_service.py`, `/templates/content` |
| **팀원 3** | 관리자 기능 및 10개 쿼리 | `admin_bp.py`, `admin_service.py`, `query_dao.py`, `/templates/admin`, `/templates/query` |

* **코드 관리**: Github Repository 사용은 필수이며, 커밋 로그를 통해 활용도를 평가받습니다.

---

## 📝 마이그레이션 체크리스트

1.  [ ] Flask 프로젝트 초기 설정 및 `requirements.txt` 작성.
2.  [ ] **`database.py` 구현** (Connection Pool 및 트랜잭션 설정).
3.  [ ] `/templates/layout/base.html` (공통 레이아웃) 구성.
4.  [ ] `/models` 및 `/services` 계층에 Phase 3의 비즈니스/DAO 로직 이식.
5.  [ ] `/controllers` 계층에 Blueprint를 사용하여 라우팅 분리.
6.  [ ] **로그인/로그아웃/회원가입** 기능 웹 구현 완료.
7.  [ ] **리뷰 등록 및 콘텐츠 검색** 기능 웹 구현 완료.
8.  [ ] **관리자 CRUD 및 10개 쿼리** 기능 웹 구현 완료.
9.  [ ] **동시성 제어 로직** 구현 및 테스트.
10. [ ] `TeamX-Phase4.zip` 및 보고서 파일 (`TeamX-task1.txt`, `TeamX-Additional_task1.txt`) 준비.
```