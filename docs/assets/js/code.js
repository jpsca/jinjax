export function ready() {
  var highlights = document.querySelectorAll(".highlight");
  highlights.forEach(highlight => {
    if (highlight.querySelector("button.copy")) {
      return; // Skip if button already exists
    }
    var button = document.createElement("button");
    button.className = "copy";
    button.innerText = window.strings.COPY || "Copy";
    highlight.append(button);
    button.addEventListener("click", function (e) {
      e.preventDefault();
      var code = highlight.querySelector("code").innerText.trim();
      window.navigator.clipboard.writeText(code);
      button.innerText = window.strings.COPIED || "Copied";
      button.blur();
      setTimeout(function () { button.innerText = window.strings.COPY || "Copy"; }, 1000);
    });
  });
}

