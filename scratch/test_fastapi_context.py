from starlette.concurrency import run_in_threadpool
import asyncio
from backend.database import set_thread_branch, active_branch, get_thread_branch, get_db_connection

async def test():
    # Set context in async middleware (main thread)
    branch = "jakarta"
    token = active_branch.set(branch)
    set_thread_branch(branch)
    
    print("Async middleware main thread get_thread_branch():", get_thread_branch())
    print("Async middleware main thread active_branch.get():", active_branch.get())
    
    def sync_endpoint():
        # Inside sync route handler (run_in_threadpool)
        tb = get_thread_branch()
        av = active_branch.get()
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT DATABASE() as db")
        db_name = cur.fetchone()['db']
        conn.close()
        return tb, av, db_name

    tb, av, db_name = await run_in_threadpool(sync_endpoint)
    print("Sync endpoint worker thread get_thread_branch():", tb)
    print("Sync endpoint worker thread active_branch.get():", av)
    print("Sync endpoint worker thread actual connected DB:", db_name)
    
    active_branch.reset(token)

asyncio.run(test())
