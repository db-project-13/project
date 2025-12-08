# ----------------------------------------------------------
# 2025.12.05 이태호
# - 로그인 화면 표시
# - MemberService를 이용한 실제 로그인 처리
# - 세션에 사용자 정보 저장 / 로그아웃 처리
# ----------------------------------------------------------
"""
인증 관련 Blueprint (로그인, 로그아웃)
"""
from flask import Blueprint, render_template, request, session, redirect, url_for, flash

from app.services import member_service

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    로그인 페이지 및 로그인 처리
    
    GET: 로그인 폼 표시
    POST: member_service.login()을 통한 로그인 처리
    """
    if request.method == 'POST':
        user_id = request.form.get('id', '').strip()
        password = request.form.get('password', '').strip()

        if not user_id or not password:
            flash('아이디와 비밀번호를 입력해주세요.', 'danger')
            return render_template('auth/login.html')

        try:
            member = member_service.login(user_id, password)

            session['user_id'] = member['id']
            session['user_name'] = member['name']
            # 현재 스키마에는 등급/관리자 정보가 없으므로 기본 False
            session['is_admin'] = False
            session.permanent = True

            flash(f"{member['name']}님, 로그인되었습니다.", 'success')
            return redirect(url_for('main.index'))

        except member_service.InvalidLoginError as e:
            flash(str(e), 'danger')
            return render_template('auth/login.html')

        except member_service.MemberServiceError as e:
            flash(str(e), 'danger')
            return render_template('auth/login.html')

        except Exception:
            flash('로그인 처리 중 오류가 발생했습니다.', 'danger')
            return render_template('auth/login.html')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    """
    로그아웃 처리
    """
    user_id = session.get('user_id')

    if user_id:
        session.clear()
        flash('로그아웃되었습니다.', 'info')
    else:
        flash('이미 로그아웃 상태입니다.', 'info')

    return redirect(url_for('main.index'))
