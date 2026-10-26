function showResults(results, store, searchTerm) {
  var searchResults = document.getElementById('search-results');
  document.querySelector('#search-query mark').textContent = searchTerm;

  var appendString = '';
  var shownUrls = new Set();

  if (results.length) {
      const words = searchTerm.toLowerCase().split(/\s+/gi).join('|'); // Support multiple words
      const highlightRegex = new RegExp(`\\b${words}\\b`, 'gi');

    results.forEach(result => {
      var item = store[result.ref];
      if (shownUrls.has(item.url)) {
        return; // Skip duplicate URLs
      }
      shownUrls.add(item.url);

      appendString += '<div class="search-result">';
      appendString += '  <h3><a href="' + item.url + '">' + item.title + '</a></h3>';
      appendString += '  <small><a href="' + item.url + '">' + item.section + '</a></small>';
      var content = item.content;

      if (item.content.startsWith('<pre>')) {
        content = content.replace(/<pre>/g, '').replace(/<\/pre>/g, '');
        if (content.length > 200) {
          content = content.slice(0, 200) + ' &hellip;';
        } else {
          content = content.slice(0, 200);
        }
        content = content.replace(highlightRegex, '<mark>$&</mark>');
        appendString += '  <div><pre>' + content + '</pre></div>';
      } else {
        content = content.slice(0, 300).replace(highlightRegex, '<mark>$&</mark>');
        appendString += '  <div>' + content + ' &hellip;</div>';
      }

      appendString += '</div>';
    });
  } else {
    appendString = '<div class="search-result"><p>' + window.strings.NO_RESULTS_FOUND + '</p></div>';
  }
  searchResults.innerHTML = appendString;
}

function getQuery(variable) {
  var params = new URLSearchParams(window.location.search.substring(1));
  if (params.has(variable)) {
    return decodeURIComponent(params.get(variable).replace(/\+/g, '%20'));
  }
  return null;
}

export function ready() {
  var searchTerm = getQuery('q');
  if (searchTerm) {
    var searchBoxes = document.querySelectorAll('.search-box');
    searchBoxes.forEach(searchBox => {
      searchBox.setAttribute('value', searchTerm);
    });
    var idx = lunr(function () {
      this.field('id');
      this.field('title', { boost: 10 });
      this.field('author');
      this.field('section');
      this.field('content');
      for (var key in window.store) {
        this.add({
          'id': key,
          'title': window.store[key].title,
          'author': window.store[key].author,
          'section': window.store[key].section,
          'content': window.store[key].content
        });
      }
    });
    var results = idx.search(searchTerm);
    showResults(results, window.store, searchTerm);
  }

  document.querySelectorAll('.search').forEach(form => {
    var searchInput = form.querySelector('input');
    form.addEventListener('submit', e => {
      e.preventDefault();
      var searchValue = searchInput.value.trim();
      if (searchValue) {
        searchInput.value = searchValue;
        form.submit();
      }
    });
  });
}