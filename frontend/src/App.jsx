import React from 'react';
import { useAgentChat } from './hooks/useAgentChat';
import { useTheme } from './hooks/useTheme';
import { Header } from './components/Header';
import { ChatMessage } from './components/ChatMessage';
import { ChatInput } from './components/ChatInput';

export default function App() {
  const { messages, input, setInput, isLoading, sendMessage, chatEndRef } = useAgentChat();
  const { theme, toggleTheme } = useTheme();

  return (
    <div style={styles.container}>
      <Header theme={theme} toggleTheme={toggleTheme} />

      <main style={styles.chatBox}>
        {messages.map((msg, index) => (
          <ChatMessage
            key={index}
            message={msg}
            isLoading={isLoading}
            isLast={index === messages.length - 1}
            chart_theme={theme}
          />
        ))}
        <div ref={chatEndRef} />
      </main>

      <ChatInput
        input={input}
        setInput={setInput}
        onSubmit={sendMessage}
        isLoading={isLoading}
      />
    </div>
  );
}

const styles = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    height: '100vh',
    maxWidth: '100%',
    margin: '0 auto',
    backgroundColor: 'var(--bg-main)',
    transition: 'background-color 0.3s ease',
  },
  chatBox: {
    flex: 1,
    overflowY: 'auto',
    padding: '20px',
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
  },
};