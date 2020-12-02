/**
 * @author oitsjustjose | https://github.com/oitsjustjose | oitsjustjose.com
 * Handles all things in regards to theming
 */

let themes = {
    "dark": "/Libraries/css/dark.css",
    "moonlight": "/Libraries/css/moonlight.css",
    "light": "/Libraries/css/light.css"
};

let mode = "dark";

const css = document.getElementById("themekit");

const updateIcon = () => {
    document.querySelectorAll(".theme-toggle").forEach((icon) => {
        if (mode == "dark") {
            icon.innerHTML = `<i class="fas fa-moon"></i>`;
        } else if (mode == "moonlight") {
            icon.innerHTML = `<i class="fas fa-sun"></i>`;
        } else {
            icon.innerHTML = `<i class="fas fa-adjust"></i>`;
        }
    });
};

const toggle = () => {
    if (mode == "dark") {
        window.localStorage.setItem("theme", "moonlight");
        mode = "moonlight";
    } else if (mode == "moonlight") {
        window.localStorage.setItem("theme", "light");
        mode = "light";
    } else {
        window.localStorage.setItem("theme", "dark");
        mode = "dark";
    }
    css.href = themes[mode];
    updateIcon();
};


window.addEventListener("DOMContentLoaded", (evt) => {
    // Bootstrap the click event listener
    document.querySelectorAll(".theme-toggle").forEach((icon) => {
        icon.addEventListener("click", () => {
            toggle();
        });
    });

    if (window.localStorage.getItem("theme") === null) {
        // Match with system dark mode
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            window.localStorage.setItem("theme", "dark");
        }
        // Match with system light mode
        else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
            window.localStorage.setItem("theme", "light");
        }
        // Literally choose the middle option 
        else {
            window.localStorage.setItem("theme", "moonlight");
        }
    }

    mode = window.localStorage.getItem("theme");
    css.href = themes[mode];
    updateIcon();
});