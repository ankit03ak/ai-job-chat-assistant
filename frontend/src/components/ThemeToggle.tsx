"use client";

import { Moon, Sun } from "lucide-react";
import { useEffect, useState } from "react";

type Theme = "light" | "dark";

const storageKey = "assistant-theme";

export default function ThemeToggle() {
  const [theme, setTheme] = useState<Theme>("light");

  useEffect(() => {
    const preferred: Theme =
      document.documentElement.dataset.theme === "dark" ? "dark" : "light";
    setTheme(preferred);
    document.documentElement.dataset.theme = preferred;
    document.documentElement.style.colorScheme = preferred;
  }, []);

  function toggleTheme() {
    const nextTheme: Theme = theme === "light" ? "dark" : "light";
    setTheme(nextTheme);
    document.documentElement.dataset.theme = nextTheme;
    document.documentElement.style.colorScheme = nextTheme;
    window.localStorage.setItem(storageKey, nextTheme);
  }

  const isDark = theme === "dark";

  return (
    <button
      className="theme-toggle"
      type="button"
      onClick={toggleTheme}
      aria-label={`Switch to ${isDark ? "light" : "dark"} theme`}
      title={`Switch to ${isDark ? "light" : "dark"} theme`}
    >
      {isDark ? <Sun size={16} /> : <Moon size={16} />}
      <span>{isDark ? "Light mode" : "Dark mode"}</span>
    </button>
  );
}
