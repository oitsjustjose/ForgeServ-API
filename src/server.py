from dataclasses import dataclass
from typing import Union, List


@dataclass
class Player:
    pass


@dataclass
class Server:
    dynmap: Union[str, None]
    health: str
    icon: str

    motd: str
    name: str

    online: int
    max: int
    players: List[Player]

    status: str
    type: str
    version: str
