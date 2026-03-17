from langchain_core.messages import HumanMessage
from ..agent.my_agent import create_product_agent
import uuid
import logging
from typing import Optional, AsyncGenerator

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self):
        self.agent = create_product_agent()
        logger.info("ChatService initialized with product agent")

    def initialize_session(self) -> str:
        """Crea un nuevo thread_id para una sesión"""
        thread_id = str(uuid.uuid4())
        logger.info(f"New session initialized: {thread_id}")
        return thread_id

    async def chat(self, message: str, thread_id: Optional[str] = None) -> dict:
        """
        Procesa un mensaje del usuario y devuelve una respuesta.
        
        Args:
            message: El mensaje del usuario
            thread_id: ID de sesión opcional. Si no se proporciona, se crea uno nuevo
            
        Returns:
            dict con 'response' y 'thread_id'
            
        Raises:
            Exception: Si hay un error al procesar el mensaje
        """
        try:
            # Si no hay thread_id, crear uno nuevo
            if not thread_id:
                thread_id = self.initialize_session()
            
            logger.info(f"Processing message for thread: {thread_id}")
            
            config = {"configurable": {"thread_id": thread_id}}
            user_message = HumanMessage(content=message)

            # Ejecutar la invocación asincrónica con configuración (checkpoint)
            result = await self.agent.ainvoke({"messages": [user_message]}, config)

            last_message = result["messages"][-1].content
            
            logger.info(f"Response generated for thread: {thread_id}")

            return {"response": last_message, "thread_id": thread_id}
            
        except Exception as e:
            logger.error(f"Error processing chat for thread {thread_id}: {str(e)}")
            raise

    async def chat_stream(self, message: str, thread_id: Optional[str] = None) -> AsyncGenerator[dict, None]:
        """
        Procesa un mensaje y devuelve la respuesta en streaming.
        
        Args:
            message: El mensaje del usuario
            thread_id: ID de sesión opcional
            
        Yields:
            dict con chunks de la respuesta
        """
        try:
            if not thread_id:
                thread_id = self.initialize_session()
            
            logger.info(f"Starting stream for thread: {thread_id}")
            
            config = {"configurable": {"thread_id": thread_id}}
            user_message = HumanMessage(content=message)

            # Streaming de la respuesta
            async for event in self.agent.astream_events(
                {"messages": [user_message]}, 
                config=config,
                version="v2"
            ):
                kind = event["event"]
                
                # Emitir chunks del LLM
                if kind == "on_chat_model_stream":
                    content = event["data"]["chunk"].content
                    if content:
                        yield {
                            "type": "content",
                            "data": content,
                            "thread_id": thread_id
                        }
                
                # Emitir llamadas a herramientas
                elif kind == "on_tool_start":
                    yield {
                        "type": "tool_start",
                        "data": event["name"],
                        "thread_id": thread_id
                    }
                    
            logger.info(f"Stream completed for thread: {thread_id}")
            
            # Enviar mensaje de finalización
            yield {
                "type": "end",
                "thread_id": thread_id
            }
            
        except Exception as e:
            logger.error(f"Error in streaming for thread {thread_id}: {str(e)}")
            yield {
                "type": "error",
                "data": str(e),
                "thread_id": thread_id
            }
    
