/**
 * Uses ZERO Jquery!!
 */

let menuOpen = false;

const toggleSubMenu = (el) => {

    let icon = el.querySelector("i.fa");
    let isOpen = icon.hasAttribute("submenuOpen") ? parseInt(icon.getAttribute("submenuOpen")) : 0;


    document.querySelectorAll(`[for=${el.getAttribute("from")}]`).forEach((elSearched) => {
        if (isOpen == 1) {
            elSearched.classList.remove("visible");
        } else {
            elSearched.classList.add("visible");
        }
    });

    if (isOpen == 1) {
        icon.style.transition = "transform ease-in-out 250ms";
        icon.style.transform = "rotate(0deg)";
        icon.setAttribute("submenuOpen", 0);
    } else { // Not open..
        icon.style.transition = "transform ease-in-out 250ms";
        icon.style.transform = "rotate(90deg)";
        icon.setAttribute("submenuOpen", 1);
    }
};

const toggleMenu = () => {
    let menu = document.querySelector(".mobile-menu");
    menuOpen = !menuOpen;

    if (menuOpen) {
        menu.classList.add("visible");
        document.body.classList.add("no-scroll");
    } else {
        menu.classList.remove("visible");
        document.body.classList.remove("no-scroll");
    }
};

window.addEventListener("DOMContentLoaded", (evt) => {
    document.querySelectorAll(".compact.submenu.item").forEach((el) => {
        let id = `subMenu_${new Date().getMilliseconds()}`;
        el.setAttribute("from", id);

        let subMenuItems = [];

        el.querySelectorAll(".compact.sub.item").forEach((child) => {
            subMenuItems.push(child);
        });

        subMenuItems.reverse();

        subMenuItems.forEach((child) => {
            child.setAttribute("for", id);
            el.parentElement.insertBefore(child, el.nextSibling);
        });
    });


    // Add .active to clicked on menus
    document.querySelectorAll(".dropdown.item").forEach((dropdown) => {
        dropdown.addEventListener("click", () => {
            if (dropdown.classList.contains("active")) {
                dropdown.classList.remove("active");
            } else {
                dropdown.classList.add("active");
            }
        });

        dropdown.addEventListener("mouseout", () => {
            if (dropdown.classList.contains("active")) {
                dropdown.classList.remove("active");
            }
        });
    });
});