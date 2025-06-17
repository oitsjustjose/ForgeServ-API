"""
Author: Jose Stovall
Description: A Flask API service for the running Minecraft server statuses

Run via Docker with either network mode = HOST, **OR** set the environment variable HOST_IP to the IP of your server
"""

import docker
from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware

from common import list_servers

app: FastAPI = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = docker.from_env()


@app.get("/")
def index(response: Response, all: bool = False, sort: str = ""):
    try:
        data = list_servers(client, all=all)
        if sort:
            data = sorted(data, key=lambda x: x[sort])
        response.status_code = status.HTTP_200_OK
        return data
    except KeyError:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": f"Failed to find key {sort}"}
