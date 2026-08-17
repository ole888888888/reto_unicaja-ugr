import React from 'react';
import EChartsReact from 'react-echarts-library';
import * as echarts from 'echarts';
import RenderTable from './RenderTable';
import darkTheme from '../assets/dark_theme.json';
import lightTheme from '../assets/light_theme.json';
import { ScaleLoader } from 'react-spinners'

export function ChatMessage({ message, isLoading, isLast, chartTheme }) {
  const isUser = message.role === 'user';
  const content = message.content;

  // To avoid printing empty bubbles on screen.
  // if (content === '' && message.type === 'text') return

  if (message.type === 'chart' && message.chartConfig) {
    const chartOption =
      typeof message.chartConfig === 'string' ? JSON.parse(message.chartConfig) : message.chartConfig;

    return (
      <div style={styles.messageWrapper}>
        <div style={{ ...styles.bubble, ...styles.assistantBubble, width: '100%' }}>
          <EChartsReact
          theme={chartTheme==="dark"?darkTheme:lightTheme} 
          option={chartOption} 
          style={{ width: '100%', height: '400px' }} 
          notMerge={true}
          />
        </div>
      </div>
    )
  }

  if (message.type === 'table' && message.tableData) {
    return (
      <div style={styles.messageWrapper}>
        <div style={{ ...styles.bubble, ...styles.assistantBubble, width: '100%' }}>
          <RenderTable tableData={message.tableData} />
        </div>
      </div>
    );
  }

  return (
    <div
      style={{
        ...styles.messageWrapper,
        justifyContent: isUser ? 'flex-end' : 'flex-start',
      }}
    >
      <div
        style={{
          ...styles.bubble,
          ...(isUser ? styles.userBubble : styles.assistantBubble),
        }}
      >
          {isLoading && !content ? (
          <ScaleLoader 
            color={'#36d7b7'} 
            height={10} 
            margin={1}
            speedMultiplier={1.5}
             barCount={10}
          />
        ) : (
          content
        )}
      </div>
    </div>
  );
}

const styles = {
  messageWrapper: {
    display: 'flex',
    width: '100%',
  },
  bubble: {
    maxWidth: '75%',
    padding: '12px 16px',
    borderRadius: '16px',
    fontSize: '0.95rem',
    lineHeight: '1.4',
    whiteSpace: 'pre-wrap',
    wordBreak: 'break-word',
    transition: 'background-color 0.3s ease, color 0.3s ease',
  },
  userBubble: {
    backgroundColor: 'var(--bubble-user-bg)',
    color: 'var(--bubble-user-text)',
    borderBottomRightRadius: '2px',
  },
  assistantBubble: {
    backgroundColor: 'var(--bubble-assistant-bg)',
    color: 'var(--bubble-assistant-text)',
    borderBottomLeftRadius: '2px',
    boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
  },
};