"""
Author: Jose Stovall
Description: A Flask API service for the running Minecraft server statuses
"""

import json
from os import environ as env

from flask import Flask, jsonify, request
import asyncio
from flask_cors import CORS
from websockets.asyncio.server import serve, ServerConnection

from common import list_servers
import docker
from docker import DockerClient

from threading import Thread


class RestServer:
    def __init__(self, docker_client: DockerClient):
        self._app = Flask("RestAPI")
        self._app.add_url_rule("/", view_func=self.index)
        self._client = docker_client
        CORS(self._app)

    def index(self):
        try:
            data = list_servers(self._client, all=bool(request.args.get("all")))

            if request.args.get("sort"):
                data = sorted(data, key=lambda x: x[request.args.get("sort")])

            resp = jsonify(data)
            resp.status_code = 200
            return resp
        except KeyError as e:
            resp = jsonify({"error": f"Failed to find key {str(e)}"})
            resp.status_code = 422
            return resp

    def run(self, **kwargs):
        print(f"Rest Server is now running on {kwargs['host']}:{kwargs['port']}")
        self._app.run(**kwargs)


class WebSocketServer:
    def __init__(self, docker_client: DockerClient):
        self._client = docker_client
        self.cache = json.dumps(list_servers(self._client, all=True))

    async def __loop_infinitely(self, conn: ServerConnection):
        while True:
            # raises ConnectionClosed ex which breaks out of the loop.
            # https://websockets.readthedocs.io/en/stable/howto/patterns.html
            await self.__wait_for_change(conn)

    async def __setup(self, host: str, port: int = 8008):
        async with serve(self.__loop_infinitely, host, port):
            await asyncio.Future()

    async def __wait_for_change(self, conn: ServerConnection):
        new = json.dumps(list_servers(self._client, all=True))

        while new == self.cache:
            await asyncio.sleep(1)
            new = json.dumps(list_servers(self._client, all=True))
        self.cache = new
        await conn.send(new)

    def run(self, host: str, port: int):
        print(f"WebSocket Server is now running on {host}:{port}")
        asyncio.run(self.__setup(host, port))


def main() -> None:
    client = docker.from_env()

    wss = WebSocketServer(client)
    wss_thread = Thread(
        daemon=True,
        target=wss.run,
        kwargs={
            "host": "0.0.0.0",
            "port": int(env["WS_PORT"]) if "WS_PORT" in env else 8008,
        },
    )

    wss_thread.start()
    RestServer(client).run(host="0.0.0.0", port=int(env["REST_PORT"]) if "REST_PORT" in env else 9090)
    wss_thread.join()


if __name__ == "__main__":
    main()
