import asyncio
import websockets
import click

async def start(uri):
    ws =  await websockets.connect(uri)
    await ws.send('hello')

    async for msg in ws:
        print(msg)
        break

@click.command()
@click.argument("uri")
def main(uri):
    ''' connect to uri'''
    asyncio.run(start(uri))

if __name__ == '__main__':
    main()
