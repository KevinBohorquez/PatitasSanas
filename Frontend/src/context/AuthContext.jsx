// context/AuthContext.jsx
import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth debe ser usado dentro de un AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const BASE_URL = 'https://veterinariaclinicabackend-production.up.railway.app/api/v1';

  // Verificar si hay usuario
  useEffect(() => {
    const savedUser = localStorage.getItem('currentUser');
    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }
    setLoading(false);
  }, []);

  // Función de login con backend
  const login = async (credentials, userRole) => {
    try {
      const response = await fetch(`${BASE_URL}/auth/login`, {
        method: 'POST',
        mode: 'cors',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({
          username: credentials.username,
          password: credentials.password,
          role: userRole
        })
      });

      const data = await response.json();

      if (response.ok && data.success === true) {
        let userData = data.user_info || data.session_info || {};
        let sessionData = data.session_info || {};
        let token = data.access_token || data.token;

        // Obtener el rol real del usuario desde el backend
        const realUserRole = (userData.tipo_usuario || sessionData.tipo_usuario || '').toLowerCase();
        const selectedRole = userRole.toLowerCase();

        // VALIDACIÓN DE SEGURIDAD: El rol real debe coincidir con el seleccionado
        if (realUserRole !== selectedRole) {
          return { 
            success: false, 
            message: `No tiene permisos para acceder como ${userRole}. Su rol es: ${userData.tipo_usuario || 'desconocido'}` 
          };
        }

        // Crear sesión 
        const userSession = {
          id: userData.id_usuario || sessionData.user_id || userData.id,
          username: userData.username || sessionData.username || credentials.username,
          role: userData.tipo_usuario || sessionData.tipo_usuario || userRole,
          name: userData.nombre_completo || userData.nombre || userData.username || credentials.username,
          email: userData.email || '',
          active: userData.estado === 'Activo' || userData.active !== false,
          token: token,
          
          permisos: data.permisos || {},
          session_info: sessionData
        };
        // Guardar en estado y localStorage
        setUser(userSession);
        localStorage.setItem('currentUser', JSON.stringify(userSession));
        
        return { 
          success: true, 
          user: userSession, 
          message: data.message || data.detail || 'Login exitoso'
        };
      } else {
        return { 
          success: false, 
          message: data.message || data.detail || data.error || 'Credenciales inválidas' 
        };
      }
    } catch (error) {
      return { 
        success: false, 
        message: 'Error de conexión. Verifique su conexión a internet.' 
      };
    }
  };

  // Función de logout
  const logout = async () => {
    try {
      // Si el usuario tiene token, notificar al backend (opcional)
      if (user?.token) {
        await fetch(`${BASE_URL}/auth/logout`, {
          method: 'POST',
          mode: 'cors',
          headers: {
            'Authorization': `Bearer ${user.token}`,
            'Content-Type': 'application/json',
          }
        }).catch(() => {
          // Si falla el logout en backend, continuar con logout local
          console.log('No se pudo notificar logout al backend');
        });
      }
    } catch (error) {
      console.error('Error en logout:', error);
    } finally {
      // Limpiar estado local siempre
      setUser(null);
      localStorage.removeItem('currentUser');
    }
  };

  // Verificar si el usuario tiene un rol específico
  const hasRole = (role) => {
    return user?.role === role;
  };

  const value = {
    user,
    login,
    logout,
    hasRole,
    isAuthenticated: !!user,
    loading
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
/*
// context/AuthContext.jsx
import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth debe ser usado dentro de un AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const BASE_URL = 'https://veterinariaclinicabackend-production.up.railway.app/api/v1';

  // Verificar si hay usuario en localStorage al cargar
  useEffect(() => {
    const savedUser = localStorage.getItem('currentUser');
    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }
    setLoading(false);
  }, []);

  // Función de login con backend
  const login = async (credentials, userRole) => {
    try {
      const response = await fetch(`${BASE_URL}/auth/login`, {
        method: 'POST',
        mode: 'cors',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({
          username: credentials.username,
          password: credentials.password,
          role: userRole
        })
      });

      const data = await response.json();

      if (response.ok && data.success) {
        // Crear sesión de usuario con los datos del backend
        const userSession = {
          id: data.user.id,
          username: data.user.username,
          role: data.user.role,
          name: data.user.name || data.user.username,
          email: data.user.email,
          active: data.user.active,
          token: data.access_token
        };
        
        // Guardar en estado y localStorage
        setUser(userSession);
        localStorage.setItem('currentUser', JSON.stringify(userSession));
        
        return { 
          success: true, 
          user: userSession, 
          message: data.message || 'Login exitoso'
        };
      } else {
        return { 
          success: false, 
          message: data.message || data.detail || 'Credenciales inválidas' 
        };
      }
    } catch (error) {
      console.error('Error en login:', error);
      return { 
        success: false, 
        message: 'Error de conexión. Verifique su conexión a internet.' 
      };
    }
  };

  // Función de logout
  const logout = async () => {
    try {
      // Si el usuario tiene token, notificar al backend (opcional)
      if (user?.token) {
        await fetch(`${BASE_URL}/auth/logout`, {
          method: 'POST',
          mode: 'cors',
          headers: {
            'Authorization': `Bearer ${user.token}`,
            'Content-Type': 'application/json',
          }
        }).catch(() => {
          // Si falla el logout en backend, continuar con logout local
          console.log('No se pudo notificar logout al backend');
        });
      }
    } catch (error) {
      console.error('Error en logout:', error);
    } finally {
      // Limpiar estado local siempre
      setUser(null);
      localStorage.removeItem('currentUser');
    }
  };

  // Verificar si el usuario tiene un rol específico
  const hasRole = (role) => {
    return user?.role === role;
  };

  const value = {
    user,
    login,
    logout,
    hasRole,
    isAuthenticated: !!user,
    loading
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}; */
/*
// context/AuthContext.jsx
import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth debe ser usado dentro de un AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Verificar si hay usuario en localStorage al cargar
  useEffect(() => {
    const savedUser = localStorage.getItem('currentUser');
    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }
    setLoading(false);
  }, []);

  const login = (userData) => {
    try {
      const userSession = {
        username: userData.username,
        role: userData.role,
        name: userData.name
      };
      
      setUser(userSession);
      localStorage.setItem('currentUser', JSON.stringify(userSession));
      return { success: true, user: userSession };
    } catch (error) {
      return { success: false, message: 'Error al iniciar sesión' };
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('currentUser');
  };

  const hasRole = (role) => {
    return user?.role === role;
  };

  const value = {
    user,
    login,
    logout,
    hasRole,
    isAuthenticated: !!user,
    loading
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};*/