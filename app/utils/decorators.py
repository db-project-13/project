"""
데코레이터 유틸리티
"""
from functools import wraps
from flask import session, redirect, url_for, flash


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
    """
    관리자 권한 필요 데코레이터
    
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
        if not session.get('is_admin', False):
            flash('관리자만 접근 가능한 메뉴입니다.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

