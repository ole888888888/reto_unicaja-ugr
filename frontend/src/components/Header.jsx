import React from 'react';
import Moon from '../assets/moon.svg'
import Sun from '../assets/sun.svg'

export function Header({ theme, toggleTheme }) {
  return (
    <header style={styles.header}>
      <div style={styles.headerTitle}>
        <img src={"/favicon.ico"} style={{width: '32px', height: '32px'}}/>
        <h1 style={{ margin: 0, fontSize: '1.2rem' }}>ADA (Asistente Digital de Acompañamiento)</h1>
      </div>
      <button onClick={toggleTheme} style={styles.themeButton}>
        <img 
          src={theme === 'light' ? Moon : Sun}
          alt='Theme Icon'
          style={{width: '22px', height: '22px'}} 
        />
      </button>
    </header>
  );
}

const styles = {
  header: {
    backgroundColor: 'var(--header-bg)',
    color: 'var(--header-text)',
    padding: '16px 24px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    transition: 'background-color 0.3s ease',
  },
  headerTitle: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
  },
  themeButton: {
    backgroundColor: '#95e891',
    border: '1.5px solid var(--bg-main)',
    borderRadius: '8px',
    padding: '6px 12px',
  
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
};