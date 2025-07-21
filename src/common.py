"""
Author: Jose Stovall
Description: Common utilities used to fetch current server statuses
"""

from typing import List

from docker import DockerClient
from docker.models.containers import Container

from server import Server


def list_servers(client: DockerClient, all: bool = False) -> List[dict]:
    """
    Distills the container data for all servers on the current host into a usable format
    Arguments:
        all (bool): whether to return *all* servers, or just the running one
    Returns:
        (List[Dict[str, any]]) A list of results from __extract_info
    """

    containers: List[Container] = list(
        filter(
            lambda x: "itzg/minecraft-server" in x.attrs["Config"]["Image"] and "net.forgeserv.hidden" not in x.labels,
            client.containers.list(all=all),
        )
    )

    ret = [Server.from_container(c) for c in containers]
    ret = list(filter(lambda x: x is not None, ret))
    return [x.asdict() for x in ret]  # type: ignore
