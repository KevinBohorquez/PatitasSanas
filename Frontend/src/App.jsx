// App.jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import RoleSelection from './pages/RoleSelection';
import Login from './pages/Login';
import AdminDashboard from './pages/AdminDashboard';
import VeterinarioDashboard from './pages/VeterinarioDashboard';
import RecepcionistaDashboard from './pages/RecepcionistaDashboard';
import ProtectedRoute from './components/common/ProtectedRoute';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Routes>
            {/* Ruta inicial - Selección de rol */}
            <Route path="/" element={<RoleSelection />} />
            
            {/* Login con parámetro de rol */}
            <Route path="/login/:role" element={<Login />} />
            
            {/* Rutas protegidas por rol */}
            <Route 
              path="/admin" 
              element={
                <ProtectedRoute allowedRoles={['administrador']}>
                  <AdminDashboard />
                </ProtectedRoute>
              } 
            />
            
            <Route 
              path="/veterinario" 
              element={
                <ProtectedRoute allowedRoles={['veterinario']}>
                  <VeterinarioDashboard />
                </ProtectedRoute>
              } 
            />
            
            <Route 
              path="/recepcionista" 
              element={
                <ProtectedRoute allowedRoles={['recepcionista']}>
                  <RecepcionistaDashboard />
                </ProtectedRoute>
              } 
            />

            {/* Redirección por defecto para rutas no encontradas */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;