"""
회원 관리 Blueprint (회원가입, 회원정보 수정)
"""
from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from app.utils.decorators import login_required

member_bp = Blueprint('member', __name__, url_prefix='/member')


@member_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    회원가입 페이지 및 회원가입 처리
    
    GET: 회원가입 폼 표시
    POST: 회원가입 처리 (추후 MemberService 연동)
    """
    # 이미 로그인된 경우 메인으로 리다이렉트
    if 'user_id' in session:
        flash('이미 로그인되어 있습니다.', 'info')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        # 폼 데이터 수집
        form_data = {
            'id': request.form.get('id', '').strip(),
            'password': request.form.get('password', '').strip(),
            'name': request.form.get('name', '').strip(),
            'address': request.form.get('address', '').strip(),
            'sex': request.form.get('sex', '').strip().upper(),
            'birthday': request.form.get('birthday', '').strip()
        }
        
        # TODO: MemberService를 통한 회원가입 처리
        # member_service = MemberService(member_dao)
        # try:
        #     member_service.register_member(form_data)
        #     flash('회원가입이 완료되었습니다. 로그인해주세요.', 'success')
        #     return redirect(url_for('auth.login'))
        # except ValueError as e:
        #     flash(str(e), 'error')
        
        # 임시: 성공 메시지 (추후 제거)
        flash('회원가입 기능은 추후 구현 예정입니다.', 'info')
        return redirect(url_for('auth.login'))
    
    return render_template('member/register.html')


@member_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """
    회원정보 수정 페이지 및 수정 처리
    
    GET: 회원정보 수정 폼 표시
    POST: 회원정보 수정 처리 (추후 MemberService 연동)
    """
    user_id = session.get('user_id')
    
    if request.method == 'POST':
        # 폼 데이터 수집
        form_data = {
            'password': request.form.get('password', '').strip(),
            'address': request.form.get('address', '').strip()
        }
        
        # TODO: MemberService를 통한 회원정보 수정 처리
        # member_service = MemberService(member_dao)
        # try:
        #     member_service.modify_profile(user_id, form_data)
        #     flash('회원정보가 성공적으로 수정되었습니다.', 'success')
        #     return redirect(url_for('member.edit_profile'))
        # except ValueError as e:
        #     flash(str(e), 'error')
        
        # 임시: 성공 메시지 (추후 제거)
        flash('회원정보 수정 기능은 추후 구현 예정입니다.', 'info')
        return redirect(url_for('member.edit_profile'))
    
    # TODO: 현재 회원정보 조회
    # member_dao = MemberDAO(current_app.db)
    # member = member_dao.find_by_id(user_id)
    
    # 임시 데이터
    member = {
        'id': user_id,
        'password': '****',
        'address': '주소 정보 없음'
    }
    
    return render_template('member/profile_edit.html', member=member)

