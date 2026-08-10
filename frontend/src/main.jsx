import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

// Create root llama a un nodo DOM, es decir va a buscar en el archivo
// un nodo de id root, y allí va a renderizar el código de react.
createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
