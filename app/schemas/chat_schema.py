from typing import List, TypedDict
from langgraph.graph import MessagesState 

class AgentState(MessagesState):
    my_agent:str
