from langchain_core.messages import HumanMessage
from ..agent.my_agent import create_product_agent
import uuid

class ChatService:
    def __init__(self):
        self.agent = create_product_agent()
        self.thread_id = None

    def initialize_session(self):
        self.thread_id = str(uuid.uuid4())
        return self.thread_id

    async def chat(self, message: str, thread_id: str = None) -> dict:
        # Si no hay thread_id recibido, crear uno nuevo o usar el existente
        if thread_id:
            self.thread_id = thread_id
        elif not self.thread_id:
            self.initialize_session()

        config = {"configurable": {"thread_id": self.thread_id}}

        user_message = HumanMessage(content=message)

        # Ejecutar la invocación asincrónica con configuración (checkpoint)
        result = await self.agent.ainvoke({"messages": [user_message]}, config)

        last_message = result["messages"][-1].content

        return {"response": last_message, "thread_id": self.thread_id}
    
