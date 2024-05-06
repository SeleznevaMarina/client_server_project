import asyncio
from server.server import start_server, start_clients

async def main():
    server_task = asyncio.create_task(start_server())
    client_task = asyncio.create_task(start_clients())

    await asyncio.sleep(300)

    server_task.cancel()
    client_task.cancel()

    await asyncio.gather(server_task, client_task, return_exceptions=True)

if __name__ == "__main__":
    asyncio.run(main())
