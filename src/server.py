import base64
import json
import re
from dataclasses import dataclass
from typing import List, Union

from ping import ServerPingResponse
from ping import ping as ping_server

SPECIAL_CHAR = "§"


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

    def asdict(self) -> dict:
        d = self.__dict__
        d["players"] = [x.__dict__ for x in self.players]
        return d

    @staticmethod
    def params_from_attrs(attrs: dict) -> Union[ServerConstructorParams, None]:
        """Builds the class from the container attrs passed in

        Args:
            attrs (dict): The container attributes for the given MC container
        """

        server_ping_info: Union[ServerPingResponse, None] = None

        # Try to ping server if it's running to get users online
        for binding in attrs["HostConfig"]["PortBindings"]:
            port, protocol = binding.split("/")
            # Realistically nothing we care about is on TCP...
            if protocol != "tcp":
                continue

            server_ping_info = ping_server("localhost", port=int(port))
            if server_ping_info is not None:
                break

        if server_ping_info is None:
            return None

        log_info = Server.parse_log_for_info(attrs["State"]["Health"]["Log"][-1]["Output"])
        players = [Player(name=pl.name, uuid=pl.id) for pl in server_ping_info.players]

        return ServerConstructorParams(
            health=attrs["State"]["Health"]["Status"],
            status=attrs["State"]["Status"],
            type=Server.get_server_type(attrs["Config"]["Env"]),
            version=log_info.version,
            icon=str(base64.b64encode(server_ping_info.icon).decode()) if server_ping_info.icon else None,
            motd=log_info.motd,
            name=attrs["Name"][1:],
            online=len(players),
            max=log_info.max,
            players=players,
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
