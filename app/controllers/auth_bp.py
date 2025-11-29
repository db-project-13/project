"""
인증 관련 Blueprint (로그인, 로그아웃)
"""
from flask import Blueprint, render_template, request, session, redirect, url_for, flash

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    로그인 페이지 및 로그인 처리
    
    GET: 로그인 폼 표시
    POST: 로그인 처리 (추후 MemberService 연동)
    """
    if request.method == 'POST':
        user_id = request.form.get('id', '').strip()
        password = request.form.get('password', '').strip()
        
        # TODO: MemberService를 통한 인증 처리
        # member_service = MemberService(member_dao)
        # member = member_service.authenticate(user_id, password)
        
        # 임시: 하드코딩된 테스트 (추후 제거)
        if user_id and password:
            # 세션에 사용자 정보 저장
            session['user_id'] = user_id
            session['is_admin'] = request.form.get('is_admin', 'F') == 'T'
            session.permanent = True
            
            flash('로그인되었습니다.', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('아이디와 비밀번호를 입력해주세요.', 'error')
    
    # GET 요청 또는 로그인 실패 시 로그인 폼 표시
    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    """
    로그아웃 처리
    
    Returns:
        메인 페이지로 리다이렉트
    """
    user_id = session.get('user_id')
    
    if user_id:
        session.clear()
        flash('로그아웃되었습니다.', 'info')
    else:
        flash('이미 로그아웃 상태입니다.', 'info')
    
    return redirect(url_for('main.index'))

