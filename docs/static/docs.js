function setTheme () {
  /* This function needs to be executed as soon as possible to prevent
    a flash of the light theme when the dark theme was previously selected
  */
  const STORAGE_KEY = "theme";
  const DARK = "dark";
  const LIGHT = "light";

  function getColorPreference () {
    return localStorage.getItem(STORAGE_KEY);
  }

  function reflectPreference () {
    const value = getColorPreference ();
    if (value === DARK) {
      document.documentElement.classList.add(DARK);
      document.documentElement.classList.remove(LIGHT);
    } else {
      document.documentElement.classList.add(LIGHT);
      document.documentElement.classList.remove(DARK);
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
