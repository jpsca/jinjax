(function () {

  const SEL_DIALOG = ".SearchDialog"
  const SEL_INPUT = ".SearchInput"
  const SEL_RESULTS = ".SearchResults"
  const ATTR_INDEX = "data-index"
  const ATTR_TRIGGER_KEY = "data-trigger-key"

  setupAll(document)

  function setupAll(root) {
    root.querySelectorAll(SEL_DIALOG)
      .forEach((dialog) => { setup(dialog) })
  }

  function setup(dialog) {
    const input = dialog.querySelector(SEL_INPUT)
    const indexUrl = dialog.getAttribute(ATTR_INDEX)
    const triggerKey = (dialog.getAttribute(ATTR_TRIGGER_KEY) || "").toLowerCase()

    const results = dialog.querySelector(SEL_RESULTS)
    const resultTmpl = dialog.querySelector("template").innerHTML.trim()

    let idx, docs

    fetch(indexUrl)
      .then((response) => response.json())
      .then((data) => {
        docs = data.docs
        idx = lunr.Index.load(data.index)

        input.addEventListener("input", onInput)

        if (triggerKey) {
          document.body.addEventListener("keydown", onBodyKeyDown)
        }
      })

    /* --- */

    function onInput (event) {
      let search_term = input.value.replace(/\s+/g, " ").trim()
      if (!search_term) { return }
      const matches =  idx.search(search_term)
      console.log(search_term, matches)
      showResults(matches, search_term)
    }

    function showResults (matches, search_term) {
      results.textContent = ""
      matches.forEach(function (match) {
        appendResult(match, search_term)
      })
    }

    function appendResult (match, search_term) {
      const page = docs[match.ref]
      let body = page.body
      let title = page.title

      search_term.split(" ").forEach(function (word) {
        const rx = new RegExp(escapeRegExp(word), "gi")
        body = page.body.replace(rx, "<mark>$1</mark>")
        title = page.title.replace(rx, "<mark>$1</mark>")
      })

      const html = resultTmpl
        .replace("{URL}", page.loc)
        .replace("{PARENT}", page.parent || "")
        .replace("{TITLE}", title)
        .replace("{BODY}", body)
        .replace("{SCORE}", match.score)

      results.appendChild(htmlToElement(html))
    }

    /* --- */

    function onBodyKeyDown (event) {
      if (event.shiftKey || event.altKey) {
        return
      }
      if (
        event.key.toLowerCase() == triggerKey
        && (event.metaKey || event.ctrlKey)
      ) {
        dialog.showModal()
        event.preventDefault()
        return false
      }
    }
  }

  /* --- UTILS --- */

  function escapeRegExp(word) {
    const escaped = word.replace(
      /[.+?^${}()|[\]\\]/g,
      "\\$&" // $& means the matched char
    )
    // Allow * to match anything in a word
    console.debug(escaped.replace(/\*/g, "\\W*"))
    return escaped.replace(/\*/g, "\\W*")
  }

  function htmlToElement(html) {
    var template = document.createElement("template");
    template.innerHTML = html;
    return template.content.firstChild;
  }

  /* --- OBSERVER --- */

  new MutationObserver( (mutationList) => {
    mutationList.forEach( (mutation) => {
      if (mutation.type !== "childList") return
      mutation.addedNodes.forEach( (node) => {
        // Node of type "element"
        if (node.nodeType === 1) {
          setupAll(node)
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

  /* --- THE END --- */
})()
