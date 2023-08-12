function setTheme () {
  /* This function needs to be executed as soon as possible to prevent
    a flash of the light theme when the dark theme was previously selected
  */
  const STORAGE_KEY = "theme";
  const DARK = "dark";
  const LIGHT = "light";

  function getColorPreference () {
    let value = localStorage.getItem(STORAGE_KEY)
    if (!value) {
      value = window.matchMedia('(prefers-color-scheme: dark)')
        ? DARK
        : LIGHT
    }
    return value
  }

  function reflectPreference () {
    const value = getColorPreference ();
    localStorage.setItem(STORAGE_KEY, value)
    if (value === DARK) {
      document.documentElement.classList.remove(LIGHT);
      document.documentElement.classList.add(DARK);
    } else {
      document.documentElement.classList.remove(DARK);
      document.documentElement.classList.add(LIGHT);
    }
  }
  reflectPreference();
}
setTheme();

function setPlatform() {
  /* Add a "macos" class to the body to show platform-specific info,
  like the modifier key for keyboard shortcuts beign the ⌘ command key
  rather than the ⌃ control key.
  */
  console.log(navigator.platform)
  if (navigator.platform.indexOf("Mac") === 0) {
    document.body.classList.add("macos");
  }
}
document.addEventListener("DOMContentLoaded", setPlatform);
