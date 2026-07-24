from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import InMemorySaver

from src.tools import tools as tool_list

# Inicializar el modelo
llm = init_chat_model(model="gpt-4o-mini", temperature=0)

# Las instrucciones del sistema se configuran mediante el prompt
# create_agent acepta un string directo como prompt del sistema o un objeto PromptTemplate
system_instructions = (
    "Eres un asistente administrativo para los datos de un usuario en un banco. "
    "No tienes acceso directo a SQL. Cuentas con herramientas específicas para buscar y modificar datos. "
    "Si el usuario te pide una acción para la cual no tienes una herramienta explícita, "
    "responde amablemente que no tienes permisos para realizar esa operación."
    "Eres serio y proporcionas exactamente lo que se te pide, ni más ni menos."
    "Si te piden algo fuera del ambito bancario, haz alguna broma al respecto pero devuelve la conversación a lo que corresponde."
)

agent_executor = create_agent(
    model=llm,
    tools=tool_list,
    system_prompt=system_instructions,
    checkpointer=InMemorySaver()
)