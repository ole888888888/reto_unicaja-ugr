import asyncio

from src.agent import agent_executor


async def memory_test():
    config={"configurable": {
        "thread_id": "15"
        }
    }

    print("Mensaje 1:")
    async for chunk, metadata in agent_executor.astream(
        input={"messages": [{"role": "user", "content": "Necesito revisar la transacción TX-9988."}]},
        config=config,
        stream_mode="messages"
    ):
        if chunk.content:
            print (f"{chunk.content}", end="", flush=True)

    print("\nMensaje 2:")
    async for chunk, metadata in agent_executor.astream(
        input={"messages": [{"role": "user", "content": "¿Cuál era el código de transacción que te acabo de dar?"}]},
        config=config,
        stream_mode="messages"
    ):
        if chunk.content:
            print(f"{chunk.content}", end="", flush=True)
    print("\n")

if __name__ == "__main__":
    asyncio.run(memory_test())