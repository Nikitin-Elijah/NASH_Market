import { useContext } from 'react';
import { Navigate } from 'react-router-dom';
import { AuthContext } from './ApiMethods';

const PrivateRoute = ({ children }) => {
  const { user, loading } = useContext(AuthContext);
  
  const isTokenValid = () => {
    const token = localStorage.getItem('token');
    if (!token) return false;

    try {
      const base64Url = token.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const payload = JSON.parse(window.atob(base64));

      const currentTime = Date.now() / 1000;
      return payload.exp > currentTime;
    } catch {
      return false;
    }
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  if (user || isTokenValid()) {
    return children;
  }

  // Изменено перенаправление на домашнюю страницу
  return <Navigate to="/" />;
};

export default PrivateRoute;
