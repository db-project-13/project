# ----------------------------------------------------------
# 2025.12.05 이태호
# ----------------------------------------------------------
"""
회원 관리 Blueprint (회원가입, 회원정보 수정)
"""
from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from app.utils.decorators import login_required
from app.services import member_service

member_bp = Blueprint('member', __name__, url_prefix='/member')


@member_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    회원가입 페이지 및 회원가입 처리
    """
    if request.method == 'GET':
        return render_template('member/register.html')

    form = request.form

    try:
        member_service.register_member(form)
        flash('회원가입이 완료되었습니다. 로그인 해주세요.', 'success')
        return redirect(url_for('auth.login'))

    except member_service.DuplicateIdError as e:
        flash(str(e), 'danger')
        return render_template('member/register.html')

    except member_service.MemberServiceError as e:
        flash(str(e), 'danger')
        return render_template('member/register.html')

    except Exception:
        flash('회원가입 처리 중 오류가 발생했습니다.', 'danger')
        return render_template('member/register.html')


@member_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def profile_edit():
    """
    마이페이지 - 비밀번호/주소 수정
    """
    user_id = session.get('user_id')

    if request.method == 'GET':
        member = member_service.get_profile(user_id)
        if member is None:
            flash('회원 정보를 찾을 수 없습니다.', 'danger')
            return redirect(url_for('main.index'))

        return render_template('member/profile_edit.html', member=member)

    form = request.form
    try:
        member_service.update_profile(user_id, form)
        flash('회원 정보가 수정되었습니다.', 'success')
        return redirect(url_for('member.profile_edit'))

    except member_service.MemberServiceError as e:
        flash(str(e), 'danger')
        member = member_service.get_profile(user_id)
        return render_template('member/profile_edit.html', member=member)

    except Exception:
        flash('회원 정보 수정 중 오류가 발생했습니다.', 'danger')
        member = member_service.get_profile(user_id)
        return render_template('member/profile_edit.html', member=member)
