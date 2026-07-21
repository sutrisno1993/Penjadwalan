import concurrent.futures
from backend.database import set_thread_branch, active_branch, get_thread_branch, get_db_connection

token = active_branch.set('jakarta')
set_thread_branch('jakarta')

print("Main thread get_thread_branch():", get_thread_branch())
print("Main thread ContextVar:", active_branch.get())

def worker():
    # Threadpool worker
    return (get_thread_branch(), active_branch.get())

with concurrent.futures.ThreadPoolExecutor() as ex:
    res = ex.submit(worker).result()
    print("Worker thread get_thread_branch():", res[0])
    print("Worker thread ContextVar:", res[1])

# Check what database connection is actually returned in worker thread
def worker_conn():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT DATABASE() as db")
    row = cur.fetchone()
    conn.close()
    return row['db']

with concurrent.futures.ThreadPoolExecutor() as ex:
    db = ex.submit(worker_conn).result()
    print("Worker thread actual connected DB:", db)
