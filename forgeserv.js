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

    const resp = await fetch(`http://mcapi.us/server/status?ip=forgeserv.net&port=${port}`);
    const data = await resp.json();

    const card = document.createElement('div');
    card.className = 'card';

    const img = document.createElement('img');
    img.className ='blurred card-img-top';
    img.src = `/Resources/servers/${id}/cover.png`;

    const icn = document.createElement('img');
    icn.className = 'icn';
    icn.src = data.favicon ? data.favicon : '/Resources/default-icon.png';

    const title = document.createElement('h3');
    title.className = 'card-title';
    title.innerText = name;

    card.appendChild(img);
    card.appendChild(icn);
    card.appendChild(title);

    const cardText = document.createElement('div');
    cardText.className = 'card-text';

    const sts = document.createElement('h6');
    sts.innerText = `Server is ${data.online ? 'online' : 'offline'}`;
    sts.style.color = data.online ? '#7cb342' : '#ff4340';

    const cnt = document.createElement('p');
    cnt.innerText = `${data.players.now} / ${data.players.max} Players Online`;

    const ver = document.createElement('p');
    ver.innerText = `Minecraft Version ${data.server.name}`;


    cardText.appendChild(sts);
    cardText.appendChild(cnt);
    cardText.appendChild(ver);
    card.appendChild(cardText);

    if (hasPackVer) {
        const packVer = document.createElement('h4');
        packVer.innerText = `Modpack Version ${extractVersion(data.motd)}`;
        card.appendChild(packVer);
    }
    if (dynmapUrl) {
        const dynAnc = document.createElement('a');
        dynAnc.href = dynmapUrl;

        const dmap = document.createElement('b');
        dmap.innerText = `${name.substring(0, 1).toUpperCase() + name.slice(1)} Dynmap`;

        dynAnc.appendChild(dmap);
        card.appendChild(dynAnc);
    }

    return card;
};

const extractVersion = (motd) => {
    return motd.substring(motd.toLowerCase().indexOf('version') + 'version'.length).trim();
};


window.addEventListener('load', () => {
    update();
    document.body.classList.remove("loading");
    setInterval(() => {
        update();
    }, 30000);
});

