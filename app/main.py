import os
import sys
from fastapi import FastAPI
from fastapi.responses import Response, JSONResponse, HTMLResponse
from contextlib import asynccontextmanager

if int(sys.version.split(".")[1]) > 10:
    from redis.asyncio import from_url
else:
    from aioredis import from_url

app = FastAPI()


@asynccontextmanager
async def lifespan(app: FastAPI):
    cache_redis_url = os.environ.get('REDIS_URL')
    redis = await from_url(cache_redis_url,
                           encoding='utf-8',
                           decode_responses=True,
                           health_check_interval=60,
                           socket_connect_timeout=True,
                           retry_on_timeout=True,
                           socket_keepalive=True)
    app.state.redis = redis
    try:
        yield
    finally:
        redis.close()
        await redis.wait_closed()

app.router.lifespan_context = lifespan


@app.post("/set")
async def set_key_value(key: str, value: str):
    try:
        status = await app.state.redis.set(key, value)
        return HTMLResponse(status_code=200, content=str(status))
    except Exception as e:
        print(f"set {key} 出错 {e}")
        return HTMLResponse(status_code=500, content="-1")


@app.get("/get")
async def get_key_value(key: str):
    try:
        value = await app.state.redis.get(key)
        return JSONResponse(status_code=200, content={"key": key, "value": value})
    except Exception as e:
        print(f"hgetall {key} 出错 {e}")
        return JSONResponse(status_code=500, content={})


@app.delete("/delete")
async def get_key_value(key: str):
    try:
        status = await app.state.redis.delete(key)
        return HTMLResponse(status_code=200, content=str(status))
    except Exception as e:
        print(f"hgetall {key} 出错 {e}")
        return HTMLResponse(status_code=500, content="-1")


@app.post("/hmset")
async def hmset_key_value(key: str, values: dict):
    try:
        status = await app.state.redis.hset(key, mapping=values)
        return HTMLResponse(status_code=200, content=str(status))
    except Exception as e:
        print(f"hmset {key} 出错 {e}")
        return HTMLResponse(status_code=500, content="-1")


@app.get("/hgetall")
async def hgetall_key(key: str):
    try:
        values = await app.state.redis.hgetall(key)
        return JSONResponse(status_code=200, content=values)
    except Exception as e:
        print(f"hgetall {key} 出错 {e}")
        return JSONResponse(status_code=500, content={})


@app.get("/hget")
async def hget_key_value(key: str, field: str):
    try:
        value = await app.state.redis.hget(key, field)
        if value is None:
            return Response(status_code=404, content=value)
        if "chanty-data.s3.us-east-1.amazonaws.com" in value:
            value = value.replace("chanty-data.s3.us-east-1.amazonaws.com", "s3ab.deno.dev")
        return Response(status_code=200, content=value)
    except Exception as e:
        print(f"hget {key} {field} 出错 {e}")
        return Response(status_code=500, content="")


@app.post("/hset")
async def hset_key_value(key: str, field: str, value: str):
    try:
        status = await app.state.redis.hset(key, field, value)
        return HTMLResponse(status_code=200, content=str(status))
    except Exception as e:
        print(f"hset {key} 出错 {field} {e}")
        return HTMLResponse(status_code=500, content="-1")


@app.delete("/hdel")
async def hdel_key_field(key: str, field: str):
    try:
        result = await app.state.redis.hdel(key, field)
        if result == 0:
            return HTMLResponse(status_code=200, content=str(result))
        return HTMLResponse(status_code=200, content=str(result))
    except Exception as e:
        print(f"hdel {key} 出错 {field} {e}")
        return HTMLResponse(status_code=200, content="-1")


if __name__ == '__main__':
    import uvicorn

    PORT = os.environ.get('PORT') or 8080
    uvicorn.run(app, host="0.0.0.0", port=PORT)
