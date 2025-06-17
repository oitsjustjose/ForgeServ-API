"""
Author: Jose Stovall
Description: A Flask API service for the running Minecraft server statuses
Architecture:

Python App that loops infinitely, pushing the correct Pixlet state to the TidByt
Changes come in via WebAPI so we can make a lightweight desktop client and leave the work to the RasPi
Also allows the TidByt to still have forgeserv.net data without needing to be stood up
"""

import logging

import docker
from fastapi import FastAPI, Response, status

from common import list_servers

app: FastAPI = FastAPI()
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
