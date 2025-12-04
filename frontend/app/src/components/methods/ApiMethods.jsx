import {createContext, useState, useEffect} from "react";
import api from "../../js/api";

export const AuthContext = createContext();

export const AuthProvider = ({children}) => {
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
        const res = await api.get("/users/me/");
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
      const res = await api.get("/users/me/");
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
        headers: {"Content-Type": "application/x-www-form-urlencoded"},
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
        "/reg/verify-code/",
        {user_id, code},
        {
          headers: {"Content-Type": "application/json"},
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

  const add = async (name, description, price, images) => {
    try {
      const params = new FormData();

      // Добавляем каждый файл с ключом "images" для поддержки нескольких изображений
      if (Array.isArray(images)) {
        images.forEach((image) => {
          params.append("images", image);
        });
      } else if (images) {
        // Обратная совместимость: если передан один файл
        params.append("images", images);
      }

      const queryParams = new URLSearchParams({
        name: name,
        description: description,
        price: price,
      });

      const res = await api.post(
        `/products/?${queryParams.toString()}`,
        params,
        {
          headers: {
            "Content-Type": "multipart/form-data",
            accept: "application/json",
          },
        }
      );
      return res.data;
    } catch (error) {
      console.error("Add product failed:", error);
      throw error;
    }
  };

  const edit = async (
    id,
    name,
    description,
    price,
    image_url,
    main_image_id
  ) => {
    try {
      const queryParams = new URLSearchParams({
        name: name,
        description: description,
        price: price,
      });

      if (main_image_id !== undefined && main_image_id !== null) {
        queryParams.append("main_image_id", main_image_id);
        console.log("Добавлен main_image_id в запрос:", main_image_id);
      } else {
        console.log("main_image_id не передан или равен null/undefined");
      }

      console.log(
        "Query параметры для редактирования:",
        queryParams.toString()
      );

      // Если есть новое изображение для загрузки, используем FormData
      if (image_url) {
        const params = new FormData();
        params.append("image", image_url);

        const res = await api.put(
          `/products/${id}?${queryParams.toString()}`,
          params,
          {
            headers: {"Content-Type": "multipart/form-data"},
          }
        );
        console.log("Ответ от PUT запроса (с изображением):", res.data);
        return res.data;
      } else {
        // Если нет нового изображения, отправляем только query параметры
        const res = await api.put(
          `/products/${id}?${queryParams.toString()}`,
          null,
          {
            headers: {accept: "application/json"},
          }
        );
        console.log("Ответ от PUT запроса (без изображения):", res.data);
        return res.data;
      }
    } catch (error) {
      console.error("Edit product failed:", error);
      console.error("Детали ошибки:", error.response?.data);
      throw error;
    }
  };

  const get = async (id) => {
    try {
      const res = await api.get(`/products/${id}`);
      return res.data;
    } catch (error) {
      console.error("Get product failed:", error);
      throw error;
    }
  };

  const deleteProduct = async (id) => {
    try {
      const res = await api.delete(`/products/${id}`);
      return res.data;
    } catch (error) {
      console.error("Delete product failed:", error);
      throw error;
    }
  };

  const register = async (username, password, confirmPassword) => {
    try {
      const res = await api.post(
        "/reg/register/",
        {
          username,
          password,
          confirm_password: confirmPassword,
        },
        {
          headers: {"Content-Type": "application/json"},
        }
      );
      return res.data;
    } catch (error) {
      console.error("Register failed:", error);
      throw error;
    }
  };

  const uploadPhoto = async (file) => {
    try {
      const params = new FormData();
      params.append("photo", file);
      const res = await api.put("/users/upload-photo/", params, {
        headers: {"Content-Type": "multipart/form-data"},
      });
      return res.data.photo_url;
    } catch (error) {
      console.error("Upload photo failed:", error);
      throw error;
    }
  };

  const getFavorites = async () => {
    try {
      const res = await api.get("/users/favorites/");
      return res.data;
    } catch (error) {
      console.error("Get favorites failed:", error);
      throw error;
    }
  };

  const getProduct = async (productId) => {
    try {
      const res = await api.get(`/products/${productId}`);
      return res.data;
    } catch (error) {
      console.error("Get product failed:", error);
      throw error;
    }
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
        deleteProduct,
        register,
        uploadPhoto,
        getFavorites,
        getProduct,
        isTokenValid,
        loading,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
