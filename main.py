import asyncio
import multiprocessing
import time
from client.client import run_client
from server.server import run_server

def start_server():
    asyncio.run(run_server())

def start_client(client_id):
    asyncio.run(run_client(client_id))

if __name__ == "__main__":
    server_process = multiprocessing.Process(target=start_server)
    client1_process = multiprocessing.Process(target=start_client, args=(1,))
    client2_process = multiprocessing.Process(target=start_client, args=(2,))

    server_process.start()
    time.sleep(1)
    client1_process.start()
    client2_process.start()

    # Ограничение времени 5 минут
    time.sleep(300)

    # Завершение процессов
    server_process.terminate()
    client1_process.terminate()
    client2_process.terminate()
    server_process.join()
    client1_process.join()
    client2_process.join()
