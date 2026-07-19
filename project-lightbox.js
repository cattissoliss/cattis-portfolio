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

const revealItems = document.querySelectorAll("[data-reveal]");

if (revealItems.length && "IntersectionObserver" in window) {
  document.documentElement.classList.add("has-reveal");

  const revealObserver = new IntersectionObserver(
    (entries, observer) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.12 }
  );

  revealItems.forEach((item) => revealObserver.observe(item));
}
