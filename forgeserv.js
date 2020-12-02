const update = async () => {
    const resp = await fetch('/servers.json');
    const data = await resp.json();
    const serverElements = document.querySelector('#servers');

    const elements = [];

    /* Generate the elements before updating the renderer */
    for (const server of data.servers) {
        elements.push(await renderServer(server));
    }

    serverElements.innerHTML = '';
    for (const el of elements) {
        serverElements.appendChild(el);
    }
};

const renderServer = async (server) => {
    const { name, id, port, hasPackVer, dynmapUrl } = server;

    const resp = await fetch(`https://mcapi.us/server/status?ip=forgeserv.net&port=${port}`);
    const data = await resp.json();

    const card = document.createElement('div');
    card.className = 'card';

    /* BEGIN CARD COVER */
    const cardCover = document.createElement('div');
    cardCover.className = 'card-cover';

    const cardImg = document.createElement('img');
    cardImg.className = 'blurred';
    cardImg.src = `/Resources/${id}/cover.png`;

    const cardIcn = document.createElement('img');
    cardIcn.className = 'icon image';
    cardIcn.src = data.favicon ? data.favicon : '/Resources/default-icon.png';

    const serverName = document.createElement('h3');
    serverName.innerText = name;
    serverName.className = 'outline-text';

    cardCover.appendChild(cardImg);
    cardCover.appendChild(cardIcn);
    cardCover.appendChild(serverName);
    /* END CARD COVER */

    /* BEGIN CARD BOTTOM */
    const serverStatus = document.createElement('h3');
    serverStatus.innerText = `Server is ${data.online ? 'online' : 'offline'}`;
    serverStatus.style.color = data.online ? '#7cb342' : '#ff4340';

    const playerCount = document.createElement('h4');
    playerCount.innerText = `${data.players.now} / ${data.players.max} Players Online`;

    const version = document.createElement('h4');
    version.innerText = `Minecraft Version ${data.server.name}`;

    card.appendChild(cardCover);
    card.appendChild(serverStatus);
    card.appendChild(playerCount);
    card.appendChild(version);

    if (hasPackVer) {
        const packVer = document.createElement('h4');
        packVer.innerText = `Modpack Version ${extractVersion(data.motd)}`;
        card.appendChild(packVer);
    } else if (dynmapUrl) {
        const dynmapAnchor = document.createElement('a');
        dynmapAnchor.href = dynmapUrl;

        const dynmap = document.createElement('h4');
        dynmap.innerText = `${name.substring(0, 1).toUpperCase() + name.slice(1)} Dynmap`;

        dynmapAnchor.appendChild(dynmap);
        card.appendChild(dynmapAnchor);
    }
    /* END CARD BOTTOM */

    return card;
};

const extractVersion = (motd) => {
    return motd.substring(motd.toLowerCase().indexOf('version') + 'version'.length).trim();
};


window.addEventListener('load', () => {
    update();
    setInterval(() => {
        update();
    }, 30000);
});

