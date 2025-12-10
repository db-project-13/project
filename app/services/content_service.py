# app/services/content_service.py
# 콘텐츠 검색 관련 Service 함수들
from typing import List, Dict, Any, Optional
from app.db import db
from app.models import content_dao


def search_content(search_term: Optional[str] = None, tag: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    콘텐츠 검색 서비스
    
    Args:
        search_term: 검색어 (콘텐츠 제목의 일부, 선택사항)
        tag: 태그명 (선택사항)
    
    Returns:
        검색된 콘텐츠 리스트
    
    검색 로직:
    - search_term만 있으면: 제목 검색
    - tag만 있으면: 태그 검색
    - 둘 다 있으면: 제목 + 태그 검색
    - 둘 다 없으면: 빈 리스트 반환
    """
    conn = db.get_db()
    if conn is None:
        return []
    
    # 둘 다 없으면 빈 리스트 반환
    if not search_term and not tag:
        return []
    
    # 검색어와 태그 전처리 (공백 제거)
    search_term = search_term.strip() if search_term else None
    tag = tag.strip() if tag else None
    
    # 둘 다 비어있으면 빈 리스트 반환
    if not search_term and not tag:
        return []
    
    try:
        if search_term and tag:
            # 제목 + 태그 검색
            return content_dao.search_by_title_and_tag(conn, search_term, tag)
        elif tag:
            # 태그만 검색
            return content_dao.search_by_tag(conn, tag)
        else:
            # 제목만 검색
            return content_dao.search_by_title(conn, search_term)
    except Exception as e:
        # 에러 발생 시 빈 리스트 반환
        print(f"검색 중 오류 발생: {str(e)}")
        return []
