"""
Flask 애플리케이션 진입점 (WSGI Entry Point)
"""
from dotenv import load_dotenv
import os

# .env 파일 로드 (가장 먼저 실행)
load_dotenv()

from app import create_app
from app.config import config

# 환경 변수에서 설정 선택 (기본값: development)
config_name = os.environ.get('FLASK_ENV', 'development')

# Flask 앱 생성
app = create_app(config[config_name])

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8000)

