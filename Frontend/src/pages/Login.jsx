// pages/Login.jsx
import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import '../styles/Login.css';

const Login = () => {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const { login, isAuthenticated, user } = useAuth();
  const navigate = useNavigate();
  const { role } = useParams();

  // Redireccionando tras autenticación 
  useEffect(() => {
    if (isAuthenticated && user) {
      const normalizedRole = user.role.toLowerCase();
      const dashboardRoutes = {
        administrador: '/admin',
        veterinario: '/veterinario',
        recepcionista: '/recepcionista'
      };
      
      const targetRoute = dashboardRoutes[normalizedRole];
      if (targetRoute) {
        navigate(targetRoute);
      }
    }
  }, [isAuthenticated, user, navigate]);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    if (error) setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validaciones
    if (!formData.username.trim() || !formData.password.trim()) {
      setError('Por favor, complete todos los campos');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const result = await login(formData, role);
      
      if (result.success) {
        // Login exitoso - Redirige al dashboard correspondiente
        const normalizedRole = result.user.role.toLowerCase();
        const dashboardRoutes = {
          administrador: '/admin',
          veterinario: '/veterinario',
          recepcionista: '/recepcionista'
        };
        
        const targetRoute = dashboardRoutes[normalizedRole];
        if (targetRoute) {
          navigate(targetRoute);
        } else {
          setError(`Rol de usuario no reconocido: ${result.user.role}`);
        }
      } else {
        setError(result.message);
      }
    } catch (err) {
      console.error('Error en handleSubmit:', err);
      setError('Error de conexión. Por favor, intente nuevamente.');
    } finally {
      setLoading(false);
    }
  };

  const handleBackToRoles = () => {
    navigate('/');
  };

  const getRoleTitle = () => {
    const titles = {
      recepcionista: 'Recepcionista',
      veterinario: 'Veterinario',
      administrador: 'Administrador'
    };
    return titles[role] || 'Usuario';
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <button 
          className="back-button"
          onClick={handleBackToRoles}
          disabled={loading}
        >
          Atrás
        </button>
        
        <div className="login-header">
          <h1 className="login-title">INICIO DE SESIÓN</h1>
          <h2 className="login-role-title">{getRoleTitle()}</h2>
        </div>
        
        <div className="login-divider"></div>
        
        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="username">USUARIO *</label>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              placeholder="Ingrese su usuario"
              required
              disabled={loading}
              autoComplete="username"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">CONTRASEÑA *</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="Ingrese su contraseña"
              required
              disabled={loading}
              autoComplete="current-password"
            />
          </div>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <button 
            type="submit" 
            className="login-button"
            disabled={loading || !formData.username.trim() || !formData.password.trim()}
          >
            {loading ? 'Iniciando sesión...' : 'INICIAR SESIÓN'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Login;

/*
// pages/Login.jsx
import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import '../styles/Login.css';

const Login = () => {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const { login, isAuthenticated, user } = useAuth();
  const navigate = useNavigate();
  const { role } = useParams();

  // Datos de usuarios por rol
  const users = {
    recepcionista: [
      { username: "recep1", password: "123", role: "recepcionista", name: "Ana López" },
      { username: "recep2", password: "123", role: "recepcionista", name: "María García" }
    ],
    veterinario: [
      { username: "vet1", password: "123", role: "veterinario", name: "Dr. Carlos Mendez" },
      { username: "vet2", password: "123", role: "veterinario", name: "Dra. Patricia Silva" }
    ],
    administrador: [
      { username: "admin", password: "123", role: "admin", name: "Administrador" }
    ]
  };

  // Redireccionar si ya está autenticado
  useEffect(() => {
    if (isAuthenticated && user) {
      const dashboardRoutes = {
        admin: '/admin',
        veterinario: '/veterinario',
        recepcionista: '/recepcionista'
      };
      navigate(dashboardRoutes[user.role] || '/');
    }
  }, [isAuthenticated, user, navigate]);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    if (error) setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // Buscar usuario en el rol correspondiente
      const roleUsers = users[role] || users.administrador;
      const foundUser = roleUsers.find(
        u => u.username === formData.username && u.password === formData.password
      );

      if (foundUser) {
        const result = login(foundUser);
        if (result.success) {
          const dashboardRoutes = {
            admin: '/admin',
            veterinario: '/veterinario',
            recepcionista: '/recepcionista'
          };
          navigate(dashboardRoutes[foundUser.role]);
        }
      } else {
        setError('Credenciales inválidas para este rol');
      }
    } catch (err) {
      setError('Error al iniciar sesión. Intente nuevamente.');
    } finally {
      setLoading(false);
    }
  };

  const handleBackToRoles = () => {
    navigate('/');
  };

  const getRoleTitle = () => {
    const titles = {
      recepcionista: 'Recepcionista',
      veterinario: 'Veterinario',
      administrador: 'Administrador'
    };
    return titles[role] || 'Usuario';
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <button 
            className="back-button"
            onClick={handleBackToRoles}
          >
            Atrás
          </button>
        <div className="login-header">
          <h1 className="login-title">INICIO DE SESIÓN</h1>
          <h2 className="login-role-title">{getRoleTitle()}</h2>
        </div>
        
        <div className="login-divider"></div>
        
        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="username">Usuario</label>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              placeholder="Ingrese su usuario"
              required
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Contraseña</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="Ingrese su contraseña"
              required
              disabled={loading}
            />
          </div>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <button 
            type="submit" 
            className="login-button"
            disabled={loading}
          >
            {loading ? 'Iniciando sesión...' : 'Iniciar sesión'}
          </button>
        </form>

        <div className="login-help">
          <p>Usuarios de prueba para {getRoleTitle()}:</p>
          <ul>
            {(users[role] || users.administrador).map((u, index) => (
              <li key={index}>
                <strong>{u.username}</strong> / 123
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};

export default Login; */