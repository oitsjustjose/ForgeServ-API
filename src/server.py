import base64
import re
from dataclasses import dataclass
from os import getenv
from typing import Any, List, Union

from docker.models.containers import Container

from ping import ServerPingResponse
from ping import ping as ping_server

SPECIAL_CHAR = "§"
DYNMAP_LABEL_KEY = "net.forgeserv.dynmap"


@dataclass
class LogDerivedInfo:
    version: str = ""
    max: int = 0
    motd: str = ""


@dataclass
class Player:
    name: str
    uuid: str


@dataclass
class ServerConstructorParams:
    health: str
    status: str
    type: str
    version: str
    icon: Union[str, None]
    motd: str
    name: str
    online: int
    max: int
    players: List[Player]
    dynmap: Union[str, None]


def ping_container_server(container: Container) -> Union[ServerPingResponse, None]:
    """Iterates through all Container:Host port binding pairs and attempts to ping the server

    Args:
        container (Container): The container whose port bindings to try to ping

    Returns:
        Union[ServerPingResponse, None]: The info derived from the Ping, if available, otherwise None (failure case)
    """

    # container.ports looks like {'25565/tcp': [{'HostIp': '0.0.0.0', 'HostPort': '25567'}, {'HostIp': '::', 'HostPort': '25567'}] }
    #  we only want the host host IP and host port, so we can skip that and just look at the values and ignore the
    #  "{port}/{tcp|udp}" part
    for ip_port_pairs in container.ports.values():
        for ip_port_pair in ip_port_pairs:
            try:
                port = int(ip_port_pair["HostPort"])
                return ping_server(getenv("HOST_IP", "localhost"), port=port)
            except ValueError:
                return None


def safe_get(d_in: dict, key: str) -> Any:
    """Attempts to get a heavily nested object in a k:v pair, safely and quickly
    Nested keys are to be split using a slash (/), so dict["State"]["Health"]["Status"]
    would mean that the key passed in would be "State/Health/Status"

    Args:
        d_in (dict): The dictionary to scan through
        key (str): The key formatted as documented above

    Returns:
        object: The dict value (can be anything) or None if we failed to find it
    """
    keys = key.split("/")
    subitem = d_in
    for k in keys:
        if k not in subitem:
            return None
        subitem = subitem[k]
    return subitem


class Server:
    def __init__(self, params: ServerConstructorParams):
        self.health: str = params.health
        self.status: str = params.status
        self.type: str = params.type
        self.version: str = params.version
        self.icon: Union[str, None] = params.icon
        self.motd: str = params.motd
        self.name: str = params.name
        self.online: int = params.online
        self.max: int = params.max
        self.players: List[Player] = params.players
        self.dynmap: Union[str, None] = params.dynmap

    def asdict(self) -> dict:
        d = self.__dict__
        d["players"] = [x.__dict__ for x in self.players]
        return d

    @staticmethod
    def from_container(container: Container):
        """Attempts to build out a server instance from a given container

        Args:
            container (Container): The container whose props should be analyzed

        Returns:
            Union[Server,None]: A server if parsing params was successful, None otherwise
        """

        ping_data = ping_container_server(container)
        if not ping_data:
            return None

        log_info = Server.parse_log_for_info(container.attrs["State"]["Health"]["Log"][-1]["Output"])
        players = [Player(name=pl.name, uuid=pl.id) for pl in ping_data.players]
        dynmap = container.labels[DYNMAP_LABEL_KEY] if DYNMAP_LABEL_KEY in container.labels else None

        return Server(
            ServerConstructorParams(
                health=str(safe_get(container.attrs, "State/Health/Status")),
                status=str(safe_get(container.attrs, "State/Status")),
                type=Server.get_server_type(list(safe_get(container.attrs, "Config/Env"))),
                version=log_info.version,
                icon=str(base64.b64encode(ping_data.icon).decode()) if ping_data.icon else None,
                motd=log_info.motd,
                name=container.name or container.id or "",
                online=len(players),
                max=log_info.max,
                players=players,
                dynmap=dynmap,
            )
        )

    @staticmethod
    def get_server_type(docker_environment: list) -> str:
        """
        Gets the type of MC Server currently hosted based on the Environment variables
        Arguments:
            env: List[str]
        Returns:
            (str) The type of server, or "Vanilla" if none can be detected.
        """
        for e in docker_environment:
            if e.startswith("TYPE="):
                tmp = e.replace("TYPE=", "")
                return tmp[0].upper() + tmp[1:].lower()

        return "Vanilla"

    @staticmethod
    def parse_log_for_info(logs: str) -> LogDerivedInfo:
        """
        Gets the Game Version, MOTD, Online and Max Count from the server's log string
        Arguments:
            log (str): the current log from this server
        Returns:
            (LogDerivedInfo): Info derived from the log lines.
        """

        def __cleanup_motd(motd: str) -> str:
            """Removes any color / format coding from a given MOTD"""
            if SPECIAL_CHAR not in motd:
                return motd
            start = motd.index(SPECIAL_CHAR)
            repl = motd[start : start + 2]
            return __cleanup_motd(motd.replace(repl, ""))

        # We only care about the right half of the data after the :
        _, logs = logs.split(" : ")
        # Find all keys for the log line (universally)
        keys: List[str] = re.findall("\w+(?=\=)", logs)
        ret = LogDerivedInfo()

        for idx, key in enumerate(keys):
            start = logs.index(key) + len(f"{key}=")
            end = len(logs) - 1
            if key != keys[-1]:  # If we're NOT on the last key in the array, bump up
                end = logs.index(keys[idx + 1])

            value = logs[start:end].strip()
            try:
                value = int(value)
            except ValueError:
                pass

            ret.__dict__[key] = value

        ret.motd = __cleanup_motd(ret.motd).replace('"', "").replace("'", "")
        return ret
