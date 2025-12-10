# ----------------------------------------------------------
# 2025.12.05 이태호
# - 로그인 화면 표시
# - MemberService를 이용한 실제 로그인 처리
# - 세션에 사용자 정보 저장 / 로그아웃 처리
# ----------------------------------------------------------
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.services import member_service

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_id = request.form.get("id", "").strip()
        password = request.form.get("password", "").strip()

        if not user_id or not password:
            flash("아이디와 비밀번호를 입력해주세요.", "danger")
            return render_template("auth/login.html")

        try:
            # 서비스 계층에 실제 로그인 로직 위임
            member = member_service.login(user_id, password)

            # 세션에 로그인 정보 저장
            session["user_id"] = member["id"]
            session["user_name"] = member["name"]
            # 현재 DB에는 관리자 컬럼이 없어서 기본 False / 'T' 체크만 해둠
            session["is_admin"] = (member.get("is_admin") == "T")
            session.permanent = True  # remember-like 효과

            flash(f"{member['name']}님 로그인 완료", "success")
            return redirect(url_for("main.index"))

        except member_service.InvalidLoginError as e:
            flash(str(e), "danger")

        except member_service.MemberServiceError as e:
            flash(str(e), "danger")

    # GET 요청이거나 에러가 난 경우
    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("로그아웃 되었습니다.", "info")
    return redirect(url_for("main.index"))
