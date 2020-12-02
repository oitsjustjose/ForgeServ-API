window.addEventListener("DOMContentLoaded", (evt) => {
    window.onclick = (event) => {
        if (event.target.classList.contains("modal")) {
            let modal = event.target;
            modal.classList.remove("visible");
            modal.removeAttribute("active");
            document.body.classList.remove("modal-no-scroll");
        }
    };

    document.querySelectorAll(".modal .close").forEach((closeBtn) => {
        closeBtn.addEventListener('click', (evt) => {
            let modal = closeBtn.parentElement.parentElement;
            modal.classList.remove("visible");
            modal.removeAttribute("active");
            document.body.classList.remove("modal-no-scroll");
        });
    });

    document.querySelectorAll("[for-modal]").forEach((modalTrigerEl) => {
        modalTrigerEl.addEventListener('click', (evt) => {
            let modal = document.getElementById(modalTrigerEl.getAttribute("for-modal"));
            modal.classList.add("visible");
            modal.setAttribute("active", "");
            document.body.classList.add("modal-no-scroll");
        });
    });


    document.body.addEventListener('keydown', (evt) => {
        if (evt.key == "Escape") {
            let modal = document.querySelector(".modal[active]");
            modal.classList.remove("visible");
            modal.removeAttribute("active");
            document.body.classList.remove("modal-no-scroll");
        }
    });
});
