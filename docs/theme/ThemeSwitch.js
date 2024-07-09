import { on } from "./jxui.js";

const SEL_TARGET = ".cd-theme-switch";
const STORAGE_KEY = "theme";

const DARK = "dark";
const LIGHT = "light";
const theme = {value: getColorPreference()};

reflectPreference();
on("click", SEL_TARGET, onClick);
// sync with system changes
window
  .matchMedia("(prefers-color-scheme: dark)")
  .addEventListener("change", ({matches:isDark}) => {
    theme.value = isDark ? DARK : LIGHT
    setPreference()
  });

function onClick (event, target) {
  if (target.matches("[disabled]")) return;
  theme.value = theme.value === LIGHT ? DARK : LIGHT;
  setPreference();
}
function setPreference () {
  localStorage.setItem(STORAGE_KEY, theme.value);
  reflectPreference();
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
function getColorPreference () {
  return localStorage.getItem(STORAGE_KEY);
}