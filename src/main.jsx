import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import { ReactFlowProvider } from '@xyflow/react';

// Required styles
import '@xyflow/react/dist/style.css';
import './index.css';

const root = ReactDOM.createRoot(document.getElementById('root'));

root.render(
  <React.StrictMode>
    <div style={{ 
      width: '100vw', 
      height: '100vh',
      background: '#f0f0f0' 
    }}>
      <ReactFlowProvider>
        <App />
      </ReactFlowProvider>
    </div>
  </React.StrictMode>
);
