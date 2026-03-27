import json
import logging

from fastapi import HTTPException, APIRouter
from fastapi.responses import StreamingResponse

from app.services.chat_service import ChatService
from app.schemas.chat_schema import MessageRequest, ChatResponse

logger = logging.getLogger(__name__)

app_routes = APIRouter()
_chat_service = ChatService()


@app_routes.get("/hello")
async def health_check():
    return {"message": "ProjectJ Agent is running"}


@app_routes.post("/chat", response_model=ChatResponse)
async def chat(request: MessageRequest):
    try:
        logger.info(f"POST /chat thread_id={request.thread_id}")
        return await _chat_service.chat(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"POST /chat error: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@app_routes.post("/chat/stream")
async def chat_stream(request: MessageRequest):
    try:
        logger.info(f"POST /chat/stream thread_id={request.thread_id}")

        async def generate():
            try:
                async for chunk in _chat_service.chat_stream(request):
                    yield f"data: {json.dumps(chunk)}\n\n"
            except Exception as e:
                logger.error(f"Stream generation error: {e}")
                yield f"data: {json.dumps({'type': 'error', 'data': str(e)})}\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"POST /chat/stream error: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")
