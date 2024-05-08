import asyncio
import random
import datetime

SERVER_PORT = 8888
MIN_INTERVAL = 0.3
MAX_INTERVAL = 3
IGNORE_PROBABILITY = 0.1
KEEPALIVE_INTERVAL = 5

RESPONSE_COUNT = 0
CLIENTS = []

async def handle_client(reader, writer):
    global RESPONSE_COUNT
    client_id = len(CLIENTS) + 1
    CLIENTS.append(writer)
    print(f'{datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]} Server: Client {client_id} connected.')

    try:
        while True:
            data = await reader.readline()
            if not data:
                print('no data')
                break
            message = data.decode().strip()
            print(f'{datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]} Server received from Client {client_id}: {message}')  
            await process_message(message, writer, client_id)
    except asyncio.CancelledError:
        pass
    except Exception as inst:
        print(inst)
        pass
    finally:
        CLIENTS.remove(writer)
        print(f'{datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]} Client {client_id} disconnected.')

async def process_message(message, writer, client_id):
    global RESPONSE_COUNT
    now = datetime.datetime.now()
    if random.random() < IGNORE_PROBABILITY:
        print(f'[{now}] Ignored message from Client {client_id}: {message}')
        return

    delay = random.uniform(0.1, 1)
    await asyncio.sleep(delay)
    response = f'[{RESPONSE_COUNT}] PONG ({message}) ({client_id}\n)'
    print(f'{datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]} Server sent to Client {client_id}: {response}')  
    writer.write(response.encode())
    await writer.drain()

    await log_response(message, response)
    RESPONSE_COUNT += 1

async def send_keepalive():
    while True:
        await asyncio.sleep(KEEPALIVE_INTERVAL)
        for writer in CLIENTS:
            keepalive_message = f'[{RESPONSE_COUNT}] keepalive'
            writer.write(keepalive_message.encode())
            await writer.drain()
            await log_response('', keepalive_message)

async def log_response(request, response):
    now = datetime.datetime.now()
    if response:
        log_message = f'{now.strftime("%Y-%m-%d")};{now.strftime("%H:%M:%S.%f")[:-3]};{request};{now.strftime("%H:%M:%S.%f")[:-3]};{response}'
    else:
        log_message = f'{now.strftime("%Y-%m-%d")};{now.strftime("%H:%M:%S.%f")[:-3]};{request};(проигнорировано);(проигнорировано)'
    with open('server/server.log', 'a') as f:
        f.write(log_message + '\n')

async def run_server():
    server = await asyncio.start_server(
        handle_client, 'localhost', SERVER_PORT)
    async with server:
        await asyncio.gather(server.serve_forever(), send_keepalive())
