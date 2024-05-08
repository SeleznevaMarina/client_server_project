import asyncio
import random
import datetime

SERVER_PORT = 8888
MIN_INTERVAL = 0.3
MAX_INTERVAL = 3
KEEPALIVE_INTERVAL = 5

async def run_client(client_id):
    try:
        REQUEST_COUNT = 0
        while True:
            try:
                reader, writer = await asyncio.open_connection(
                    'localhost', SERVER_PORT)
            except Exception as e:
                print(f'{datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]} Client {client_id} error: {e}')
                await asyncio.sleep(1)  
                continue
            
            print(f'{datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]} Client {client_id} connected.')

            try:
                while True:
                    ping_message = f'[{REQUEST_COUNT}] PING\n'
                    print(f'{datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]} Client {client_id} sent: {ping_message}')  
                    writer.write(ping_message.encode())
                    await writer.drain()
                    response = await asyncio.wait_for(reader.readline(), timeout=3)
                    if response:
                        response = response.decode().strip()
                        print(f'{datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]} - Client {client_id} received: {response}')  
                    else:
                        response = '(таймаут)'
                    await log_response(client_id, ping_message, response)
                    REQUEST_COUNT += 1
                    await asyncio.sleep(random.uniform(0.3, 3))
            except asyncio.CancelledError:
                raise
            except Exception as e:
                print(f'{datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]} Client {client_id} error: {e}')
            finally:
                writer.close()
                await writer.wait_closed()
                print(f'{datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]} Client {client_id} disconnected.')

    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f'{datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]} Client {client_id} error: {e}')

async def log_response(client_id, request, response=''):
    now = datetime.datetime.now()
    log_message = f'{now.strftime("%Y-%m-%d")};{now.strftime("%H:%M:%S.%f")[:-3]};{request};{now.strftime("%H:%M:%S.%f")[:-3]};{response}'
    with open(f'client/client{client_id}_log.txt', 'a') as f:
        f.write(log_message + '\n')
