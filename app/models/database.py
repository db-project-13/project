# 12월 8일 이태호
# 파일 생성
import os
import oracledb


class OracleDBPool:
    def __init__(self):
        self.pool = None

    def init_pool(self, dsn, user, password, min_size=2, max_size=10):
        if self.pool is None:
            self.pool = oracledb.create_pool(
                user=user,
                password=password,
                dsn=dsn,
                min=min_size,
                max=max_size,
                increment=1,
                threaded=True
            )
            print(f"✅ Oracle DB Pool initialized (DSN: {dsn})")

    def get_db(self):
        if self.pool is None:
            raise RuntimeError("DB pool is not initialized.")
        return self.pool.acquire()


db = OracleDBPool()
