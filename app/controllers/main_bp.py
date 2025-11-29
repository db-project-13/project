"""
메인 페이지 Blueprint
"""
from flask import Blueprint, render_template, session

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """
    메인 페이지
    
    Returns:
        메인 페이지 템플릿
    """
    # 세션 정보 확인 (로그인 상태)
    user_id = session.get('user_id')
    is_admin = session.get('is_admin', False)
    
    return render_template(
        'main/index.html',
        user_id=user_id,
        is_admin=is_admin
    )

