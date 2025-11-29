"""
애플리케이션 설정
"""
import os
from datetime import timedelta


class Config:
    """기본 설정 클래스"""
    
    # Flask 기본 설정
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # 세션 설정
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # 데이터베이스 설정 (추후 구현)
    DB_DSN = os.environ.get('DB_DSN') or 'localhost:1521/orcl'
    DB_USER = os.environ.get('DB_USER') or 'university'
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or 'comp322'
    
    # Connection Pool 설정
    DB_POOL_MIN = int(os.environ.get('DB_POOL_MIN', 2))
    DB_POOL_MAX = int(os.environ.get('DB_POOL_MAX', 10))
    
    # 디버그 모드
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'


class DevelopmentConfig(Config):
    """개발 환경 설정"""
    DEBUG = True


class ProductionConfig(Config):
    """프로덕션 환경 설정"""
    DEBUG = False


# 설정 매핑
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

