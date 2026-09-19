import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .graph import graph

app = FastAPI(title="ReviewGraph")
STATIC = Path(__file__).resolve().parent.parent / "static"
app.mount("/static", StaticFiles(directory=STATIC), name="static")


class Req(BaseModel):
    code: str


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


@app.post("/api/review")
def review(req: Req):
    return graph.invoke({"code": req.code})


@app.post("/api/stream")
def stream(req: Req):
    """SSE：每个节点跑完就推一条，前端据此点亮流程图。"""
    def gen():
        for chunk in graph.stream({"code": req.code}, stream_mode="updates"):
            for node, upd in chunk.items():
                yield f"data: {json.dumps({'node': node, 'update': upd}, ensure_ascii=False)}\n\n"
        yield 'data: {"done": true}\n\n'
    return StreamingResponse(gen(), media_type="text/event-stream")
