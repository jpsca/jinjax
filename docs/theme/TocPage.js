import { on } from "./jxui.js";

const ACTIVE = "active";
const SEL_TARGET = ".tTocPage a";
const SEL_ACTIVE = `${SEL_TARGET}.${ACTIVE}`;
const SEL_SECTIONS = "main.page section[id]";

on("click", SEL_TARGET, handleClick);

function handleClick (event, target) {
  deActivateAll();
  target.classList.add(ACTIVE);
}

/* =========================================================== */

function deActivateAll() {
  document.querySelectorAll(SEL_ACTIVE).forEach(function (node) {
    node.classList.remove(ACTIVE);
  });
}

export function scrollSpy() {
  const labels = {};
  Array.from(document.querySelectorAll(SEL_TARGET)).forEach(function(aNode){
    labels[aNode.href.slice(1)] = aNode;
  });

  function observe(entries) {
    for(const entry of entries) {
      if (entry.isIntersecting) {
        const aNode = labels[entry.id];
        if (aNode) {
          deActivateAll();
          aNode.classList.add(ACTIVE)
        }
      }
    }
  }

  const observer = new IntersectionObserver(observe, {rootMargin: "-50% 0px"});

  const sections = document.querySelectorAll(SEL_SECTIONS);
  for (let i = 0; i < sections.length; i++)
    observer.observe(sections[i]);
}

window.onload = scrollSpy;

