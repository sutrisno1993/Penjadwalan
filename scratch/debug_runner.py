import sys
import logging
logging.basicConfig(level=logging.DEBUG)

print("Starting custom uvicorn runner...")
try:
    import uvicorn
    from backend.main import app
    print("App imported successfully! Running uvicorn...")
    uvicorn.run(app, host="127.0.0.1", port=8002)
except Exception as e:
    import traceback
    traceback.print_exc()
    print("CRASHED:", str(e))
