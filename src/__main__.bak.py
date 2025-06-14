"""
Author: Jose Stovall
Description: A Flask API service for the running Minecraft server statuses
"""

from os import environ as env


def main() -> None:
    host_method = env["METHOD"].lower()
    if host_method == "rest":
        from runtimes import rest

        rest.run()
    elif host_method == "websocket":
        from runtimes import websocket

        websocket.run()
    else:
        raise Exception(f"Unsupported 'METHOD' environment variable Currently set to {host_method}. Must be either 'rest' or 'websocket', and CANNOT be empty!")


if __name__ == "__main__":
    main()
