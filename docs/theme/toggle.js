(function(){

const ATTR_TOGGLE_CLASS = "data-toggle"
const SEL_TOGGLE = `[${ATTR_TOGGLE_CLASS}]`

const ATTR_TOGGLE_MODAL = "data-toggle-modal"
const SEL_SHOW_MODAL = `[${ATTR_TOGGLE_MODAL}]`

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
  root.querySelectorAll(SEL_TOGGLE)
    .forEach( (node) => {
      node.addEventListener("click", onToggleClick)
    })
  root.querySelectorAll(SEL_SHOW_MODAL)
  .forEach( (node) => {
    node.addEventListener("click", onShowModalClick)
  })
}

addEvents(document)

function onToggleClick (event) {
  const target = event.currentTarget
  const [ sel, value ] = (target.getAttribute(ATTR_TOGGLE_CLASS) || "").split("|")
  if (!!sel && !!value) { toggle(sel, value) }
}

function toggle (sel, value) {
  for (const node of document.querySelectorAll(sel)) {
    toggleAttribute(node, value)
  }
}

function toggleAttribute (node, value) {
  if (value[0] == "[") {
    node.toggleAttribute(value.slice(1, -1))
  } else if (value[0] == ".") {
    node.classList.toggle(value.slice(1))
  }
}

function onShowModalClick (event) {
  const target = event.currentTarget
  const sel = target.getAttribute(ATTR_TOGGLE_MODAL) || ""
  for (const dialog of document.querySelectorAll(sel)) {
    if (dialog.open) {
      dialog.close()
     } else {
      dialog.showModal()
     }
  }
}

})()
