"""
Author: Jose Stovall
Description: Common utilities used to fetch current server statuses
"""

from typing import List, Union

from docker import DockerClient

from server import Server


def list_servers(client: DockerClient, all: bool = False) -> List[dict]:
    """
    Distills the container data for all servers on the current host into a usable format
    Arguments:
        all (bool): whether to return *all* servers, or just the running one
    Returns:
        (List[Dict[str, any]]) A list of results from __extract_info
    """

    def __parse(attrs: dict) -> Union[Server, None]:
        """
        Retrieves only valuable fields from the a Minecraft Server's container attributes
        Arguments:
            attrs (Dict[str, any]): The container's attributes
        Returns:
            (Server): The server parsed out from the container's attributes
        """
        params = Server.params_from_attrs(attrs)
        return Server(params) if params else None

    containers = list(
        filter(
            lambda x: "itzg/minecraft-server" in x.attrs["Config"]["Image"] and "net.forgeserv.hide" not in x.labels,
            client.containers.list(all=all),
        )
    )

    ret = [__parse(c.attrs) for c in containers]
    ret = list(filter(lambda x: x is not None, ret))
    return [x.asdict() for x in ret]  # type: ignore
