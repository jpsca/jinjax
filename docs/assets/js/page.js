export function ready() {
  var links = document.querySelectorAll(".page__toc a");
  links.forEach(link => {
    link.addEventListener("click", function (event) {
      const pop = event.target.closest(".page__toc");
      if (pop) { pop.hidePopover(); }
    });
  });

  if (!window.scrollPositions) {
    window.scrollPositions = {};
  }
  window.addEventListener("turbo:before-cache", preserveScroll)
  window.addEventListener("turbo:before-render", restoreScroll)
  window.addEventListener("turbo:render", restoreScroll)
}

function preserveScroll () {
  document.querySelectorAll("[data-preserve-scroll]").forEach((element) => {
    scrollPositions[element.id] = element.scrollTop;
  })
}

function restoreScroll (event) {
  document.querySelectorAll("[data-preserve-scroll]").forEach((element) => {
    element.scrollTop = scrollPositions[element.id];
  })

  if (!event.detail.newBody) return
  // event.detail.newBody is the body element to be swapped in.
  // https://turbo.hotwired.dev/reference/events
  event.detail.newBody.querySelectorAll("[data-preserve-scroll]").forEach((element) => {
    element.scrollTop = scrollPositions[element.id];
  })
}
