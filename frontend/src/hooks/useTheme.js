import { useState, useEffect } from 'react';

export function useTheme() {
  const [theme, setTheme] = useState(() => { // Arrow function to avoid reinitializing.
    return localStorage.getItem('theme') || 'light'; // It's called lazy initial state.
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prevTheme) => (prevTheme === 'light' ? 'dark' : 'light'));
  };

  return { theme, toggleTheme };
}