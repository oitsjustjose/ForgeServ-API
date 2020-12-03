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

    // Init all tooltips to be bootstrappy bois
    [].slice.call(document.querySelectorAll('[data-toggle="tooltip"]'))
        .map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
};

const renderServer = async (server) => {
    const { name, id, port, hasPackVer, dynmapUrl } = server;

    const resp = await fetch(`https://mcapi.us/server/status?ip=forgeserv.net&port=${port}`);
    const data = await resp.json();

    const card = document.createElement('div');
    card.className = 'card';

    if (dynmapUrl) {
        card.addEventListener('click', () => {
            window.open(dynmapUrl, "_blank");
        });
        card.setAttribute("data-toggle", "tooltip");
        card.setAttribute("data-placement", "top");
        card.setAttribute("title", "Click to View Dynmap");
    } else {
        card.setAttribute("data-toggle", "tooltip");
        card.setAttribute("data-placement", "top");
        card.setAttribute("title", "No Dynmap for this Server 😭");
    }

    const img = document.createElement('img');
    img.className = 'card-img-top';
    img.src = `/Resources/servers/${id}/cover.png`;

    const icn = document.createElement('img');
    icn.className = 'icn';
    icn.src = data.favicon ? data.favicon : '/Resources/default-icon.png';

    card.appendChild(img);
    card.appendChild(icn);

    const container = document.createElement('p');
    container.className = 'card-body';


    const title = document.createElement('h4');
    title.className = 'card-title mb-3';
    title.innerText = `${name}: (${data.online ? 'Online' : 'Offline'})`;
    title.style.color = data.online ? '#7cb342' : '#ff4340';
    container.appendChild(title);

    const ver = document.createElement('h5');
    ver.innerText = `Server Running ${data.server.name}`;

    const cnt = document.createElement('h6');
    cnt.innerText = `${data.players.now}/${data.players.max} Players Online`;

    if (hasPackVer) {
        const packVer = document.createElement('h5');
        packVer.innerText = `Modpack Version ${extractVersion(data.motd)}`;
        container.appendChild(packVer);
    }

    container.appendChild(ver);
    container.appendChild(cnt);
    card.appendChild(container);

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

