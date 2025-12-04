import React, {
  useEffect,
  useState,
  useRef,
  useCallback,
  useContext,
} from "react";
import {useParams, useNavigate} from "react-router-dom";
import Header from "../layouts/Header.jsx";
import api from "../../js/api";
import {AuthContext} from "../methods/ApiMethods.jsx";
import "bootstrap-icons/font/bootstrap-icons.css";

// Кастомный хук для пагинации товаров пользователя
const useUserPaginatedProducts = (userId, onLoadMore) => {
  const [nextPageOffset, setNextPageOffset] = useState(null);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const observerTarget = useRef(null);

  const loadMore = useCallback(async () => {
    if (
      !hasMore ||
      isLoadingMore ||
      nextPageOffset === null ||
      nextPageOffset === undefined
    ) {
      return;
    }

    setIsLoadingMore(true);
    try {
      const response = await api.get(`/products/user/${userId}`, {
        params: {
          limit: 10,
          offset: nextPageOffset,
        },
      });

      const items = Array.isArray(response.data?.items)
        ? response.data.items
        : [];
      const newNextPageOffset = response.data?.next_page_offset;

      if (onLoadMore) {
        onLoadMore(items);
      }

      if (newNextPageOffset !== null && newNextPageOffset !== undefined) {
        setNextPageOffset(newNextPageOffset);
        setHasMore(true);
      } else {
        setHasMore(false);
      }
    } catch (err) {
      console.error("Ошибка при загрузке товаров:", err);
      setHasMore(false);
    } finally {
      setIsLoadingMore(false);
    }
  }, [nextPageOffset, hasMore, isLoadingMore, onLoadMore, userId]);

  const initializePagination = useCallback((initialOffset) => {
    if (initialOffset !== null && initialOffset !== undefined) {
      setNextPageOffset(initialOffset);
      setHasMore(true);
    } else {
      setHasMore(false);
    }
  }, []);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && hasMore && !isLoadingMore) {
          loadMore();
        }
      },
      {
        root: null,
        rootMargin: "100px",
        threshold: 0.1,
      }
    );

    const currentTarget = observerTarget.current;
    if (currentTarget) {
      observer.observe(currentTarget);
    }

    return () => {
      if (currentTarget) {
        observer.unobserve(currentTarget);
      }
    };
  }, [hasMore, isLoadingMore, loadMore]);

  return {
    observerTarget,
    isLoadingMore,
    hasMore,
    initializePagination,
    loadMore,
  };
};

const UserPage = () => {
  const {id} = useParams();
  const navigate = useNavigate();
  const {user: currentUser} = useContext(AuthContext);
  const [user, setUser] = useState(null);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [favoriteIds, setFavoriteIds] = useState(new Set());

  // Загрузка избранных товаров
  useEffect(() => {
    const loadFavorites = async () => {
      try {
        const token = localStorage.getItem("token");
        if (!token) return;

        const data = await api.get("/users/me/favorites");
        const items = Array.isArray(data.data)
          ? data.data
          : data.data?.items || [];
        const favoriteIdsSet = new Set(
          items.map((item) => item.id || item.product_id)
        );
        setFavoriteIds(favoriteIdsSet);
      } catch (err) {
        // Игнорируем ошибки, если пользователь не авторизован
        console.error("Failed to load favorites:", err);
      }
    };
    loadFavorites();
  }, []);

  // Загрузка данных пользователя
  useEffect(() => {
    // Если пользователь открывает свою собственную страницу, перенаправляем на /profile
    if (
      currentUser &&
      id &&
      (currentUser.id === parseInt(id) || currentUser.id.toString() === id)
    ) {
      navigate("/profile");
      return;
    }

    const fetchUser = async () => {
      try {
        setLoading(true);
        const res = await api.get(`/users/${id}`);
        setUser(res.data);
      } catch (err) {
        console.error("Ошибка при загрузке пользователя:", err);
        setError("Не удалось загрузить данные пользователя");
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, [id, currentUser, navigate]);

  // Обработчик клика на карточку товара
  const handleCardClick = (productId) => {
    navigate(`/product/${productId}`);
  };

  // Обработчик клика на сердечко
  const handleFavoriteClick = async (e, productId) => {
    e.stopPropagation();

    const token = localStorage.getItem("token");
    if (!token) {
      navigate("/login");
      return;
    }

    const isFavorite = favoriteIds.has(productId);

    try {
      if (isFavorite) {
        await api.delete(`/users/me/favorites/${productId}`);
        setFavoriteIds((prev) => {
          const newSet = new Set(prev);
          newSet.delete(productId);
          return newSet;
        });
      } else {
        await api.post(`/users/me/favorites/${productId}`);
        setFavoriteIds((prev) => new Set([...prev, productId]));
      }
    } catch (err) {
      console.error("Failed to toggle favorite:", err);
    }
  };

  // Callback для добавления новых товаров при пагинации
  const handleLoadMore = (newProducts) => {
    setProducts((prevProducts) => [...prevProducts, ...newProducts]);
  };

  const {observerTarget, isLoadingMore, hasMore, initializePagination} =
    useUserPaginatedProducts(id, handleLoadMore);

  // Загрузка товаров пользователя
  useEffect(() => {
    const fetchProducts = async () => {
      if (!id) return;

      try {
        const response = await api.get(`/products/user/${id}`, {
          params: {
            limit: 10,
            offset: 0,
          },
        });

        const items = Array.isArray(response.data?.items)
          ? response.data.items
          : [];
        setProducts(items);

        const nextPageOffset = response.data?.next_page_offset;
        initializePagination(nextPageOffset);
      } catch (err) {
        console.error("Ошибка при загрузке товаров:", err);
      }
    };

    fetchProducts();
  }, [id, initializePagination]);

  if (loading) {
    return (
      <div>
        <Header />
        <div
          className="d-flex justify-content-center align-items-center"
          style={{minHeight: "50vh"}}
        >
          <div className="spinner" />
        </div>
      </div>
    );
  }

  if (error || !user) {
    return (
      <div>
        <Header />
        <div
          className="d-flex justify-content-center align-items-center"
          style={{minHeight: "50vh"}}
        >
          <p className="text-danger">{error || "Пользователь не найден"}</p>
        </div>
      </div>
    );
  }

  return (
    <div>
      <Header />
      <div className="container py-4">
        {/* Профиль пользователя */}
        <div className="mb-4">
          <div className="w-100 d-flex flex-row justify-content-start align-items-center">
            <div>
              <img
                src={user.photo_url || "/blue-avatar.png"}
                alt={user.username || "avatar"}
                style={{
                  width: "100px",
                  height: "100px",
                  borderRadius: "50%",
                  objectFit: "cover",
                  display: "block",
                }}
                className="m-2"
              />
            </div>
            <div className="d-flex flex-column justify-content-center m-2">
              <h5 className="text fs-3">{user.username}</h5>
              <span className="text fs-5">@{user.username}</span>
            </div>
          </div>
        </div>

        {/* Список товаров */}
        <div>
          <h3 className="mb-3">Товары продавца</h3>
          {products.length === 0 ? (
            <p className="text-muted">У этого продавца пока нет товаров</p>
          ) : (
            <>
              <div className="product-grid">
                {products.map((p) => (
                  <div
                    key={p.id}
                    className="product-wrapper"
                    onClick={() => handleCardClick(p.id)}
                  >
                    <div
                      className="card product-card"
                      style={{
                        borderRadius: "12px",
                        overflow: "hidden",
                        transition: "transform 0.3s ease, box-shadow 0.3s ease",
                      }}
                    >
                      <div
                        className="favorite-button"
                        onClick={(e) => handleFavoriteClick(e, p.id)}
                      >
                        <i
                          className={`bi ${
                            favoriteIds.has(p.id) ? "bi-heart-fill" : "bi-heart"
                          }`}
                        />
                      </div>
                      <div style={{height: "200px", overflow: "hidden"}}>
                        <img
                          src={
                            p.images?.find?.((img) => img.is_main)?.url ||
                            (p.images && p.images[0]?.url) ||
                            ""
                          }
                          alt={p.name}
                          style={{
                            height: "100%",
                            width: "100%",
                            objectFit: "cover",
                            transition: "transform 0.4s ease",
                          }}
                        />
                      </div>
                      <div className="d-flex flex-column justify-content-center">
                        <span className="m-2 mb-0">{p.name}</span>
                        <p className="fw-bold m-2 mt-0">{p.price} ₽</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              {/* Элемент-наблюдатель для бесконечной прокрутки */}
              {hasMore && (
                <div
                  ref={observerTarget}
                  style={{
                    height: "20px",
                    width: "100%",
                    display: "flex",
                    justifyContent: "center",
                    alignItems: "center",
                    padding: "20px",
                  }}
                >
                  {isLoadingMore && <div className="spinner" />}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default UserPage;
