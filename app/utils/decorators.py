"""
데코레이터 유틸리티
"""
from functools import wraps
from flask import session, redirect, url_for, flash
from app.db import db

def login_required(f):
    """
    로그인 필요 데코레이터
    
    Args:
        f: 보호할 함수
    
    Returns:
        래핑된 함수
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('로그인이 필요합니다.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 1. 로그인 여부 확인
        user_id = session.get('user_id')
        if not user_id:
            flash('로그인이 필요합니다.', 'warning')
            return redirect(url_for('auth.login')) # auth.login은 팀원이 만들 경로

        # 2. DB에서 관리자 여부(IsAdmin) 확인
        conn = db.get_db()
        cursor = conn.cursor()
        
        try:
            sql = "SELECT IsAdmin FROM MEMBER WHERE ID = :mid"
            cursor.execute(sql, mid=user_id)
            result = cursor.fetchone()
            
            # 계정이 없거나, 관리자가 아니면('F') 거부
            if not result or result[0] != 'T':
                flash('관리자 권한이 필요합니다.', 'danger')
                return redirect(url_for('main.index')) # 메인 페이지로 튕김
                
        except Exception as e:
            flash(f'인증 확인 중 오류 발생: {str(e)}', 'danger')
            return redirect(url_for('main.index'))
        finally:
            cursor.close()
            
        return f(*args, **kwargs)
    return decorated_function

