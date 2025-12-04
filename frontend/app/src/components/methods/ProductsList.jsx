import React, {useEffect, useState, useContext} from "react";
import {useNavigate} from "react-router-dom";
import api from "../../js/api";
import {usePaginatedProducts} from "./PaginatedProducts.jsx";
import {AuthContext} from "./ApiMethods.jsx";
import "bootstrap-icons/font/bootstrap-icons.css";

export default function ProductList() {
  const [products, setProducts] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(false);
  const [favoriteIds, setFavoriteIds] = useState(new Set());
  const {user, getFavorites} = useContext(AuthContext);

  const navigate = useNavigate();

  const handleCardClick = (id) => {
    navigate(`/product/${id}`);
  };

  // Загрузка избранных товаров при монтировании компонента
  useEffect(() => {
    const loadFavorites = async () => {
      if (!user) return;
      try {
        const data = await getFavorites();
        const items = Array.isArray(data) ? data : data?.items || [];
        const favoriteIdsSet = new Set(
          items.map((item) => item.id || item.product_id)
        );
        setFavoriteIds(favoriteIdsSet);
      } catch (err) {
        console.error("Failed to load favorites:", err);
      }
    };
    loadFavorites();
  }, [user, getFavorites]);

  // Обработчик клика на сердечко
  const handleFavoriteClick = async (e, productId) => {
    e.stopPropagation(); // Предотвращаем переход на страницу товара

    if (!user) {
      navigate("/login");
      return;
    }

    const isFavorite = favoriteIds.has(productId);

    try {
      if (isFavorite) {
        // Удаляем из избранного
        await api.delete(`/users/me/favorites/${productId}`);
        setFavoriteIds((prev) => {
          const newSet = new Set(prev);
          newSet.delete(productId);
          return newSet;
        });
      } else {
        // Добавляем в избранное
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

  // Хук для пагинации
  const {observerTarget, isLoadingMore, hasMore, initializePagination} =
    usePaginatedProducts(handleLoadMore);

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await api.get("/products", {
          params: {
            limit: 10,
            offset: 0,
          },
        });
        // API возвращает объект пагинации: { items, total_count, limit, next_page_offset }
        const items = Array.isArray(response.data?.items)
          ? response.data.items
          : [];
        setProducts(items);

        // Инициализируем пагинацию с next_page_offset из ответа
        const nextPageOffset = response.data?.next_page_offset;
        initializePagination(nextPageOffset);
      } catch (err) {
        console.error(err);
        setError(true);
      } finally {
        setIsLoading(false);
      }
    };

    fetchProducts();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Загружаем только при монтировании компонента

  if (isLoading) return <div className="spinner" />;
  if (error || products.length === 0) return <p>Не удалось загрузить товары</p>;

  return (
    <div className="container py-4">
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
                <p className="fw-bold m-2 mt-0">{p.price}</p>
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
    </div>
  );
}
