# app/db.py
import oracledb
from flask import current_app, g

class OracleDB:
    def __init__(self):
        self.pool = None

    def init_app(self, app):
        """Flask 앱 초기화 시 실행되어 커넥션 풀을 생성합니다."""
        
        # config.py의 설정값 가져오기
        user = app.config.get('DB_USER')
        password = app.config.get('DB_PASSWORD')
        dsn = app.config.get('DB_DSN')
        min_pool = app.config.get('DB_POOL_MIN', 2)
        max_pool = app.config.get('DB_POOL_MAX', 10)

        try:
            # 커넥션 풀 생성 (Thin 모드 기본 사용)
            self.pool = oracledb.create_pool(
                user=user,
                password=password,
                dsn=dsn,
                min=min_pool,
                max=max_pool,
                increment=1
            )
            print(f"✅ Oracle DB Pool initialized (DSN: {dsn})")
        except oracledb.Error as e:
            print(f"❌ DB Pool creation failed: {e}")

        # 요청이 끝나면 자동으로 db_close 호출
        app.teardown_appcontext(self.close_db)

    def get_db(self):
        """현재 요청(Request)에 할당된 DB 연결을 반환합니다."""
        if 'db_conn' not in g:
            try:
                # 풀에서 연결 하나를 빌려서 g(전역 컨텍스트)에 저장
                g.db_conn = self.pool.acquire()
            except oracledb.Error as e:
                print(f"Connection acquire failed: {e}")
                return None
        return g.db_conn

    def close_db(self, e=None):
        """요청이 끝나면 연결을 풀에 반환합니다."""
        db_conn = g.pop('db_conn', None)
        if db_conn is not None:
            try:
                self.pool.release(db_conn)
            except oracledb.Error as e:
                print(f"Connection release failed: {e}")

# 싱글톤 인스턴스 생성 (이 변수를 다른 파일에서 import 해서 사용)
db = OracleDB()