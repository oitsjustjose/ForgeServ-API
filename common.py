"""
Author: Jose Stovall
Description: Common utilities used to fetch current server statuses
"""

import docker
import base64
import json
import requests
from ping import ping as ping_server

client = docker.from_env()

def __parse_log(log: str) -> dict:
    """
    Gets the Game Version, MOTD, Online and Max Count from the server's log string
    Arguments:
        log (str): the current log from this server
    Returns:
        Dict[str, str] with fields:
            "version": str
            "online": str
            "max": str
            "motd": str
    """

    FORMAT_CODES = ["§0", "§1", "§2", "§3", "§4", "§5", "§6", "§7", "§8", "§9", "§a", "§b", "§c", "§d", "§e", "§f", "§o", "§l", "§m", "§n", "§o", "§r"]
    KEYS = ["version", "online", "max", "motd"]
    log = log.replace("localhost:25565 : ", "")
    for cd in FORMAT_CODES:
        log = log.replace(cd, "")

    ret = {}
    for idx, key in enumerate(KEYS):
        start = log.find(key) + len(key)
        end = 0
        try:
            end = log.index(KEYS[idx+1])
        except IndexError:
            end = len(log)
        except ValueError:
            ret[key] = ""

        value = log[start:end].strip().replace("=", "").replace("'", "")
        ret[key] = value
    return ret

def __get_type(env: list) -> str:
    """
    Gets the type of MC Server currently hosted based on the Environment variables
    Arguments:
        env: List[str]
    Returns:
        (str) The type of server, or "Vanilla" if none can be detected.
    """
    for e in env:
        if e.startswith("TYPE="):
            tmp = e.replace("TYPE=", "")
            return tmp[0].upper() + tmp[1:].lower()

    return "Vanilla"


def __extract_info(attrs: dict) -> dict:
    """
    Retrieves only valuable fields from the a Minecraft Server's container attributes
    Arguments:
        attrs (Dict[str, any]): The container's attributes
    Returns:
        (Dict[str, any]) with fields:
            "name": str
            "type": str
            "status": str
            "health": str
            "players": List[Dict[str, str]], (A mapping of username & UUID)
            "icon": str (A base64 representation of the server's 'server-icon.png')
            "dynmap": Union[str, None] (None if the server has no dynmap associated with it)
            "version": str
            "online": str
            "max": str
            "motd": str
    """
    players = []
    icon = None
    dynmap = None

    # Try to ping server if it's running to get users online
    if attrs["State"]["Status"] == "running":
        for key in attrs["HostConfig"]["PortBindings"]:
            for binding in attrs["HostConfig"]["PortBindings"][key]:
                try:
                    data = ping_server("localhost", port=int(binding["HostPort"]))
                    if not data: # Hmm, it's a minecraft container but not a minecraft server port? might be dynmap:
                        # dynmap = find_dynmap(int(binding["HostPort"]))
                        host_port = int(binding["HostPort"])
                        request = requests.get(f"http://172.16.1.4:7070/{host_port}")
                        if request.ok:
                            dynmap = request.text
                        continue
                    icon = data.icon
                    players += [{"name": x.name, "uuid": x.id} for x in data.players]
                except Exception as e:
                    print(e)
                    pass

    info = {
        "name": attrs["Name"][1:],
        "type": __get_type(attrs["Config"]["Env"]),
        "status": attrs["State"]["Status"],
        "health": attrs["State"]["Health"]["Status"],
        "players": players,
        "icon": str(base64.b64encode(icon).decode()) if icon else None,
        "dynmap": dynmap
    }

    info.update(__parse_log(attrs["State"]["Health"]["Log"][-1]["Output"]))
    return info

def get_server_info(all: bool = False):
    """
    Distills the container data for all servers on the current host into a usable format
    Arguments:
        all (bool): whether to return *all* servers, or just the running one
    Returns:
        (List[Dict[str, any]]) A list of results from __extract_info
    """
    containers = list(
        filter(
            lambda x: "itzg/minecraft-server" in x.attrs['Config']['Image'] and "net.forgeserv.hide" not in x.labels,
            client.containers.list(all=all)
        )
    )

    ret = [__extract_info(c.attrs) for c in containers]
    ret = list(filter(lambda x: x is not None, ret))
    return ret
