import React from 'react';

export function ChatInput({ input, setInput, onSubmit, isLoading }) {
  return (
    <form onSubmit={onSubmit} style={styles.inputForm}>
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Escribe tu consulta (ej: ¿Cuál es mi saldo actual?)..."
        disabled={isLoading}
        style={styles.input}
      />
      <button
        type="submit"
        disabled={isLoading || !input.trim()}
        style={styles.button}
      >
        Enviar
      </button>
    </form>
  );
}

const styles = {
  inputForm: {
    display: 'flex',
    gap: '10px',
    padding: '16px 20px',
    backgroundColor: 'var(--input-bg)',
    borderTop: '1px solid var(--border-color)',
    transition: 'background-color 0.3s ease',
  },
  input: {
    flex: 1,
    padding: '12px 16px',
    border: '1px solid var(--input-border)',
    borderRadius: '24px',
    fontSize: '0.95rem',
    outline: 'none',
    backgroundColor: 'var(--input-bg)',
    color: 'var(--input-text)',
  },
  button: {
    backgroundColor: 'var(--button-bg)',
    color: 'var(--button-text)',
    border: 'none',
    borderRadius: '24px',
    padding: '0 24px',
    fontWeight: 'bold',
    cursor: 'pointer',
  },
};