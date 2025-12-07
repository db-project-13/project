# 콘텐츠 표시 및 리뷰 기능 구현 문서

**작성일**: 2025-01-XX  
**브랜치**: `feature/content-display`  
**작성자**: tldnr1

---

## 📋 구현 개요

이 문서는 `feature/content-display` 브랜치에서 구현한 콘텐츠 표시 및 리뷰 관리 기능에 대한 설명과 테스트 가이드를 포함합니다.

### 구현 목표
1. 메인 페이지에 전체 콘텐츠 목록 표시
2. 테마별(영화/게임/도서) 콘텐츠 목록 페이지 구현
3. 콘텐츠 상세 페이지 구현 (기본 정보, 태그, 구매처, 리뷰 통계)
4. 리뷰 CRUD 기능 구현 (등록/수정/삭제)

---

## 🎯 구현된 기능

### 1. 메인 페이지 (`/`)

#### 기능 설명
- 전체 콘텐츠 목록을 카드 형태로 표시
- 테마별 통계 표시 (영화/게임/도서 개수)
- 페이지네이션 지원 (20개씩)

#### 표시 정보
- 콘텐츠 제목
- 출시일
- 제작사명
- 시리즈명 (있는 경우)
- 미디어 타입 태그
- 평균 평점 및 리뷰 수

#### 구현 파일
- `app/controllers/main_bp.py` - 메인 페이지 라우팅 및 DB 조회 로직
- `app/templates/main/index.html` - 메인 페이지 템플릿

---

### 2. 테마별 콘텐츠 목록 페이지

#### 라우팅
- `/content/movies` - 영화 목록
- `/content/games` - 게임 목록
- `/content/books` - 도서 목록

#### 기능 설명
- MediaType 태그를 기준으로 콘텐츠 필터링
- 페이지네이션 지원
- 각 콘텐츠 카드에서 상세 페이지로 이동 가능

#### 구현 파일
- `app/controllers/content_bp.py` - 테마별 라우팅 및 `_get_contents_by_theme()` 헬퍼 함수
- `app/templates/content/theme_list.html` - 테마별 목록 공통 템플릿

---

### 3. 콘텐츠 상세 페이지 (`/content/<int:content_id>`)

#### 기능 설명
콘텐츠의 상세 정보를 종합적으로 표시하는 페이지입니다.

#### 표시 정보

**1. 기본 정보**
- 제목
- 출시일
- 제작사명 및 제작사 정보
- 시리즈명 (있는 경우)

**2. 태그 정보**
- 카테고리별 태그 그룹화 표시
  - MediaType (영화/게임/도서 등)
  - Genres (장르)
  - Language (언어)
  - Subtitle (자막)
  - Rate (등급)

**3. 구매처 정보**
- 구매 링크 목록 (외부 링크로 새 창 열기)

**4. 리뷰 통계**
- 평균 평점
- 총 리뷰 수
- 평점별 분포 그래프 (5점~1점)

**5. 리뷰 목록**
- 작성자명
- 평점 (별점 표시)
- 코멘트
- 좋아요 수
- 정렬: 좋아요 수 > 평점 순

#### 구현 파일
- `app/controllers/content_bp.py` - `detail()` 함수
- `app/templates/content/detail.html` - 상세 페이지 템플릿

---

### 4. 리뷰 관리 기능

#### 4.1 리뷰 등록 (`/content/<int:content_id>/review`)

**기능 설명**
- 로그인한 사용자가 콘텐츠에 리뷰를 작성할 수 있습니다.
- 한 사용자는 한 콘텐츠당 하나의 리뷰만 작성 가능합니다.
- 평점(1-5)과 코멘트(선택사항)를 입력할 수 있습니다.

**제약사항**
- 로그인 필수 (`@login_required` 데코레이터)
- 중복 리뷰 방지 (이미 작성한 경우 수정 기능 안내)

**구현 파일**
- `app/controllers/content_bp.py` - `create_review()` 함수
- `app/templates/content/review_form.html` - 리뷰 등록 폼

---

#### 4.2 리뷰 수정 (`/content/<int:content_id>/review/edit`)

**기능 설명**
- 사용자가 자신이 작성한 리뷰를 수정할 수 있습니다.
- 기존 평점과 코멘트가 폼에 미리 채워져 있습니다.

**제약사항**
- 로그인 필수
- 본인이 작성한 리뷰만 수정 가능

**구현 파일**
- `app/controllers/content_bp.py` - `update_review()` 함수
- `app/templates/content/review_form.html` - 리뷰 수정 폼 (동일 템플릿 사용)

---

#### 4.3 리뷰 삭제 (`/content/<int:content_id>/review/delete`)

**기능 설명**
- 사용자가 자신이 작성한 리뷰를 삭제할 수 있습니다.
- 삭제 전 확인 다이얼로그가 표시됩니다.

**제약사항**
- 로그인 필수
- 본인이 작성한 리뷰만 삭제 가능
- POST 메서드만 허용

**구현 파일**
- `app/controllers/content_bp.py` - `delete_review()` 함수

---

### 5. 네비게이션 바 업데이트

#### 추가된 링크
- 영화 (`/content/movies`)
- 게임 (`/content/games`)
- 도서 (`/content/books`)

#### 구현 파일
- `app/templates/layout/base.html` - 네비게이션 바 수정

---

## 📁 수정/생성된 파일 목록

### 수정된 파일
1. `app/controllers/content_bp.py`
   - 콘텐츠 상세 페이지 DB 조회 로직 추가
   - 리뷰 CRUD 라우팅 추가
   - 테마별 페이지 라우팅 추가

2. `app/controllers/main_bp.py`
   - 메인 페이지 DB 조회 로직 추가
   - 테마별 통계 조회 추가

3. `app/templates/content/detail.html`
   - 콘텐츠 상세 정보 표시 개선
   - 리뷰 통계 섹션 추가
   - 리뷰 목록 및 수정/삭제 버튼 추가

4. `app/templates/content/review_form.html`
   - 리뷰 등록/수정 폼 통합
   - action 파라미터로 모드 구분

5. `app/templates/main/index.html`
   - 콘텐츠 목록 카드 표시
   - 테마별 통계 및 링크 추가

6. `app/templates/layout/base.html`
   - 네비게이션 바에 테마별 링크 추가

### 새로 생성된 파일
1. `app/templates/content/theme_list.html`
   - 테마별 콘텐츠 목록 공통 템플릿

---

## 🗄️ 데이터베이스 쿼리

### 주요 SQL 쿼리

#### 1. 메인 페이지 - 전체 콘텐츠 목록
```sql
SELECT c.ContentID, c.Title, 
       TO_CHAR(c.ReleaseDate, 'YYYY-MM-DD') as ReleaseDate,
       p.Prodname, s.SName,
       (SELECT LISTAGG(t.Tag, ', ') WITHIN GROUP (ORDER BY t.Tag)
        FROM TAG_TO tt JOIN TAG t ON tt.TCode = t.TagCode
        WHERE tt.CID = c.ContentID AND t.Category = 'MediaType') as MediaType,
       (SELECT ROUND(AVG(r.Rating), 1) FROM RATING r WHERE r.CID = c.ContentID) as AvgRating,
       (SELECT COUNT(*) FROM RATING r WHERE r.CID = c.ContentID) as ReviewCount
FROM CONTENT c
JOIN PRODUCT_CO p ON c.PID = p.ProdcoID
LEFT JOIN SERIES s ON c.SID = s.SeriesID
ORDER BY c.ReleaseDate DESC
```

#### 2. 테마별 콘텐츠 목록
```sql
SELECT c.ContentID, c.Title, 
       TO_CHAR(c.ReleaseDate, 'YYYY-MM-DD') as ReleaseDate,
       p.Prodname, s.SName,
       (SELECT ROUND(AVG(r.Rating), 1) FROM RATING r WHERE r.CID = c.ContentID) as AvgRating,
       (SELECT COUNT(*) FROM RATING r WHERE r.CID = c.ContentID) as ReviewCount
FROM CONTENT c
JOIN PRODUCT_CO p ON c.PID = p.ProdcoID
LEFT JOIN SERIES s ON c.SID = s.SeriesID
JOIN TAG_TO tt ON c.ContentID = tt.CID
JOIN TAG t ON tt.TCode = t.TagCode
WHERE t.Category = 'MediaType' AND t.Tag = :theme
ORDER BY c.ReleaseDate DESC
```

#### 3. 콘텐츠 상세 정보
```sql
-- 기본 정보
SELECT c.ContentID, c.Title, 
       TO_CHAR(c.ReleaseDate, 'YYYY-MM-DD') as ReleaseDate,
       p.ProdcoID, p.Prodname, p.ProdInfo,
       s.SeriesID, s.SName
FROM CONTENT c
JOIN PRODUCT_CO p ON c.PID = p.ProdcoID
LEFT JOIN SERIES s ON c.SID = s.SeriesID
WHERE c.ContentID = :cid

-- 태그 정보 (카테고리별)
SELECT t.Category, LISTAGG(t.Tag, ', ') WITHIN GROUP (ORDER BY t.Tag) as Tags
FROM TAG t
JOIN TAG_TO tt ON t.TagCode = tt.TCode
WHERE tt.CID = :cid
GROUP BY t.Category

-- 구매처 정보
SELECT MainURL, SubURL FROM SHOP WHERE CID = :cid ORDER BY MainURL

-- 리뷰 통계
SELECT ROUND(AVG(Rating), 1) as AvgRating, 
       COUNT(*) as ReviewCount,
       COUNT(CASE WHEN Rating = 5 THEN 1 END) as Rating5,
       COUNT(CASE WHEN Rating = 4 THEN 1 END) as Rating4,
       COUNT(CASE WHEN Rating = 3 THEN 1 END) as Rating3,
       COUNT(CASE WHEN Rating = 2 THEN 1 END) as Rating2,
       COUNT(CASE WHEN Rating = 1 THEN 1 END) as Rating1
FROM RATING WHERE CID = :cid

-- 리뷰 목록
SELECT r.Rating, r.Comm, r.Likes, 
       m.Name as MemberName, m.ID as MemberID
FROM RATING r
JOIN MEMBER m ON r.MID = m.ID
WHERE r.CID = :cid
ORDER BY r.Likes DESC NULLS LAST, r.Rating DESC, m.ID
```

#### 4. 리뷰 등록
```sql
INSERT INTO RATING (MID, CID, Rating, Comm, Likes)
VALUES (:mid, :cid, :rating, :comm, 0)
```

#### 5. 리뷰 수정
```sql
UPDATE RATING 
SET Rating = :rating, Comm = :comm
WHERE MID = :mid AND CID = :cid
```

#### 6. 리뷰 삭제
```sql
DELETE FROM RATING WHERE MID = :mid AND CID = :cid
```

---

## 🚀 실행 방법

### 1. 사전 요구사항 확인

```bash
# Python 버전 확인 (3.11 이상)
python --version

# 가상 환경 활성화 (Windows)
venv\Scripts\activate

# 의존성 설치 확인
pip list | grep -i flask
pip list | grep -i oracledb
```

### 2. 데이터베이스 초기화

```bash
# DB 초기화 스크립트 실행
python app\init_db.py
```

**주의**: 이 스크립트는 기존 데이터를 삭제하고 새로 생성합니다.  
실행 전 확인 메시지에 `y`를 입력해야 합니다.

### 3. 환경 변수 설정

`.env` 파일이 있는지 확인하고, 없으면 `.env.sample`을 참고하여 생성하세요.

```bash
# .env 파일 예시
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here
DB_DSN=localhost:1521/orcl
DB_USER=your-db-username
DB_PASSWORD=your-db-password
DB_POOL_MIN=2
DB_POOL_MAX=10
```

### 4. 애플리케이션 실행

```bash
# Flask 앱 실행
python run.py
```

서버가 시작되면 다음 주소로 접속할 수 있습니다:
```
http://localhost:8000
```

---

## ✅ 확인 방법

### 1. 메인 페이지 확인

**접속**: `http://localhost:8000/`

**확인 사항**:
- [ ] 전체 콘텐츠 목록이 카드 형태로 표시되는가?
- [ ] 테마별 통계(영화/게임/도서 개수)가 표시되는가?
- [ ] 각 콘텐츠 카드에 제목, 출시일, 제작사, 평점이 표시되는가?
- [ ] 페이지네이션이 정상 작동하는가? (20개 이상일 경우)
- [ ] "상세보기" 버튼을 클릭하면 상세 페이지로 이동하는가?

---

### 2. 테마별 페이지 확인

**접속**:
- 영화: `http://localhost:8000/content/movies`
- 게임: `http://localhost:8000/content/games`
- 도서: `http://localhost:8000/content/books`

**확인 사항**:
- [ ] 해당 테마의 콘텐츠만 필터링되어 표시되는가?
- [ ] 네비게이션 바의 테마 링크가 정상 작동하는가?
- [ ] 페이지네이션이 정상 작동하는가?

---

### 3. 콘텐츠 상세 페이지 확인

**접속**: `http://localhost:8000/content/<content_id>`  
(예: `http://localhost:8000/content/301`)

**확인 사항**:

**기본 정보**:
- [ ] 제목, 출시일, 제작사, 시리즈가 표시되는가?
- [ ] 제작사 정보가 표시되는가? (있는 경우)

**태그 정보**:
- [ ] 카테고리별로 태그가 그룹화되어 표시되는가?
- [ ] MediaType, Genres, Language 등이 표시되는가?

**구매처 정보**:
- [ ] 구매 링크가 표시되는가? (있는 경우)
- [ ] 링크를 클릭하면 새 창에서 열리는가?

**리뷰 통계**:
- [ ] 평균 평점이 표시되는가?
- [ ] 총 리뷰 수가 표시되는가?
- [ ] 평점별 분포 그래프가 표시되는가? (리뷰가 있는 경우)

**리뷰 목록**:
- [ ] 리뷰 목록이 표시되는가?
- [ ] 작성자명, 평점(별점), 코멘트, 좋아요 수가 표시되는가?
- [ ] 리뷰가 없는 경우 "아직 등록된 리뷰가 없습니다" 메시지가 표시되는가?

---

### 4. 리뷰 등록 기능 확인

**접속**: `http://localhost:8000/content/<content_id>/review`

**확인 사항**:
- [ ] 로그인하지 않은 경우 로그인 페이지로 리다이렉트되는가?
- [ ] 로그인한 경우 리뷰 등록 폼이 표시되는가?
- [ ] 평점 선택 드롭다운이 정상 작동하는가?
- [ ] 코멘트 입력란에 텍스트를 입력할 수 있는가?
- [ ] "등록하기" 버튼을 클릭하면 리뷰가 등록되는가?
- [ ] 등록 후 상세 페이지로 리다이렉트되고 리뷰가 표시되는가?
- [ ] 이미 리뷰를 작성한 경우 중복 등록이 방지되는가?

**테스트 시나리오**:
1. 로그인하지 않은 상태에서 리뷰 작성 버튼 클릭 → 로그인 페이지로 이동
2. 로그인 후 리뷰 작성 → 정상 등록 확인
3. 같은 콘텐츠에 다시 리뷰 작성 시도 → "이미 리뷰를 작성하셨습니다" 메시지 표시

---

### 5. 리뷰 수정 기능 확인

**접속**: `http://localhost:8000/content/<content_id>/review/edit`

**확인 사항**:
- [ ] 본인이 작성한 리뷰의 경우 "리뷰 수정" 버튼이 표시되는가?
- [ ] 수정 폼에 기존 평점과 코멘트가 미리 채워져 있는가?
- [ ] 평점과 코멘트를 수정할 수 있는가?
- [ ] "수정하기" 버튼을 클릭하면 리뷰가 수정되는가?
- [ ] 수정 후 상세 페이지로 리다이렉트되고 수정된 내용이 표시되는가?
- [ ] 타인이 작성한 리뷰에는 수정 버튼이 표시되지 않는가?

**테스트 시나리오**:
1. 본인 리뷰의 "수정" 버튼 클릭 → 수정 폼 표시
2. 평점과 코멘트 수정 후 제출 → 수정 확인
3. 타인 리뷰에는 수정 버튼이 없는지 확인

---

### 6. 리뷰 삭제 기능 확인

**확인 사항**:
- [ ] 본인이 작성한 리뷰의 경우 "리뷰 삭제" 버튼이 표시되는가?
- [ ] 삭제 버튼 클릭 시 확인 다이얼로그가 표시되는가?
- [ ] 확인 후 삭제가 정상적으로 수행되는가?
- [ ] 삭제 후 상세 페이지로 리다이렉트되고 리뷰가 목록에서 사라지는가?
- [ ] 타인이 작성한 리뷰에는 삭제 버튼이 표시되지 않는가?

**테스트 시나리오**:
1. 본인 리뷰의 "삭제" 버튼 클릭 → 확인 다이얼로그 표시
2. 확인 클릭 → 리뷰 삭제 확인
3. 취소 클릭 → 삭제 취소 확인
4. 타인 리뷰에는 삭제 버튼이 없는지 확인

---

### 7. 네비게이션 바 확인

**확인 사항**:
- [ ] 네비게이션 바에 "영화", "게임", "도서" 링크가 추가되어 있는가?
- [ ] 각 링크를 클릭하면 해당 테마 페이지로 이동하는가?
- [ ] "홈", "콘텐츠 검색" 링크도 정상 작동하는가?

---

## 🐛 문제 해결

### 데이터베이스 연결 오류

**증상**: "DB Pool creation failed" 또는 연결 오류 메시지

**해결 방법**:
1. `.env` 파일의 DB 설정 확인
2. Oracle DB 서버가 실행 중인지 확인
3. DSN, 사용자명, 비밀번호가 올바른지 확인

```bash
# DB 연결 테스트
python -c "import oracledb; conn = oracledb.connect(user='your_user', password='your_pass', dsn='your_dsn'); print('연결 성공')"
```

---

### 리뷰가 표시되지 않음

**증상**: 리뷰를 등록했지만 목록에 표시되지 않음

**해결 방법**:
1. DB에 실제로 저장되었는지 확인
```sql
SELECT * FROM RATING WHERE CID = <content_id>;
```
2. 브라우저 캐시 삭제 후 새로고침
3. 서버 로그에서 에러 메시지 확인

---

### 페이지네이션 오류

**증상**: 페이지네이션이 작동하지 않거나 오류 발생

**해결 방법**:
1. URL 파라미터 확인 (`?page=2`)
2. 총 데이터 개수 확인
3. 서버 로그에서 에러 메시지 확인

---

## 📝 추가 개선 사항

### 향후 개선 가능한 기능

1. **리뷰 좋아요 기능**
   - 현재 Likes 컬럼은 있지만 UI에서 증가시키는 기능 없음
   - 좋아요 버튼 추가 가능

2. **리뷰 검색/필터링**
   - 평점별 필터링
   - 키워드 검색

3. **콘텐츠 이미지**
   - 썸네일 이미지 추가
   - 이미지 업로드 기능

4. **성능 최적화**
   - 쿼리 최적화 (인덱스 활용)
   - 캐싱 적용

---

## 📚 참고 자료

- [Flask 공식 문서](https://flask.palletsprojects.com/)
- [Oracle Database 문서](https://docs.oracle.com/en/database/)
- [Bootstrap 5 문서](https://getbootstrap.com/docs/5.3/)

---

**마지막 업데이트**: 2025-01-XX

