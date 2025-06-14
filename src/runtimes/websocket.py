"""
@author: Jose Stovall | oitsjustjose
A dedicated websocket server for updating connected clients with
    the latest set of changes to the server list
"""

import asyncio
import json
from os import environ as env

import docker
from docker import DockerClient
from websockets.asyncio.server import ServerConnection, serve

from common import get_server_info


def __fetch(client: DockerClient):
    return json.dumps(get_server_info(client, all=True))


CLIENT = docker.from_env()
CACHE = __fetch(CLIENT)


async def __loop_infinitely(conn: ServerConnection):
    while True:
        # raises ConnectionClosed ex which breaks out of the loop.
        # https://websockets.readthedocs.io/en/stable/howto/patterns.html
        await __wait_for_change(conn)


async def __setup(host: str, port: int = 8008):
    async with serve(__loop_infinitely, host, port):
        await asyncio.Future()


async def __wait_for_change(conn: ServerConnection):
    global CACHE

    new = json.dumps(get_server_info(CLIENT, all=True))

    while new == CACHE:
        await asyncio.sleep(1)
        new = json.dumps(get_server_info(CLIENT, all=True))
    CACHE = new
    await conn.send(new)


def run():
    host = "0.0.0.0"
    port = int(env["PORT"]) if "PORT" in env else 8008

    print(f"WebSocket Server is now running on {host}:{port}")
    asyncio.run(__setup(host, port))
