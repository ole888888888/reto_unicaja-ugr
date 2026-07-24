import subprocess

from langchain_core.messages import AIMessageChunk

from src.agent import agent_executor

COLOR_USUARIO = "\033[34m"        # Azul normal
COLOR_USUARIO_SUB = "\033[4;34m"  # Azul SUBRAYADO
COLOR_AGENTE = "\033[33m"         # Amarillo/Verde normal
COLOR_AGENTE_SUB = "\033[4;33m"   # Amarillo/Verde SUBRAYADO
COLOR_RESET = "\033[0m"           # Resetear todo

if __name__ == "__main__":
    subprocess.run("clear")
    print("  ____        _        _                         _                    _  ") 
    print(" |  _ \\  __ _| |_ __ _| |__   __ _ ___  ___     / \\   __ _  ___ _ __ | |_ ")
    print(" | | | |/ _` | __/ _` | '_ \\ / _` / __|/ _ \\   / _ \\ / _` |/ _ \\ '_ \\| __|")
    print(" | |_| | (_| | || (_| | |_) | (_| \\__ \\  __/  / ___ \\ (_| |  __/ | | | |_ ")
    print(" |____/ \\__,_|\\__\\__,_|_.__/ \\__,_|___/\\___| /_/   \\_\\__, |\\___|_| |_|\\__|")
    print("                                                     |___/                \n\n\n")
    
    # Configuramos el identificador único para mantener el hilo de la conversación
    config = {"configurable": {
        "thread_id": "0001",
        "user_id": 1
        }
    }
    
    while True:
        pregunta = input(f"{COLOR_USUARIO_SUB}Usuario:{COLOR_RESET}{COLOR_USUARIO} ")
        if pregunta.lower() in ["salir", "exit", "quit"]:
            print("Saliendo del agente. ¡Hasta luego!")
            break
        
        output_stream = agent_executor.stream(
            {"messages":[{"role":"user","content":pregunta}]},
            config=config,
            stream_mode="messages"
        )

        agente_empezo = False

        for chunk,metadata in output_stream:
            if not agente_empezo:
                print(f"{COLOR_AGENTE_SUB}\nAgente:{COLOR_RESET} ", end="")
                agente_empezo = True
            if isinstance(chunk,AIMessageChunk) and chunk.content:
                if isinstance(chunk.content, str):
                    print(COLOR_AGENTE+chunk.content,end="",flush=True)
        print("\n")
