import logging
import asyncio
import functools
import time
from fastapi import FastAPI, Body, Query

# -------- Decorator with timing --------
def log_execution(logger: logging.Logger):
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            logger.info(f"Entering: {func.__name__}")
            start = time.time()
            try:
                result = await func(*args, **kwargs)
                return {
                    "result": result,
                    "execution_time": round(time.time() - start, 3)
                }
            finally:
                logger.info(f"Exiting: {func.__name__}")

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            logger.info(f"Entering: {func.__name__}")
            start = time.time()
            try:
                result = func(*args, **kwargs)
                return {
                    "result": result,
                    "execution_time": round(time.time() - start, 3)
                }
            finally:
                logger.info(f"Exiting: {func.__name__}")

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

# -------- Logger Setup --------
logger = logging.getLogger("myapp")
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

# -------- FastAPI App --------
app = FastAPI()

@log_execution(logger)
@app.get("/sync-get")
def sync_get(sleep_sec: float = Query(1.0)):
    time.sleep(sleep_sec)
    return {"message": "sync GET", "slept": f"{sleep_sec}s"}

@log_execution(logger)
@app.post("/sync-post")
def sync_post(payload: dict = Body(...), sleep_sec: float = Query(1.0)):
    time.sleep(sleep_sec)
    return {"message": "sync POST", "slept": f"{sleep_sec}s", "received": payload}

@log_execution(logger)
@app.get("/async-get")
async def async_get(sleep_sec: float = Query(1.0)):
    await asyncio.sleep(sleep_sec)
    return {"message": "async GET", "slept": f"{sleep_sec}s"}

@log_execution(logger)
@app.post("/async-post")
async def async_post(payload: dict = Body(...), sleep_sec: float = Query(1.0)):
    await asyncio.sleep(sleep_sec)
    return {"message": "async POST", "slept": f"{sleep_sec}s", "received": payload}
