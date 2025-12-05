"""
Flask 애플리케이션 팩토리
"""
from flask import Flask
from app.config import Config
from app.db import db

# 주의: .env 파일은 run.py에서 이미 로드되므로 여기서는 로드하지 않음
# (run.py가 진입점이므로 run.py에서 load_dotenv() 호출)


def create_app(config_class=Config):
    """
    Flask 애플리케이션 팩토리 함수
    
    Args:
        config_class: 설정 클래스 (기본값: Config)
    
    Returns:
        Flask 애플리케이션 인스턴스
    """
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 데이터베이스 초기화
    db.init_app(app)
    
    # Blueprint 등록
    from app.controllers.auth_bp import auth_bp
    from app.controllers.member_bp import member_bp
    from app.controllers.content_bp import content_bp
    from app.controllers.admin_bp import admin_bp
    from app.controllers.main_bp import main_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(member_bp)
    app.register_blueprint(content_bp)
    app.register_blueprint(admin_bp)
    
    return app

