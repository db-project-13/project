# 12/09 anton061311
'''
# app/db.py
import oracledb
from flask import g


class OracleDB:
    def __init__(self):
        self.pool = None

    def init_app(self, app):
        """Flask 앱 초기화 시 실행되어 커넥션 풀을 생성합니다."""

        user = app.config.get("DB_USER")
        password = app.config.get("DB_PASSWORD")
        dsn = app.config.get("DB_DSN")
        min_pool = int(app.config.get("DB_POOL_MIN", 2))
        max_pool = int(app.config.get("DB_POOL_MAX", 10))

        if not user or not password or not dsn:
            raise RuntimeError(
                "DB_USER, DB_PASSWORD, DB_DSN 설정이 필요합니다."
            )

        self.pool = oracledb.create_pool(
            user=user,
            password=password,
            dsn=dsn,          # ✅ 여기 DSN 문자열만 제대로 맞추면 됨
            min=min_pool,
            max=max_pool,
            increment=1,
        )

        print(f"✅ Oracle DB Pool initialized (DSN: {dsn})")

        # 요청 끝날 때마다 close_db 실행
        app.teardown_appcontext(self.close_db)

    def get_db(self):
        """현재 요청에 할당된 DB 연결 반환 (없으면 풀에서 하나 빌려옴)."""
        if self.pool is None:
            raise RuntimeError("DB pool is not initialized.")

        if "db_conn" not in g:
            try:
                g.db_conn = self.pool.acquire()
            except oracledb.Error as e:
                print(f"Connection acquire failed: {e}")
                return None
        return g.db_conn

    def close_db(self, e=None):
        """요청이 끝나면 연결을 풀에 반환합니다."""
        db_conn = g.pop("db_conn", None)
        if db_conn is not None:
            try:
                # 세션 풀에서 가져온 커넥션은 close() 하면 풀로 반환됨
                db_conn.close()
            except oracledb.Error as e:
                print(f"Connection release failed: {e}")


# 싱글톤 인스턴스
db = OracleDB()
'''



# app/db.py
from contextlib import contextmanager
import oracledb
from flask import g


class OracleDB:
    def __init__(self):
        self.pool = None

    def init_app(self, app):
        """Flask 앱 초기화 시 실행되어 커넥션 풀을 생성합니다."""

        user = app.config.get("DB_USER")
        password = app.config.get("DB_PASSWORD")
        dsn = app.config.get("DB_DSN")
        min_pool = int(app.config.get("DB_POOL_MIN", 2))
        max_pool = int(app.config.get("DB_POOL_MAX", 10))

        if not user or not password or not dsn:
            raise RuntimeError(
                "DB_USER, DB_PASSWORD, DB_DSN 설정이 필요합니다."
            )

        self.pool = oracledb.create_pool(
            user=user,
            password=password,
            dsn=dsn,          # ✅ 여기 DSN 문자열만 제대로 맞추면 됨
            min=min_pool,
            max=max_pool,
            increment=1,
        )

        print(f"✅ Oracle DB Pool initialized (DSN: {dsn})")

        # 요청 끝날 때마다 close_db 실행
        app.teardown_appcontext(self.close_db)

    def get_db(self):
        """현재 요청에 할당된 DB 연결 반환 (없으면 풀에서 하나 빌려옴)."""
        if self.pool is None:
            raise RuntimeError("DB pool is not initialized.")

        if "db_conn" not in g:
            try:
                g.db_conn = self.pool.acquire()
            except oracledb.Error as e:
                print(f"Connection acquire failed: {e}")
                return None
        return g.db_conn

    def close_db(self, e=None):
        """요청이 끝나면 연결을 풀에 반환합니다."""
        db_conn = g.pop("db_conn", None)
        if db_conn is not None:
            try:
                # 세션 풀에서 가져온 커넥션은 close() 하면 풀로 반환됨
                db_conn.close()
            except oracledb.Error as e:
                print(f"Connection release failed: {e}")

    @contextmanager
    def transaction(self):
        """
        트랜잭션 컨텍스트 매니저.
        사용 예:
            with db.transaction() as conn:
                cursor = conn.cursor()
                cursor.execute(...)
        """
        conn = self.get_db()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise


# 싱글톤 인스턴스
db = OracleDB()
