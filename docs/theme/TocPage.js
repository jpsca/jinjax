(function(){
/** "scrollspy" implementation
 * Only one ".Page" will be observed
*/

const ACTIVE = "active"
const UP = "up"
const DOWN = "down"

const SEL_TOC = ".TocPage"
const SEL_TARGET = `${SEL_TOC} a`
const SEL_ACTIVE = `${SEL_TARGET}.${ACTIVE}`
const SEL_PAGE = ".Page"
const SEL_HEADERS = "h1[id], h2[id], h3[id], h4[id], h5[id], h6[id]";

function deActivateLinks() {
  document.querySelectorAll(SEL_ACTIVE).forEach(function (node) {
    node.classList.remove(ACTIVE)
  })
}

/* =========================================================== */

new MutationObserver( (mutationList) => {
  mutationList.forEach( (mutation) => {
    if (mutation.type !== "childList") return
    mutation.addedNodes.forEach( (node) => {
      // Node of type "element"
      if (node.nodeType === 1) {
        addEvents(node)
      }
    })
  })
})
  .observe(document.body, {
    subtree: true,
    childList: true,
    attributes: false,
    characterData: false
  })

function addEvents (root) {
  root.querySelectorAll(SEL_TARGET)
    .forEach( (node) => {
      node.addEventListener('click', onClick)
    })
}

function onClick (event) {
  const target = event.target.closest(SEL_TARGET)
  deActivateLinks()
  target.classList.add(ACTIVE)
}

addEvents(document)

/* =========================================================== */

const observer = new IntersectionObserver(onIntersect)

let headers
let prevYPosition = 0
let direction = UP

headers = document.querySelector(SEL_PAGE).querySelectorAll(SEL_HEADERS)
headers.forEach(function (header) {
  observer.observe(header)
})

function onIntersect (entries, observer) {
  entries.forEach(function (entry) {
    direction = document.scrollTop > prevYPosition ? DOWN : UP
    prevYPosition = document.scrollTop
    if (!shouldUpdate(entry)) { return }

    const header = direction === DOWN ? getTargetHeader(entry) : entry.target
    activateLink(header)
  })
}

function shouldUpdate (entry) {
  return (
       (direction === DOWN && !entry.isIntersecting)
    || (direction === UP && entry.isIntersecting)
  )
}

function getTargetHeader (entry) {
  const index = headers.findIndex((header) => header == entry.target)

  if (index >= headers.length - 1) {
    return entry.target
  } else {
    return headers[index + 1]
  }
}

function activateLink(header) {
  deActivateLinks();
  document.querySelectorAll(`${SEL_TOC} a[href="#${header.id}"`).forEach(function (node) {
    node.classList.add(ACTIVE)
  })
}

})()
