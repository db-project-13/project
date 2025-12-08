# ----------------------------------------------------------
# 2025.12.05 이태호
# ----------------------------------------------------------
"""
회원 관리 Blueprint (회원가입, 회원정보 수정)
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.services import member_service
from app.utils.decorators import login_required

member_bp = Blueprint("member", __name__, url_prefix="/member")


@member_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        form = {
            "id": request.form.get("id").strip(),
            "password": request.form.get("password").strip(),
            "name": request.form.get("name").strip(),
            "address": request.form.get("address").strip(),
            "sex": request.form.get("sex"),
            "birthday": request.form.get("birthday")
        }

        try:
            member_service.register(form)
            flash("회원가입 완료! 로그인 해주세요.", "success")
            return redirect(url_for("auth.login"))

        except member_service.MemberServiceError as e:
            flash(str(e), "danger")

    return render_template("member/register.html")


@member_bp.route("/profile")
@login_required
def profile():
    user_id = session.get("user_id")
    member = member_service.get_profile(user_id)
    return render_template("member/profile.html", member=member)


@member_bp.route("/profile/edit", methods=["GET", "POST"])
@login_required
def profile_edit():
    user_id = session.get("user_id")

    if request.method == "POST":
        form = {
            "password": request.form.get("password"),
            "address": request.form.get("address"),
            "sex": request.form.get("sex"),
            "birthday": request.form.get("birthday")
        }

        try:
            member_service.update_profile(user_id, form)
            flash("회원정보가 수정되었습니다.", "success")
            return redirect(url_for("member.profile"))

        except member_service.MemberServiceError as e:
            flash(str(e), "danger")

    member = member_service.get_profile(user_id)
    return render_template("member/profile_edit.html", member=member)
