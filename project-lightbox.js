const diagramTrigger = document.querySelector(".diagram-enlarge");
const diagramLightbox = document.querySelector("#uml-diagram-lightbox");
const lightboxClose = diagramLightbox?.querySelector(".lightbox-close");

if (diagramTrigger && diagramLightbox && lightboxClose) {
  diagramTrigger.addEventListener("click", () => {
    diagramLightbox.showModal();
  });

  lightboxClose.addEventListener("click", () => {
    diagramLightbox.close();
  });

  diagramLightbox.addEventListener("click", (event) => {
    if (event.target === diagramLightbox) {
      diagramLightbox.close();
    }
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && diagramLightbox.open) {
      event.preventDefault();
      diagramLightbox.close();
    }
  });

  diagramLightbox.addEventListener("close", () => {
    diagramTrigger.focus();
  });
}
