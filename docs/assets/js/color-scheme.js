if ('colorScheme' in localStorage) {
  document.documentElement.classList.remove('cs-light', 'cs-dark', 'cs-system');
  document.documentElement.classList.add('cs-' + localStorage.colorScheme);
}
function ready() {
  const currentScheme = document.documentElement.classList.contains('cs-dark')
    ? 'dark' : (document.documentElement.classList.contains('cs-light') ? 'light' : 'system');

  document.querySelectorAll('.color-scheme button').forEach(button => {
    button.addEventListener('click', function (e) {
      e.preventDefault();
      const next = button.dataset.next;
      document.documentElement.classList.remove('cs-light', 'cs-dark', 'cs-system');
      document.documentElement.classList.add('cs-' + next);
      localStorage.colorScheme = next;
    });
  });
}

document.addEventListener('DOMContentLoaded', () => {
  ready();
});
