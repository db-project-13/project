# Team13-Phase3 콘솔 애플리케이션 분석 문서

## 📋 프로젝트 개요

**프로젝트명**: Team13-Phase3  
**유형**: 콘솔 기반 Java 애플리케이션  
**데이터베이스**: Oracle Database 21c  
**개발 환경**: Eclipse 25-09, Java 11 (Module System)  
**목적**: 리뷰 관리 시스템 (콘텐츠 리뷰 등록 및 조회, 회원 관리, 콘텐츠 관리)

---

## 🏗️ 아키텍처 구조

### 전체 구조
```
MainMenu (진입점)
├── DB 연결 관리 (Oracle JDBC)
├── 세션 관리 (currentUserId, isAdmin)
└── 메뉴 라우팅
    ├── MemberService (회원 관리)
    ├── ReviewService (리뷰 등록)
    ├── ContentTab (콘텐츠 관리 - 관리자 전용)
    └── QueryUI (쿼리 실행 및 조회)
        └── QueryDAO (데이터 접근 계층)
```

### 패키지 구조
```
phase3/
├── MainMenu.java          # 메인 진입점 및 메뉴 라우팅
├── MemberService.java     # 회원가입/회원정보 수정
├── ReviewService.java     # 리뷰 등록
├── ContentTab.java        # 콘텐츠 관리 (CRUD)
├── QueryUI.java           # 쿼리 메뉴 UI
├── QueryDAO.java          # 데이터 접근 객체 (10개 쿼리)
├── MemberDTO.java         # 회원 데이터 전송 객체
├── ContentDTO.java        # 콘텐츠 데이터 전송 객체
└── ReviewStatDTO.java     # 리뷰/통계 데이터 전송 객체
```

---

## 📦 주요 컴포넌트 분석

### 1. MainMenu.java
**역할**: 애플리케이션 진입점 및 중앙 제어

**주요 기능**:
- Oracle DB 연결 관리 (`connectToDatabase()`, `closeConnection()`)
- 세션 상태 관리 (`currentUserId`, `isAdmin`)
- 메인 메뉴 표시 및 라우팅
- 로그인/로그아웃 처리

**핵심 메서드**:
- `main(String[] args)`: 프로그램 진입점
- `handleLoginOrLogout()`: 로그인/로그아웃 처리
- `handleContentManagement()`: 관리자 권한 확인 후 콘텐츠 관리 호출
- `printMainMenu()`: 로그인 상태에 따른 동적 메뉴 표시

**DB 연결 정보**:
```java
DB_URL = "jdbc:oracle:thin:@localhost:1521:orcl"
USER = "university"
PASS = "comp322"
```

**세션 관리 방식**:
- `static String currentUserId`: 현재 로그인한 사용자 ID (null = 비로그인)
- `static boolean isAdmin`: 관리자 여부 (MEMBER 테이블의 IsAdmin 컬럼 기반)

---

### 2. MemberService.java
**역할**: 회원 관리 서비스

**주요 기능**:
- **회원가입** (`registerMember()`)
  - ID 중복 확인
  - 필수 필드: ID, Password, Name
  - 선택 필드: Address, Sex (M/F), Birthday (YYYY-MM-DD)
- **회원정보 수정** (`modifyMemberProfile()`)
  - 로그인 상태에서만 가능
  - 수정 가능 필드: Password, Address
  - 현재 정보 조회 후 변경사항만 업데이트

**데이터베이스 테이블**: `MEMBER`
- 컬럼: ID (PK), Password, Name, Address, Sex, Birthday, IsAdmin

**특징**:
- ID 중복 검사 (`isIdDuplicated()`)
- 날짜 형식 검증 (YYYY-MM-DD)
- Nullable 필드 처리

---

### 3. ReviewService.java
**역할**: 리뷰 등록 서비스

**주요 기능**:
- **리뷰 등록** (`registerReview()`)
  1. 콘텐츠 검색 (제목 LIKE 검색)
  2. 검색 결과가 1개면 자동 선택, 여러 개면 사용자 선택
  3. 평점 입력 (1-5)
  4. 코멘트 입력 (선택)
  5. DB에 INSERT

**데이터베이스 테이블**: `RATING`
- 컬럼: MID (FK → MEMBER.ID), CID (FK → CONTENT.ContentID), Rating, Comm, Likes
- 제약조건: (MID, CID) 복합 PK (중복 리뷰 방지)

**특징**:
- 콘텐츠 검색 기능 (`searchContentByTitle()`)
- 검색 결과 다중 선택 UI (`selectFromMultipleResults()`)
- 중복 리뷰 방지 (PK 제약조건)

---

### 4. ContentTab.java
**역할**: 콘텐츠 관리 (관리자 전용)

**주요 기능**:
- **제작사(PRODUCT_CO) 관리**
  - INSERT: 신규 제작사 등록
  - UPDATE: 제작사명/제작사 소개 수정
  - DELETE: 제작사 삭제 (참조하는 콘텐츠가 없을 때만)
- **콘텐츠(CONTENT) 관리**
  - INSERT: 신규 콘텐츠 등록 (제작사 ID 필수, 시리즈 ID 선택)
  - UPDATE: 제목/출시일/제작사 ID/시리즈 ID 수정
  - DELETE: 콘텐츠 삭제 (RATING, SHOP, TAG_TO 참조 확인)
- **시리즈(SERIES) 관리**
  - INSERT: 신규 시리즈 등록
  - UPDATE: 시리즈명 수정
  - DELETE: 시리즈 삭제 (참조하는 콘텐츠가 없을 때만)

**데이터베이스 테이블**:
- `PRODUCT_CO`: ProdcoID (PK), Prodname, ProdInfo
- `CONTENT`: ContentID (PK), Title, ReleaseDate, PID (FK), SID (FK, nullable)
- `SERIES`: SeriesID (PK), SName

**특징**:
- 외래키 참조 무결성 검사 (`checkPId()`, `checkSId()`, `isContentReferenced()`)
- 동적 UPDATE 쿼리 생성 (변경된 필드만 업데이트)
- ID 중복 검사

---

### 5. QueryDAO.java
**역할**: 데이터 접근 객체 (10개 선정 쿼리 실행)

**쿼리 목록**:

1. **Q 1-1**: 단일 테이블 쿼리 (Selection + Projection)
   - `selectMembersBySex(String sex)`: 특정 성별 회원 조회

2. **Q 1-2**: 단일 테이블 쿼리 (날짜 필터링)
   - `selectRecentContents(Date releaseDate)`: 특정 날짜 이후 출시 콘텐츠 조회

3. **Q 2-1**: Multi-way Join
   - `selectReviewsByProdco(String prodName)`: 제작사별 리뷰 조회

4. **Q 3-1**: Aggregation + Multi-way Join + GROUP BY
   - `aggregateRatingByTag()`: 태그별 평점 통계 (평균 평점, 총 리뷰 수)

5. **Q 4-2**: Subquery (Correlated Subquery)
   - `selectHighRatingReviews()`: 콘텐츠별 평균 평점보다 높은 리뷰 조회

6. **Q 6-1**: Selection + Projection + IN predicates
   - `selectShopByReleasePeriod(Date startDate, Date endDate)`: 기간 출시 콘텐츠의 SHOP 정보 조회

7. **Q 7-1**: In-line view를 활용한 Query
   - `selectHighRatedContentByProdco(String prodName, double minRating)`: 특정 제작사의 고평점 콘텐츠 목록

8. **Q 8-1**: Multi-way join with join predicates in WHERE + ORDER BY
   - `selectContentBySeriesSortedByDate(int seriesId)`: 시리즈별 콘텐츠 출시일 순 정렬

9. **Q 9-1**: Aggregation + Multi-way Join + GROUP BY + ORDER BY (Ranking)
   - `selectTop5Reviewers()`: 활동 우수 TOP 5 멤버 랭킹

10. **Q 9-2**: Aggregation + Multi-way Join + GROUP BY + ORDER BY (Ranking)
    - `selectProdcoRatingRanking()`: 제작사별 평균 평점 랭킹

**특징**:
- PreparedStatement 사용 (SQL Injection 방지)
- DTO 패턴으로 결과 매핑
- 리소스 관리 (`oraClose()` 메서드)

---

### 6. QueryUI.java
**역할**: 쿼리 실행 UI 및 결과 출력

**주요 기능**:
- 쿼리 메뉴 표시 (`printQueryList()`)
- 사용자 입력 받기 (날짜, 문자열, 숫자)
- 쿼리 실행 및 결과 포맷팅 출력
- 날짜 입력 검증 (`inputDate()`)

**특징**:
- 테이블 형식 결과 출력
- 날짜 형식 검증 (yyyy-MM-dd)
- 예외 처리 및 사용자 피드백

---

### 7. DTO 클래스들

#### MemberDTO.java
- 필드: id, password, name, address, sex, birthday
- 용도: 회원 정보 전송

#### ContentDTO.java
- 필드: contentId, title, releaseDate, pid, sid, prodname, sname, avgRating, reviewCount
- 용도: 콘텐츠 정보 전송 (조인 결과 포함)

#### ReviewStatDTO.java
- 필드: mid, cid, rating, comm, likes, memberName, contentTitle, groupName, avgRating, totalReviews, countValue
- 용도: 리뷰 및 통계 데이터 전송 (다양한 쿼리 결과를 담기 위해 유연한 구조)

---

## 🔐 인증 및 권한 관리

### 로그인 프로세스
1. 사용자 ID/PW 입력
2. `MEMBER` 테이블에서 조회
3. 일치 시 `currentUserId` 설정 및 `isAdmin` 플래그 설정
4. 로그아웃 시 두 변수 초기화

### 권한 체계
- **비로그인**: 회원가입, 쿼리 조회만 가능
- **일반 회원**: 로그인, 회원정보 수정, 리뷰 등록, 쿼리 조회
- **관리자**: 모든 기능 + 콘텐츠 관리 (제작사/콘텐츠/시리즈 CRUD)

---

## 💾 데이터베이스 스키마

### 주요 테이블

#### MEMBER
- `ID` (PK, VARCHAR)
- `Password` (VARCHAR)
- `Name` (VARCHAR)
- `Address` (VARCHAR, nullable)
- `Sex` (CHAR(1), nullable, 'M'/'F')
- `Birthday` (DATE, nullable)
- `IsAdmin` (CHAR(1), 'T'/'F')

#### CONTENT
- `ContentID` (PK, INTEGER)
- `Title` (VARCHAR)
- `ReleaseDate` (DATE)
- `PID` (FK → PRODUCT_CO.ProdcoID)
- `SID` (FK → SERIES.SeriesID, nullable)

#### RATING
- `MID` (FK → MEMBER.ID, 복합 PK)
- `CID` (FK → CONTENT.ContentID, 복합 PK)
- `Rating` (INTEGER, 1-5)
- `Comm` (VARCHAR, nullable)
- `Likes` (INTEGER, default 0)

#### PRODUCT_CO
- `ProdcoID` (PK, INTEGER)
- `Prodname` (VARCHAR)
- `ProdInfo` (VARCHAR, nullable)

#### SERIES
- `SeriesID` (PK, INTEGER)
- `SName` (VARCHAR)

#### 기타 테이블 (쿼리에서 사용)
- `TAG`: TagCode (PK), Tag
- `TAG_TO`: TCode (FK), CID (FK)
- `SHOP`: CID (FK), MainURL, SubURL

---

## 🎨 UI/UX 특징

### 콘솔 UI 패턴
- 메뉴 기반 네비게이션
- 상태 표시 (로그인 상태, 관리자 여부)
- 테이블 형식 결과 출력
- 입력 검증 및 에러 메시지
- 콘솔 클리어 (줄바꿈 50줄)

### 사용자 상호작용
- 숫자 입력: 메뉴 선택
- 문자열 입력: 검색어, 이름 등
- 날짜 입력: YYYY-MM-DD 형식
- 선택 입력: 여러 결과 중 선택

---

## 🔧 기술 스택 및 의존성

### Java 모듈 시스템
- `module-info.java`: `requires java.sql;`
- Java 11 이상

### 외부 라이브러리
- `ojdbc11.jar`: Oracle JDBC 드라이버
- `orai18n.jar`: 한글 인코딩 지원

### 환경 변수
- `NLS_LANG`: `AMERICAN_AMERICA.KO16KSC5601` (한글 변수 지원)

---

## 🚀 웹 애플리케이션 전환을 위한 고려사항

### 1. 아키텍처 개선

#### 현재 구조의 한계
- 모든 로직이 콘솔에 종속
- 세션 관리가 static 변수로만 처리
- UI와 비즈니스 로직이 혼재

#### 웹 전환 시 제안 구조
```
Frontend (React/Vue/Angular)
    ↓ HTTP/REST API
Backend (Spring Boot)
    ├── Controller Layer (REST API)
    ├── Service Layer (비즈니스 로직)
    ├── Repository Layer (DAO → JPA/MyBatis)
    └── Entity Layer (DTO → Entity)
        ↓ JDBC/JPA
Oracle Database
```

### 2. 세션 관리 개선

#### 현재 방식
```java
static String currentUserId = null;
static boolean isAdmin = false;
```

#### 웹 전환 시
- **세션 기반**: HttpSession 사용 (서버 측 세션)
- **토큰 기반**: JWT (JSON Web Token) 사용 (Stateless)
- **권장**: JWT + Refresh Token 방식

### 3. 데이터베이스 연결 관리

#### 현재 방식
```java
static Connection conn = null;
// 애플리케이션 시작 시 한 번 연결
```

#### 웹 전환 시
- **Connection Pool**: HikariCP, Apache DBCP
- **ORM**: JPA/Hibernate (Entity Manager)
- **트랜잭션 관리**: `@Transactional` 어노테이션

### 4. API 설계 제안

#### RESTful API 엔드포인트 예시

**인증**
- `POST /api/auth/login` - 로그인
- `POST /api/auth/logout` - 로그아웃
- `POST /api/auth/register` - 회원가입

**회원**
- `GET /api/members/me` - 현재 사용자 정보 조회
- `PUT /api/members/me` - 회원정보 수정

**리뷰**
- `POST /api/reviews` - 리뷰 등록
- `GET /api/reviews?contentId={id}` - 콘텐츠별 리뷰 조회
- `GET /api/reviews?memberId={id}` - 회원별 리뷰 조회

**콘텐츠 관리 (관리자)**
- `GET /api/admin/contents` - 콘텐츠 목록
- `POST /api/admin/contents` - 콘텐츠 등록
- `PUT /api/admin/contents/{id}` - 콘텐츠 수정
- `DELETE /api/admin/contents/{id}` - 콘텐츠 삭제
- `GET /api/admin/producers` - 제작사 목록
- `POST /api/admin/producers` - 제작사 등록
- `GET /api/admin/series` - 시리즈 목록
- `POST /api/admin/series` - 시리즈 등록

**쿼리**
- `GET /api/queries/members?sex={M|F}` - Q 1-1
- `GET /api/queries/contents?releaseDate={date}` - Q 1-2
- `GET /api/queries/reviews/producer?name={name}` - Q 2-1
- `GET /api/queries/stats/tags` - Q 3-1
- `GET /api/queries/reviews/high-rating` - Q 4-2
- `GET /api/queries/shops?startDate={date}&endDate={date}` - Q 6-1
- `GET /api/queries/contents/high-rated?producer={name}&minRating={rating}` - Q 7-1
- `GET /api/queries/contents/series/{seriesId}` - Q 8-1
- `GET /api/queries/members/top-reviewers` - Q 9-1
- `GET /api/queries/producers/ranking` - Q 9-2

### 5. 보안 강화

#### 현재 보안 이슈
- 비밀번호 평문 저장
- SQL Injection 방지는 되어 있음 (PreparedStatement)
- CSRF 방지 없음 (콘솔이므로 불필요)

#### 웹 전환 시 보안 개선
- **비밀번호 암호화**: BCrypt, Argon2
- **HTTPS**: SSL/TLS 인증서
- **CSRF 토큰**: Spring Security CSRF 보호
- **XSS 방지**: 입력값 검증 및 이스케이프
- **SQL Injection**: JPA 사용 시 자동 방지
- **Rate Limiting**: API 호출 제한

### 6. 프론트엔드 제안

#### 기술 스택 옵션
1. **React + TypeScript**
   - 컴포넌트 기반 UI
   - 상태 관리: Redux/Zustand
   - HTTP 클라이언트: Axios

2. **Vue.js + TypeScript**
   - 간단한 학습 곡선
   - 상태 관리: Pinia/Vuex

3. **Angular**
   - 엔터프라이즈급 프레임워크
   - TypeScript 기본

#### UI 컴포넌트 제안
- **로그인/회원가입 폼**: React Hook Form + Validation
- **리뷰 등록**: 콘텐츠 검색 자동완성 (Debounce)
- **콘텐츠 관리**: DataTable (정렬, 필터링, 페이지네이션)
- **쿼리 결과**: 차트 라이브러리 (Chart.js, Recharts) - 통계 쿼리용

### 7. 비동기 처리

#### 현재 방식
- 동기식 콘솔 입력/출력
- 블로킹 I/O

#### 웹 전환 시
- **비동기 API 호출**: Promise/async-await
- **실시간 업데이트**: WebSocket (리뷰 좋아요, 실시간 통계)
- **백그라운드 작업**: Spring @Async (대용량 쿼리)

### 8. 에러 처리 개선

#### 현재 방식
- try-catch로 콘솔에 에러 메시지 출력

#### 웹 전환 시
- **글로벌 예외 처리**: `@ControllerAdvice`
- **에러 응답 표준화**: ErrorResponse DTO
- **로깅**: Logback/SLF4J
- **모니터링**: Prometheus + Grafana

### 9. 테스트 전략

#### 현재 상태
- 테스트 코드 없음

#### 웹 전환 시
- **단위 테스트**: JUnit 5 + Mockito
- **통합 테스트**: Spring Boot Test + TestContainers (Oracle)
- **E2E 테스트**: Cypress/Playwright

### 10. 성능 최적화

#### 현재 이슈
- 매번 DB 연결 (단일 Connection)
- N+1 쿼리 문제 가능성

#### 웹 전환 시
- **Connection Pool**: 최적 크기 설정
- **캐싱**: Redis (인기 콘텐츠, 통계)
- **쿼리 최적화**: 인덱스 추가, EXPLAIN PLAN 분석
- **페이지네이션**: 대용량 데이터 처리

---

## 📝 마이그레이션 체크리스트

### Phase 1: 백엔드 API 구축
- [ ] Spring Boot 프로젝트 생성
- [ ] Oracle DB 연결 설정 (HikariCP)
- [ ] Entity 클래스 생성 (JPA)
- [ ] Repository 계층 구현
- [ ] Service 계층 구현 (기존 로직 이식)
- [ ] Controller 계층 구현 (REST API)
- [ ] 인증/인가 구현 (Spring Security + JWT)
- [ ] 예외 처리 및 로깅 설정

### Phase 2: 프론트엔드 구축
- [ ] React/Vue 프로젝트 생성
- [ ] 라우팅 설정
- [ ] 인증 페이지 (로그인/회원가입)
- [ ] 회원정보 수정 페이지
- [ ] 리뷰 등록 페이지 (콘텐츠 검색 포함)
- [ ] 콘텐츠 관리 페이지 (관리자)
- [ ] 쿼리 결과 페이지 (10개 쿼리)
- [ ] 공통 컴포넌트 (헤더, 사이드바, 테이블)

### Phase 3: 통합 및 테스트
- [ ] API 통합 테스트
- [ ] E2E 테스트
- [ ] 성능 테스트
- [ ] 보안 테스트

### Phase 4: 배포
- [ ] 프로덕션 환경 설정
- [ ] CI/CD 파이프라인 구축
- [ ] 모니터링 설정

---

## 🔍 코드 품질 개선 포인트

### 현재 코드의 장점
- ✅ PreparedStatement 사용 (SQL Injection 방지)
- ✅ DTO 패턴 사용
- ✅ 계층 분리 (Service, DAO)
- ✅ 입력 검증

### 개선 필요 사항
- ⚠️ 세션 관리가 static 변수로만 처리
- ⚠️ 에러 처리가 단순 (콘솔 출력만)
- ⚠️ 트랜잭션 관리 없음
- ⚠️ 로깅 시스템 없음
- ⚠️ 테스트 코드 없음
- ⚠️ 비밀번호 평문 저장

---

## 📚 참고 자료

### 기술 문서
- Oracle JDBC 드라이버 문서
- Java Module System 문서
- Spring Boot 공식 문서
- React/Vue 공식 문서

### 데이터베이스 스키마
- `MEMBER`, `CONTENT`, `RATING`, `PRODUCT_CO`, `SERIES`, `TAG`, `TAG_TO`, `SHOP` 테이블 구조

---

## 📌 결론

Team13-Phase3는 콘솔 기반의 리뷰 관리 시스템으로, 다음과 같은 특징을 가지고 있습니다:

1. **명확한 계층 구조**: MainMenu → Service → DAO → Database
2. **다양한 쿼리**: 10개의 선정된 쿼리로 다양한 데이터 조회
3. **권한 관리**: 일반 회원과 관리자 구분
4. **데이터 무결성**: 외래키 참조 검사 및 중복 방지

웹 애플리케이션으로 전환 시, 위의 고려사항을 참고하여 현대적인 웹 아키텍처로 재구성할 수 있습니다.

---

**작성일**: 2024년  
**목적**: 콘솔 애플리케이션 분석 및 웹 전환 가이드

