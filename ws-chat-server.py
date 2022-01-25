import websockets
import click
import asyncio
import logging
import os

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(os.path.basename(__file__))
msg_queue = None
running = True
clients = []
tasks = []

async def start(port):
    stop = asyncio.Future()
    create_protocol = websockets.basic_auth_protocol_factory(
        realm="dev server",
        credentials=("user", "needapass")
    )

    #init broadcast task
    b_task = asyncio.create_task(broadcast_task())
    tasks.append(b_task)
    cleanup_task = asyncio.create_task(cleanup_clients())
    tasks.append(cleanup_task)
    asyncio.create_task(monitor_tasks())
    async with websockets.serve(ws_handler, port=port, create_protocol=create_protocol) as svr:
        await stop
    
async def monitor_tasks():
    while running:
        await asyncio.sleep(1)
        for t in tasks:
            if t.done():
                try:
                    await t
                except:
                    log.error('task error')

async def cleanup_clients():
    while running:
        await asyncio.sleep(1)
        # log.debug("check clients status")
        to_be_removed = []
        for c in clients:
            # log.debug("client[%s] status [%s]", c.id, c.state)
            if c.state == websockets.connection.State.CLOSED:
                to_be_removed.append(c)
        for c in to_be_removed:
            clients.remove(c)
            log.info("remove client[%s]", c.id)


async def broadcast_task():
    global msg_queue
    msg_queue = asyncio.Queue()
    while running:
        (client, msg) = await msg_queue.get()
        log.debug("new msg[%s] from [%s]", msg, client.id)
        await broadcast(msg, client)

async def broadcast(msg, client):
    for c in clients:
        log.debug("send msg[%s] -> client[%s]", msg, c.id)
        await send_msg(c, msg)

async def send_msg(c, msg):
    if c is not None:
        try:
            await c.send(msg)
        except:
            log.error('send msg fail')

async def ws_handler(ws):
    log.info("new client %s", ws.id)
    clients.append(ws)
    async for msg in ws:
        log.info('recv: %s', msg)
        await msg_queue.put((ws, msg))


@click.command()
@click.option('--port', default=9000, help='server port')
def main(port):
    asyncio.run(start(port))

if __name__ == '__main__':
    main()