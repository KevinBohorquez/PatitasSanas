// App.jsx
import React from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ToastProvider } from './context/ToastContext';
import { ConfirmProvider } from './context/ConfirmProvider';
import AppRoutes from './routes/AppRoutes';

function App() {
  return (
    <ToastProvider position="top-right" defaultDuration={4000}>
      <ConfirmProvider>
        <AuthProvider>
          <Router>
            <div className="App">
              <AppRoutes />
            </div>
          </Router>
        </AuthProvider>
      </ConfirmProvider>
    </ToastProvider>
  );
}

export default App;
