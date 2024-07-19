const ATTR_FACT = "data-fact";
const CLASS_FACTS = "cd-source__facts";
const CLASS_FACTS_VISIBLE = `${CLASS_FACTS}--visible`;

document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll('[data-component="Source"]').forEach(showFacts);
});

function showFacts(node) {
  function renderFacts(facts) {
    Array.from(node.querySelectorAll(`[${ATTR_FACT}]`))
    .forEach(function(node) {
      const name = node.getAttribute(ATTR_FACT);
      if (facts[name]) {
        node.removeAttribute("hidden");
        node.innerText = facts[name];
      }
    });

    node.querySelector(`.${CLASS_FACTS}`).classList.add(CLASS_FACTS_VISIBLE);
  }

  getSourceFacts(node.href, renderFacts);
}

function getSourceFacts(url, callback) {
  const key = `Source:${url}`;
  let facts = sessionStorage.getItem(key);
  if (facts) {
    callback(JSON.parse(facts));
    return;
  }

  fetchSourceFacts(url)
  .then((facts) => {
    if (facts && Object.keys(facts).length) {
      sessionStorage.setItem(key, JSON.stringify(facts));
      callback(facts);
    }
  });
}

function fetchJSON(url) {
  return fetch(url)
    .then(response => response.json())
    .catch((error) => {
      console.log(error);
    });
}

function fetchSourceFacts(url) {
  /* Try to match GitHub repository */
  let match = url.match(/^.+github\.com\/([^/]+)\/?([^/]+)?/i);
  if (match) {
    const [, user, repo] = match;
    return fetchSourceFactsFromGitHub(user, repo);
  }

  /* Try to match GitLab repository */
  match = url.match(/^.+?([^/]*gitlab[^/]+)\/(.+?)\/?$/i);
  if (match) {
    const [, base, slug] = match;
    return fetchSourceFactsFromGitLab(base, slug);
  }

  /* Fallback */
  return null;
}

function fetchSourceFactsFromGitLab(base, project) {
  const url = `https://${base}/api/v4/projects/${encodeURIComponent(project)}`

  fetchJSON(url)
  .then(function({ star_count, forks_count }) {
    return {
      stars: star_count,
      forks: forks_count,
    };
  });
}

function fetchSourceFactsFromGitHub (user, repo) {
  if (typeof repo === "undefined") {
    return fetchSourceFactsFromGitHubOrg(user);
  } else {
    return fetchSourceFactsFromGitHubRepo(user, repo);
  }
}

function fetchSourceFactsFromGitHubOrg(user) {
  const url = `https://api.github.com/users/${user}`

  fetchJSON(url)
  .then(function(data) {
    return {
      numrepos: data.public_repos,
    };
  });
}

function fetchSourceFactsFromGitHubRepo(user, repo) {
  const url = `https://api.github.com/repos/${user}/${repo}`

  const release = fetchJSON(`${url}/releases/latest`)
  .then((data) => {
    return {
      version: data.tag_name,
    };
  });

  const info = fetchJSON(url)
  .then((data) => {
    return {
      stars: data.stargazers_count,
      forks: data.forks_count,
    };
  });

  return Promise.all([release, info])
  .then(([release, info]) => {
    return { ...release, ...info };
  });
}
