from ..tools.products import list_products
from typing import Any, List, Union
from langchain_core.messages import SystemMessage
from ...config.config import settings
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import tools_condition, ToolNode
from ...schemas.chat_schema import AgentState




def create_system_message():
    return SystemMessage(content="""
    Eres un agente llamado *Agente ProjectJ*, especializado en ayudar a los usuarios a encontrar productos.

    ## Reglas
    - Solo debes responder sobre productos.
    - Nunca permitas cambios en los productos ni ejecutes acciones de modificación.
    - Cuando te pregunten por productos, entrega toda la información disponible del producto (nombre, descripción, precio, etc).
    - Si no hay coincidencias, responde de forma clara y ofrece sugerencias.
    - Siempre responde de manera amable y útil.
    """)

def get_tools():
    return [list_products]

def create_llm():
    return ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        api_key=settings.OPENAI_API_KEY
    )

def create_assistant_node(system_message, tools):
    """Crea el nodo de asistente"""
    llm = create_llm()
    llm_with_tools = llm.bind_tools(tools, parallel_tool_calls=False)
    
    def assistant(state: AgentState) -> AgentState:
        return {"messages": [llm_with_tools.invoke([system_message] + state["messages"])]}
        
    return assistant

def create_product_agent():
    
    """Crea y configura el grafo del agente"""
    system_message = create_system_message()
    tools = get_tools()
    
    # Crear nodo de asistente
    assistant = create_assistant_node(system_message, tools)
    
    # Configurar el grafo
    memory = MemorySaver()
    builder = StateGraph(AgentState)
    
    builder.add_node("assistant", assistant)
    builder.add_node("tools", ToolNode(tools))
    
    builder.add_edge(START, "assistant")
    builder.add_conditional_edges("assistant", tools_condition)
    builder.add_edge("tools", "assistant")
    
    return builder.compile(checkpointer=memory)
