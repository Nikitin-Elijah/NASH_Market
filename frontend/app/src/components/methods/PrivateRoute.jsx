import { useContext, useEffect, useMemo } from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { AuthContext } from './ApiMethods';

const PrivateRoute = ({ redirectPath = '/login' }) => {
  const { user, setUser, loading } = useContext(AuthContext);

  const tokenValid = useMemo(() => {
    const token = localStorage.getItem('token');
    if (!token) return false;
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload.exp > Date.now() / 1000;
    } catch {
      setUser(null);
      return false;
    }
  }, [user]);

  // Очистка user, если токен недействителен
  useEffect(() => {
    if (!user && !tokenValid) {
      localStorage.removeItem('token');
      setUser(null);
    }
  }, [user, setUser, tokenValid]);

  if (loading) return <div className="spinner" />;

  if (!user && !tokenValid) {
    return <Navigate to={redirectPath} replace />;
  }

  return <Outlet />;
};

export default PrivateRoute;
