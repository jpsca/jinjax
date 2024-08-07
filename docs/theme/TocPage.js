import { on } from "./jxui.js";

const ACTIVE = "active";
const SEL_BACKTOTOP = ".cd-back-to-top"
const SEL_PAGETOC = ".cd-toc-page"
const SEL_TARGET = `${SEL_PAGETOC} a`;
const SEL_ACTIVE = `${SEL_TARGET}.${ACTIVE}`;
const SEL_PAGE = "#main.page";
const SEL_SECTIONS = `${SEL_PAGE} section[id]`;
const DESKTOP_THRESHOLD = 1024;

on("click", SEL_TARGET, handleClick);
on("click", SEL_BACKTOTOP, backToTop);

function handleClick(event, target) {
  removeHighlight();
  setTimeout(function () { updateHighlight(target) }, 10);
}

function updateHighlight (elem) {
  if (window.innerWidth > DESKTOP_THRESHOLD && !elem?.classList.contains(ACTIVE)) {
    removeHighlight();
    if (!elem) return;
    elem.classList.add(ACTIVE);
  }
}

function removeHighlight () {
  document.querySelectorAll(SEL_ACTIVE).forEach(function (node) {
    node.classList.remove(ACTIVE);
  });
}

function resetNavPosition () {
  var pagetoc = document.querySelector(SEL_TOC);
  pagetoc?.scroll({ top: 0 });
}

export function backToTop () {
  window.scrollTo({ top: 0, behavior: "smooth" });
  resetNavPosition();
}

export function scrollSpy() {
  const sections = Array.from(document.querySelectorAll(SEL_SECTIONS));

  function matchingNavLink(elem) {
    if (!elem) return;
    var index = sections.indexOf(elem);

    var match;
    while (index >= 0 && !match) {
      var sectionId = sections[index].getAttribute("id");
      if (sectionId) {
        match = document.querySelector(`${SEL_PAGETOC} [href="#${sectionId}"]`);
      }
      index--;
    }
    return match;
  }

  function belowBottomHalf(i) {
    return i.boundingClientRect.bottom > (i.rootBounds.bottom + i.rootBounds.top) / 2;
  }

  function prevElem(elem) {
    var index = sections.indexOf(elem);
    if (index <= 0) {
      return null;
    }
    return sections[index - 1];
  }

  const PAGE_LOAD_BUFFER = 1000;

  function navHighlight(entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        updateHighlight(matchingNavLink(entry.target));
      } else if (entry.time >= PAGE_LOAD_BUFFER && belowBottomHalf(entry)) {
        updateHighlight(matchingNavLink(prevElem(entry.target)));
      }
    });
  }

  const observer = new IntersectionObserver(navHighlight, {
    threshold: 0,
    rootMargin: "0% 0px -95% 0px"
  });

  sections.forEach(function (elem) {
    observer.observe(elem);
  })
  observer.observe(document.querySelector(SEL_PAGE));
}

document.addEventListener("DOMContentLoaded", scrollSpy);
