import * as code from './code.js';
import * as search from './search.js';
import * as page from './page.js';

/* Added so the DOMContentLoaded events work without any changes. */
document.addEventListener("turbo:load", function() {
  document.dispatchEvent(new CustomEvent("DOMContentLoaded"));
});

document.addEventListener('DOMContentLoaded', () => {
  code.ready();
  search.ready();
  page.ready();
});
