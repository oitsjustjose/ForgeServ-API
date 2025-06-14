"""
Author: Jose Stovall
Description: A WebSocket service which only pushes messages to clients when 
    server details change
"""

import json
import asyncio
from os import environ as env
from websockets.server import serve

from common import get_server_info

def __get():
    return json.dumps(get_server_info(all=True))

async def wait_for_change(ws):
    global cache
    data = __get()

    while data == cache:
        await asyncio.sleep(1)
        data = __get()

    cache = data
    await ws.send(data)

async def run(websocket):
    while True:
        # raises ConnectionClosed ex which breaks out of the loop.
        # https://websockets.readthedocs.io/en/stable/howto/patterns.html
        await wait_for_change(websocket)

async def setup():
    async with serve(run, "localhost", int(env["PORT"])):
        await asyncio.Future()

if __name__ == "__main__":
    # Used to store the last message and compare if there's any change
    cache = __get()
    asyncio.run(setup())
