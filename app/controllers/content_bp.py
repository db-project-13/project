"""
콘텐츠 및 리뷰 관리 Blueprint
"""
from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from app.utils.decorators import login_required

content_bp = Blueprint('content', __name__, url_prefix='/content')


@content_bp.route('/search', methods=['GET', 'POST'])
def search():
    """
    콘텐츠 검색 페이지 및 검색 처리
    
    GET: 검색 폼 표시
    POST: 검색 결과 표시 (추후 ReviewService 연동)
    """
    if request.method == 'POST':
        search_term = request.form.get('search_term', '').strip()
        
        if not search_term:
            flash('검색어를 입력해주세요.', 'error')
            return render_template('content/search.html')
        
        # TODO: ReviewService를 통한 콘텐츠 검색
        # review_service = ReviewService(content_dao)
        # results = review_service.search_content(search_term)
        
        # 임시: 빈 결과 리스트
        results = []
        flash(f'"{search_term}" 검색 결과: {len(results)}개 (검색 기능은 추후 구현 예정)', 'info')
        
        return render_template('content/search_results.html', results=results, search_term=search_term)
    
    return render_template('content/search.html')


@content_bp.route('/<int:content_id>/review', methods=['GET', 'POST'])
@login_required
def create_review(content_id):
    """
    리뷰 등록 페이지 및 등록 처리
    
    Args:
        content_id: 콘텐츠 ID
    
    GET: 리뷰 등록 폼 표시
    POST: 리뷰 등록 처리 (추후 ReviewService 연동)
    """
    user_id = session.get('user_id')
    
    if request.method == 'POST':
        try:
            rating = int(request.form.get('rating', 0))
            comment = request.form.get('comment', '').strip()
            
            if rating < 1 or rating > 5:
                flash('평점은 1-5 사이의 값이어야 합니다.', 'error')
                return redirect(url_for('content.create_review', content_id=content_id))
            
            # TODO: ReviewService를 통한 리뷰 등록
            # review_service = ReviewService(content_dao)
            # try:
            #     review_service.register_review(user_id, content_id, rating, comment)
            #     flash('리뷰가 성공적으로 등록되었습니다.', 'success')
            #     return redirect(url_for('content.detail', content_id=content_id))
            # except ValueError as e:
            #     flash(str(e), 'error')
            
            # 임시: 성공 메시지
            flash(f'리뷰 등록 기능은 추후 구현 예정입니다. (콘텐츠 ID: {content_id}, 평점: {rating})', 'info')
            return redirect(url_for('content.create_review', content_id=content_id))
            
        except ValueError:
            flash('평점은 숫자로 입력해주세요.', 'error')
    
    # TODO: 콘텐츠 정보 조회
    # content_dao = ContentDAO(current_app.db)
    # content = content_dao.find_by_id(content_id)
    
    # 임시 데이터
    content = {
        'content_id': content_id,
        'title': f'콘텐츠 {content_id} (임시)'
    }
    
    return render_template('content/review_form.html', content=content)


@content_bp.route('/<int:content_id>')
def detail(content_id):
    """
    콘텐츠 상세 페이지
    
    Args:
        content_id: 콘텐츠 ID
    
    Returns:
        콘텐츠 상세 페이지 템플릿
    """
    # TODO: 콘텐츠 정보 및 리뷰 목록 조회
    # content_dao = ContentDAO(current_app.db)
    # content = content_dao.find_by_id(content_id)
    # reviews = content_dao.get_reviews_by_content_id(content_id)
    
    # 임시 데이터
    content = {
        'content_id': content_id,
        'title': f'콘텐츠 {content_id} (임시)',
        'release_date': '2024-01-01',
        'producer': '임시 제작사'
    }
    reviews = []
    
    return render_template('content/detail.html', content=content, reviews=reviews)

