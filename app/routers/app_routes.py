from fastapi import HTTPException, APIRouter
from fastapi.responses import StreamingResponse
from app.agents.services.chat_service import ChatService
from app.schemas.chat_schema import MessageRequest, ChatResponse
import json
import logging

# Configurar logging
logger = logging.getLogger(__name__)

app_routes = APIRouter()
chat_service = ChatService()

@app_routes.get("/hello")
async def say_hello():
    return {"message": "Hello from app_routes"}

@app_routes.post("/chat", response_model=ChatResponse)
async def chat(message_request: MessageRequest):
    """
    Endpoint de chat estándar (respuesta completa).
    
    Args:
        message_request: Objeto con el mensaje y opcional thread_id
        
    Returns:
        ChatResponse: La respuesta del agente con el thread_id
        
    Raises:
        HTTPException: Si ocurre un error al procesar el mensaje
    """
    try:
        logger.info(f"Chat request received: thread_id={message_request.thread_id}")
        
        response = await chat_service.chat(
            message=message_request.message,
            thread_id=message_request.thread_id
        )
        
        return response
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing chat: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app_routes.post("/chat/stream")
async def chat_stream(message_request: MessageRequest):
    """
    Endpoint de chat con streaming (respuesta en tiempo real).
    
    Args:
        message_request: Objeto con el mensaje y opcional thread_id
        
    Returns:
        StreamingResponse: Stream de eventos SSE con la respuesta
        
    Raises:
        HTTPException: Si ocurre un error al procesar el mensaje
    """
    try:
        logger.info(f"Chat stream request received: thread_id={message_request.thread_id}")
        
        async def generate():
            try:
                async for chunk in chat_service.chat_stream(
                    message=message_request.message,
                    thread_id=message_request.thread_id
                ):
                    yield f"data: {json.dumps(chunk)}\n\n"
            except Exception as e:
                logger.error(f"Error in stream generation: {str(e)}")
                yield f"data: {json.dumps({'type': 'error', 'data': str(e)})}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
        
    except ValueError as e:
        logger.error(f"Validation error in stream: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error starting chat stream: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")
