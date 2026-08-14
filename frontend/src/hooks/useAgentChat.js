import { useState, useRef, useEffect } from 'react';

export function useAgentChat() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      type: 'text',
      content:
        '¡Hola! Soy tu Asistente Financiero. ¿En qué puedo ayudarte hoy? (Puedes consultar tu saldo, ver movimientos o hacer una transferencia).',
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const chatEndRef = useRef(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async (e) => {
    e?.preventDefault();
    if (!input.trim() || isLoading) return;

    const userPrompt = input;
    setInput('');
    setIsLoading(true);

    // Add the user's request.
    setMessages((prev) => [...prev, { role: 'user', content: userPrompt }]);
    setMessages((prev) => [...prev, {role: 'assistant', type: 'text', content: ''}])

    try {
      const response = await fetch('http://127.0.0.1:8000/api/agent', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: userPrompt }),
      });

      if (!response.ok) {
        throw new Error(`Server returned status ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      let buffer = '';
      let accumulatedText = '';
      let currentEvent = 'message';

      while (true) {
        // done is a  bool marking if the streaming has ended.
        // value is the data sent in the streaming.
        // We wait for a value to arrive.
        const { done, value } = await reader.read();
        if (done) break;

        // We take the info into the buffer.
        buffer += decoder.decode(value, {stream: true});
        // We separate by lines.
        const lines = buffer.split('\n');

        // We take the last incomplete line and put it in the buffer to be concatenated
        // with the next value.
        buffer = lines.pop() || '';

        // Process the lines we have.
        for (let line of lines) {
          // Get the type of event to process.
          if (line.startsWith('event: ')) {
            currentEvent = line.replace('event: ', '').trim();
          } 
          // Process the data.
          else if (line.startsWith('data: ')) {
            let dataContent = line.replace('data: ', '');

            // chart processing.
            if (currentEvent === "chart"){
              try {
                const chartConfig = JSON.parse(dataContent)
                setMessages((prev) => [
                  ...prev,
                  { role: 'assistant', type: 'chart', chartConfig},
                ])
              } catch (err) {
                console.error('Failed to parse chart JSON', err)
              }
              currentEvent = 'message';
              accumulatedText = '';
            } 
            // Table processing.
            else if (currentEvent === "table"){
              try {
                const tableData = JSON.parse(dataContent)
                setMessages((prev) => [
                  ...prev,
                  { role: 'assistant', type: 'table', tableData},
                ])
              } catch (err) {
                console.error ('Failed to parse the table JSON', err);
              }
              currentEvent = "message";
              accumulatedText = '';
            } 
            // Message processing.
            else {
              const data = JSON.parse(dataContent)
              accumulatedText += data.text;
              setMessages((prev) => {
                const lastMsg = prev[prev.length - 1];

                // Append new text bubble if previous message is non-text or user message
                if (
                  lastMsg.role === 'user' ||
                  lastMsg.type === 'chart' ||
                  lastMsg.type === 'table') {
                  return [...prev, {role: 'assistant', type: 'text', content: accumulatedText}]
                }

                // If not update the active text bubble
                const updated = [...prev];
                updated[updated.length - 1] = {
                  role: 'assistant',
                  type: 'text',
                  content: accumulatedText,
                };
                return updated;
              });
            }
          }
        }
      }
    } catch (error) {
      setMessages((prev) =>{ 
        const updated = [...prev];
        updated[updated.length-1] = {
          role: 'assistant',
          content:
            'Ocurrió un error al procesar tu solicitud. Asegúrate de que el backend de FastAPI está corriendo.',
        };
        return updated
      });
    } finally {
      setIsLoading(false);
    }
  };

  return {
    messages,
    input,
    setInput,
    isLoading,
    sendMessage,
    chatEndRef,
  };
}