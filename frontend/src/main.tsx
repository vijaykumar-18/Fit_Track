import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import { RenderErrorBoundary } from './components/RenderErrorBoundary'
import './styles/index.css'
import './styles/advanced.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <RenderErrorBoundary>
        <App />
      </RenderErrorBoundary>
    </BrowserRouter>
  </React.StrictMode>,
)
