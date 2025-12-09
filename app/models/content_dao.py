# app/models/content_dao.py
# 콘텐츠 검색 관련 DAO 함수들
from typing import List, Dict, Any, Optional


def _row_to_content_dict(row, columns) -> Dict[str, Any]:
    """
    CONTENT 조회 결과 한 행(row)을 파이썬 dict로 변환
    """
    return dict(zip(columns, row))


def search_by_title(conn, search_term: str) -> List[Dict[str, Any]]:
    """
    콘텐츠 제목으로 검색 (LIKE 검색)
    
    Args:
        conn: Oracle DB 연결 객체
        search_term: 검색어 (콘텐츠 제목의 일부)
    
    Returns:
        검색된 콘텐츠 리스트
    """
    cursor = conn.cursor()
    
    sql = """
        SELECT c.ContentID, c.Title, 
               TO_CHAR(c.ReleaseDate, 'YYYY-MM-DD') as ReleaseDate,
               p.Prodname, s.SName,
               (SELECT ROUND(AVG(r.Rating), 1) FROM RATING r WHERE r.CID = c.ContentID) as AvgRating,
               (SELECT COUNT(*) FROM RATING r WHERE r.CID = c.ContentID) as ReviewCount
        FROM CONTENT c
        JOIN PRODUCT_CO p ON c.PID = p.ProdcoID
        LEFT JOIN SERIES s ON c.SID = s.SeriesID
        WHERE UPPER(c.Title) LIKE UPPER('%' || :search_term || '%')
        ORDER BY c.ReleaseDate DESC
    """
    
    cursor.execute(sql, {"search_term": search_term})
    columns = [col[0].lower() for col in cursor.description]
    cursor.rowfactory = lambda *args: dict(zip(columns, args))
    results = cursor.fetchall()
    cursor.close()
    
    return results


def search_by_tag(conn, tag: str) -> List[Dict[str, Any]]:
    """
    태그로 콘텐츠 검색 (부분 일치, 대소문자 구분 없음)
    
    Args:
        conn: Oracle DB 연결 객체
        tag: 태그명 (부분 일치 검색)
    
    Returns:
        검색된 콘텐츠 리스트
    """
    cursor = conn.cursor()
    
    sql = """
        SELECT DISTINCT c.ContentID, c.Title, 
               TO_CHAR(c.ReleaseDate, 'YYYY-MM-DD') as ReleaseDate,
               c.ReleaseDate as ReleaseDateRaw,
               p.Prodname, s.SName,
               (SELECT ROUND(AVG(r.Rating), 1) FROM RATING r WHERE r.CID = c.ContentID) as AvgRating,
               (SELECT COUNT(*) FROM RATING r WHERE r.CID = c.ContentID) as ReviewCount
        FROM CONTENT c
        JOIN PRODUCT_CO p ON c.PID = p.ProdcoID
        LEFT JOIN SERIES s ON c.SID = s.SeriesID
        JOIN TAG_TO tt ON c.ContentID = tt.CID
        JOIN TAG t ON tt.TCode = t.TagCode
        WHERE UPPER(t.Tag) LIKE UPPER('%' || :tag || '%')
        ORDER BY c.ReleaseDate DESC
    """
    
    cursor.execute(sql, {"tag": tag})
    columns = [col[0].lower() for col in cursor.description]
    cursor.rowfactory = lambda *args: dict(zip(columns, args))
    results = cursor.fetchall()
    cursor.close()
    
    return results


def search_by_title_and_tag(conn, search_term: str, tag: str) -> List[Dict[str, Any]]:
    """
    제목과 태그를 모두 사용한 검색
    
    Args:
        conn: Oracle DB 연결 객체
        search_term: 검색어 (콘텐츠 제목의 일부)
        tag: 태그명 (부분 일치 검색)
    
    Returns:
        검색된 콘텐츠 리스트
    """
    cursor = conn.cursor()
    
    sql = """
        SELECT DISTINCT c.ContentID, c.Title, 
               TO_CHAR(c.ReleaseDate, 'YYYY-MM-DD') as ReleaseDate,
               c.ReleaseDate as ReleaseDateRaw,
               p.Prodname, s.SName,
               (SELECT ROUND(AVG(r.Rating), 1) FROM RATING r WHERE r.CID = c.ContentID) as AvgRating,
               (SELECT COUNT(*) FROM RATING r WHERE r.CID = c.ContentID) as ReviewCount
        FROM CONTENT c
        JOIN PRODUCT_CO p ON c.PID = p.ProdcoID
        LEFT JOIN SERIES s ON c.SID = s.SeriesID
        JOIN TAG_TO tt ON c.ContentID = tt.CID
        JOIN TAG t ON tt.TCode = t.TagCode
        WHERE UPPER(c.Title) LIKE UPPER('%' || :search_term || '%')
          AND UPPER(t.Tag) LIKE UPPER('%' || :tag || '%')
        ORDER BY c.ReleaseDate DESC
    """
    
    cursor.execute(sql, {"search_term": search_term, "tag": tag})
    columns = [col[0].lower() for col in cursor.description]
    cursor.rowfactory = lambda *args: dict(zip(columns, args))
    results = cursor.fetchall()
    cursor.close()
    
    return results
