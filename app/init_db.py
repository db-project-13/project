import oracledb
import os
import sys
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# === [설정] ===
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_DSN = os.environ.get('DB_DSN')

# 실행할 SQL 파일 목록 (순서대로 실행됩니다)
SQL_FILES = [
    'app\DBreset_table.sql',    # 1. 테이블/시퀀스 초기화 및 생성
    'app\DBreset_insert.sql',    # 2. 더미 데이터 삽입
]

def execute_sql_file(conn, cursor, filename):
    """단일 SQL 파일을 읽어서 실행하는 함수"""
    print(f"\n📄 파일 처리 시작: {filename}")
    
    if not os.path.exists(filename):
        print(f"❌ 오류: '{filename}' 파일을 찾을 수 없습니다.")
        return False

    try:
        with open(filename, 'r', encoding='ANSI') as f:
            sql_content = f.read()
    except Exception as e:
        print(f"❌ 파일 읽기 오류: {e}")
        return False

    # 구문 분리 (세미콜론 기준)
    statements = sql_content.split(';')
    
    success_count = 0
    error_count = 0

    for statement in statements:
        stmt = statement.strip()
        if not stmt:
            continue
        
        try:
            cursor.execute(stmt)
            # 실행 성공 로그 (너무 길면 자르기)
            log_stmt = stmt.replace('\n', ' ')[:40]
            print(f"   ✅ 실행: {log_stmt}...")
            success_count += 1
        except oracledb.Error as e:
            error_obj, = e.args
            # ORA-00942: 테이블 없음, ORA-02289: 시퀀스 없음 (무시)
            if error_obj.code in (942, 2289):
                print(f"   ⚠️  건너뜀 (대상 없음): {stmt[:30]}...")
            else:
                print(f"   ❌ 실패: {stmt[:30]}...")
                print(f"      └─ 이유: {error_obj.message}")
                error_count += 1

    print(f"   [결과] 성공: {success_count}건, 실패/건너뜀: {error_count}건")
    return True

def run_init_script():
    print(f"🔄 데이터베이스 초기화를 시작합니다... (Target: {DB_DSN})")
    
    conn = None
    try:
        # DB 연결 (한 번 연결해서 여러 파일 실행)
        conn = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)
        cursor = conn.cursor()
        
        # 파일 목록 순회하며 실행
        for sql_file in SQL_FILES:
            success = execute_sql_file(conn, cursor, sql_file)
            if not success:
                print(f"⛔ '{sql_file}' 처리 중 문제가 발생하여 중단합니다.")
                break
            
            # 파일 하나 끝날 때마다 커밋
            conn.commit()
            
        print("\n" + "=" * 50)
        print("🎉 모든 작업이 완료되었습니다.")
        
    except oracledb.Error as e:
        print(f"\n❌ DB 연결 치명적 오류: {e}")
    finally:
        if conn:
            conn.close()
            print("🔌 DB 연결 해제됨")

if __name__ == '__main__':
    # 실행 전 확인
    print(f"대상 파일: {', '.join(SQL_FILES)}")
    check = input(f"⚠️  주의: 위 파일들을 순서대로 실행하여 DB를 초기화합니다.\n계속하시겠습니까? (y/n): ")
    
    if check.lower() == 'y':
        run_init_script()
    else:
        print("작업이 취소되었습니다.")