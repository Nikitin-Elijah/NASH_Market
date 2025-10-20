import { createContext, useState, useEffect } from 'react';
import api from '../js/api';
import { useNavigate } from "react-router-dom";


export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Проверка авторизации при загрузке
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          setLoading(false);
          return;
        }

        // Устанавливаем токен в заголовки по умолчанию
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        
        const userRes = await api.get('/users/me');
        setUser(userRes.data);
      } catch (error) {
        console.error('Auth check failed:', error);
        // При ошибке авторизации очищаем токен
        localStorage.removeItem('token');
        delete api.defaults.headers.common['Authorization'];
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  const login = async (email, password) => {
    try {
      const params = new URLSearchParams();
      params.append('username', email);
      params.append('password', password);

      const res = await api.post('/users/token', params, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });
      
      const token = res.data.access_token;
      localStorage.setItem('token', token);
      
      // Устанавливаем токен в заголовки после успешного логина
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;

      const userRes = await api.get('/users/me');
      setUser(userRes.data);
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  };

  // Добавляем функцию logout
  const logout = () => {
    localStorage.removeItem('token');
    delete api.defaults.headers.common['Authorization'];
    setUser(null);
  };
    
  const add = async (name, description, price, image_url) => {
    const params = new FormData();
    params.append('name', name);
    params.append('description', description);
    params.append('price', price);
    params.append('image', image_url);
    const res = await api.post('/products', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
    console.log(res.data)
  }
  
  const getUser = async () => {
    const token = localStorage.getItem('token');
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    const res = await api.get('/users/me');
    return res.data;
  };
  
  const edit = async (id, name, description, price, image_url) => {
    const params = new FormData();
    params.append('name', name);
    params.append('description', description);
    params.append('price', price);
    params.append('image', image_url);
    await api.put(`/products/${id}`, params, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
  }

  const uploadPhoto = async (file) => {
    const params = new FormData();
    params.append('photo', file);
    const res = await api.put('/users/upload-photo', params, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return res.data.photo_url;
  }

  const get = async (id) => {
    const res = await api.get(`/products/${id}`);
    return res.data
  }
  return (
    <AuthContext.Provider value={{ user, login, add, edit, get, getUser, loading, logout, uploadPhoto }}>
      {children}
    </AuthContext.Provider>
  );
};
