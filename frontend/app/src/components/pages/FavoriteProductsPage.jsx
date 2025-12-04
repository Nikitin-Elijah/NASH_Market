import React, {useEffect, useState, useContext} from "react";
import {useNavigate} from "react-router-dom";
import {AuthContext} from "../methods/ApiMethods";
import Header from "../layouts/Header";
import api from "../../js/api";
import "bootstrap-icons/font/bootstrap-icons.css";

export default function FavoriteProductsPage() {
  const [products, setProducts] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(false);
  const [removedFromFavorites, setRemovedFromFavorites] = useState(new Set());
  const {getFavorites, user} = useContext(AuthContext);

  const navigate = useNavigate();

  const handleCardClick = (id) => {
    navigate(`/product/${id}`);
  };

  // Обработчик клика на сердечко - переключает состояние избранного
  const handleFavoriteClick = async (e, productId) => {
    e.stopPropagation(); // Предотвращаем переход на страницу товара

    if (!user) {
      navigate("/login");
      return;
    }

    const isRemoved = removedFromFavorites.has(productId);

    try {
      if (isRemoved) {
        // Возвращаем в избранное
        await api.post(`/users/favorites/${productId}`);
        setRemovedFromFavorites((prev) => {
          const newSet = new Set(prev);
          newSet.delete(productId);
          return newSet;
        });
      } else {
        // Удаляем из избранного
        await api.delete(`/users/favorites/${productId}/`);
        setRemovedFromFavorites((prev) => new Set([...prev, productId]));
      }
    } catch (err) {
      console.error("Failed to toggle favorite:", err);
    }
  };

  useEffect(() => {
    const fetchFavorites = async () => {
      try {
        const data = await getFavorites();
        // Проверяем структуру ответа - может быть массив или объект с items
        const items = Array.isArray(data) ? data : data?.items || [];
        setProducts(items);
      } catch (err) {
        console.error(err);
        setError(true);
      } finally {
        setIsLoading(false);
      }
    };

    fetchFavorites();
  }, [getFavorites]);

  if (isLoading)
    return (
      <div>
        <Header />
        <div className="spinner" />
      </div>
    );
  if (error || products.length === 0)
    return (
      <div>
        <Header />
        <div
          style={{
            height: "200px",
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            alignItems: "center",
            gap: "16px",
          }}
        >
          <p>У вас пока нет избранных товаров</p>
          <button className="" onClick={() => navigate("/")}>
            Вернуться на главную
          </button>
        </div>
      </div>
    );

  return (
    <div>
      <Header />
      <div className="container py-4">
        <div className="product-grid">
          {products.map((p) => {
            // Определяем ID товара (может быть id, product_id или product.id)
            const productId = p.id || p.product_id || p.product?.id;
            return (
              <div
                key={productId}
                className="product-wrapper"
                onClick={() => handleCardClick(productId)}
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
                    onClick={(e) => handleFavoriteClick(e, productId)}
                  >
                    <i
                      className={`bi ${
                        removedFromFavorites.has(productId)
                          ? "bi-heart"
                          : "bi-heart-fill"
                      }`}
                    />
                  </div>
                  <div style={{height: "200px", overflow: "hidden"}}>
                    <img
                      src={
                        (p.images || p.product?.images)?.find?.(
                          (img) => img.is_main
                        )?.url ||
                        ((p.images || p.product?.images) &&
                          (p.images || p.product?.images)[0]?.url) ||
                        ""
                      }
                      alt={p.name || p.product?.name}
                      style={{
                        height: "100%",
                        width: "100%",
                        objectFit: "cover",
                        transition: "transform 0.4s ease",
                      }}
                    />
                  </div>
                  <div className="d-flex flex-column justify-content-center">
                    <span className="m-2 mb-0">
                      {p.name || p.product?.name}
                    </span>
                    <p className="fw-bold m-2 mt-0">
                      {p.price || p.product?.price}
                    </p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
