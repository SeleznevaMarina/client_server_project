import asyncio
import random
import datetime

SERVER_PORT = 8888
MIN_INTERVAL = 0.3
MAX_INTERVAL = 3
KEEPALIVE_INTERVAL = 5

async def handle_response(reader, writer):
    while True:
        data = await reader.readline()
        if not data:
            break
        message = data.decode().strip()
        log_response(message)

async def run_client(client_id):
    try:
        while True:
            reader, writer = await asyncio.open_connection(
                'localhost', SERVER_PORT)
            ping_message = f'[{REQUEST_COUNT}] PING'
            writer.write(ping_message.encode())
            await writer.drain()
            response = await asyncio.wait_for(reader.readline(), timeout=3)
            if response:
                response = response.decode().strip()
            else:
                response = '(таймаут)'
            log_response(client_id, ping_message, response)
            await asyncio.sleep(random.uniform(0.3, 3))
    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f'Client {client_id} error: {e}')

async def log_response(client_id, request, response=''):
    now = datetime.datetime.now()
    log_message = f'{now.strftime("%Y-%m-%d")};{now.strftime("%H:%M:%S.%f")[:-3]};{request};{now.strftime("%H:%M:%S.%f")[:-3]};{response}'
    with open(f'client{client_id}_log.txt', 'a') as f:
        f.write(log_message + '\n')

async def main():
    client1_task = asyncio.create_task(run_client(1))
    client2_task = asyncio.create_task(run_client(2))
    await client1_task
    await client2_task

if __name__ == "__main__":
    asyncio.run(main())
