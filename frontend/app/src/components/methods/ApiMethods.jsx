import { createContext, useState, useEffect } from "react";
import api from "../../js/api";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const logout = () => {
    setUser(null);
    localStorage.removeItem("token");
    delete api.defaults.headers.common["Authorization"];
  };

  useEffect(() => {
    const loadUser = async () => {
      try {
        const token = localStorage.getItem("token");
        if (!token) return;

        api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
        const res = await api.get("/users/me");
        setUser(res.data);
      } catch (error) {
        console.error("Auth check failed:", error);
        setTimeout(() => logout(), 0);
      } finally {
        setLoading(false);
      }
    };
    loadUser();
  }, []);

  const refreshUser = async () => {
    try {
      const token = localStorage.getItem("token");
      if (!token) return null;
      api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
      const res = await api.get("/users/me");
      setUser(res.data);
      return res.data;
    } catch (error) {
      console.error("Refresh user failed:", error);
      setTimeout(() => logout(), 0);
      return null;
    }
  };

  const isTokenValid = () => {
    const token = localStorage.getItem("token");
    if (!token) return false;
    try {
      const base64Url = token.split(".")[1];
      const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
      const payload = JSON.parse(window.atob(base64));
      const currentTime = Date.now() / 1000;
      return payload.exp > currentTime;
    } catch {
      return false;
    }
  };

  const login = async (username, password) => {
    try {
      const params = new URLSearchParams();
      params.append("username", username);
      params.append("password", password);

      const res = await api.post("/users/token", params, {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      });

      const token = res.data.access_token;
      localStorage.setItem("token", token);
      api.defaults.headers.common["Authorization"] = `Bearer ${token}`;

      const currentUser = await refreshUser();
      return currentUser;
    } catch (error) {
      console.error("Login failed:", error);
      throw error;
    }
  };

  const verify = async (user_id, code) => {
    try {
      const res = await api.post(
        "/auth/verify-code",
        { user_id, code },
        {
          headers: { "Content-Type": "application/json" },
        }
      );

      const token = res.data.access_token;
      localStorage.setItem("token", token);
      api.defaults.headers.common["Authorization"] = `Bearer ${token}`;

      const currentUser = await refreshUser();
      return currentUser;
    } catch (error) {
      console.error("Verification failed:", error);
      throw error;
    }
  };

  const add = async (name, description, price, image_url) => {
    const params = new FormData();
    params.append("name", name);
    params.append("description", description);
    params.append("price", price);
    params.append("image", image_url);

    const res = await api.post("/products", params, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return res.data;
  };

  const edit = async (id, name, description, price, image_url) => {
    const params = new FormData();
    params.append("name", name);
    params.append("description", description);
    params.append("price", price);
    params.append("image", image_url);

    const res = await api.put(`/products/${id}`, params, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return res.data;
  };

  const get = async (id) => {
    const res = await api.get(`/products/${id}`);
    return res.data;
  };

  const register = async (username, password, confirmPassword) => {
    const res = await api.post(
      "/auth/register",
      {
        username,
        password,
        confirm_password: confirmPassword,
      },
      {
        headers: { "Content-Type": "application/json" },
      }
    );
    return res.data;
  };

  const uploadPhoto = async (file) => {
    const params = new FormData();
    params.append("photo", file);
    const res = await api.put("/users/upload-photo", params, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return res.data.photo_url;
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        setUser,
        login,
        verify,
        logout,
        refreshUser,
        add,
        edit,
        get,
        register,
        uploadPhoto,
        isTokenValid,
        loading,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
