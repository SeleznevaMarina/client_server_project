import asyncio
import random
import datetime

SERVER_PORT = 8888
MIN_INTERVAL = 0.3
MAX_INTERVAL = 3
IGNORE_PROBABILITY = 0.1
KEEPALIVE_INTERVAL = 5

async def handle_client(reader, writer):
    client_id = len(CLIENTS) + 1
    CLIENTS.append(writer)
    print(f'Client {client_id} connected.')

    try:
        while True:
            data = await reader.readline()
            if not data:
                break
            message = data.decode().strip()
            await process_message(message, writer, client_id)
    except asyncio.CancelledError:
        pass
    finally:
        CLIENTS.remove(writer)
        print(f'Client {client_id} disconnected.')

async def process_message(message, writer, client_id):
    now = datetime.datetime.now()
    if random.random() < IGNORE_PROBABILITY:
        print(f'[{now}] Ignored message from Client {client_id}: {message}')
        return

    delay = random.uniform(0.1, 1)
    await asyncio.sleep(delay)
    response = f'[{RESPONSE_COUNT}] PONG ({message}) ({client_id})'
    writer.write(response.encode())
    await writer.drain()

    log_response(message, response)

async def send_keepalive():
    while True:
        await asyncio.sleep(KEEPALIVE_INTERVAL)
        now = datetime.datetime.now()
        for writer in CLIENTS:
            keepalive_message = f'[{RESPONSE_COUNT}] keepalive'
            writer.write(keepalive_message.encode())
            await writer.drain()
            log_response('', keepalive_message)

async def log_response(request, response):
    now = datetime.datetime.now()
    if response:
        log_message = f'{now.strftime("%Y-%m-%d")};{now.strftime("%H:%M:%S.%f")[:-3]};{request};{now.strftime("%H:%M:%S.%f")[:-3]};{response}'
    else:
        log_message = f'{now.strftime("%Y-%m-%d")};{now.strftime("%H:%M:%S.%f")[:-3]};{request};(проигнорировано);(проигнорировано)'
    with open('server.log', 'a') as f:
        f.write(log_message + '\n')

async def start_server():
    server = await asyncio.start_server(
        handle_client, 'localhost', SERVER_PORT)
    async with server:
        await server.serve_forever()

async def start_clients():
    for i in range(2):
        asyncio.create_task(run_client(i + 1))
        await asyncio.sleep(1)

async def run_client(client_id):
    while True:
        try:
            reader, writer = await asyncio.open_connection(
                'localhost', SERVER_PORT)
            ping_message = f'[{REQUEST_COUNT}] PING'
            writer.write(ping_message.encode())
            await writer.drain()
            response = await reader.readline()
            response = response.decode().strip()
            log_response(ping_message, response)
            await asyncio.sleep(random.uniform(0.3, 3))
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f'Client {client_id} error: {e}')
            break

RESPONSE_COUNT = 0
REQUEST_COUNT = 0
CLIENTS = []

async def main():
    server_task = asyncio.create_task(start_server())
    client_task = asyncio.create_task(start_clients())
    keepalive_task = asyncio.create_task(send_keepalive())

    await asyncio.sleep(300)

    server_task.cancel()
    client_task.cancel()
    keepalive_task.cancel()

    await asyncio.gather(server_task, client_task, keepalive_task, return_exceptions=True)

if __name__ == "__main__":
    asyncio.run(main())
