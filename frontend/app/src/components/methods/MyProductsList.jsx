import {useEffect, useState, useContext, useRef, useCallback} from "react";
import {useNavigate} from "react-router-dom";
import {AuthContext} from "./ApiMethods.jsx";
import "bootstrap-icons/font/bootstrap-icons.css";
import api from "../../js/api";

/**
 * Хук для бесконечной прокрутки товаров пользователя
 * @param {Function} onLoadMore - Callback функция, вызываемая при загрузке новых товаров
 * @param {number} userId - ID пользователя
 * @returns {Object} Объект с функциями и состоянием для пагинации
 */
function usePaginatedUserProducts(onLoadMore, userId) {
  const [nextPageOffset, setNextPageOffset] = useState(null);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const observerTarget = useRef(null);

  /**
   * Загружает следующую страницу товаров пользователя
   */
  const loadMore = useCallback(async () => {
    if (
      !hasMore ||
      isLoadingMore ||
      nextPageOffset === null ||
      nextPageOffset === undefined ||
      !userId
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

      // Вызываем callback с новыми товарами
      if (onLoadMore) {
        onLoadMore(items);
      }

      // Обновляем offset для следующей загрузки
      if (newNextPageOffset !== null && newNextPageOffset !== undefined) {
        setNextPageOffset(newNextPageOffset);
        setHasMore(true);
      } else {
        setHasMore(false);
      }
    } catch (err) {
      console.error("Ошибка при загрузке товаров пользователя:", err);
      setHasMore(false);
    } finally {
      setIsLoadingMore(false);
    }
  }, [nextPageOffset, hasMore, isLoadingMore, onLoadMore, userId]);

  /**
   * Инициализирует пагинацию с начальным offset
   * @param {number|null} initialOffset - Начальный offset из первого запроса
   */
  const initializePagination = useCallback((initialOffset) => {
    if (initialOffset !== null && initialOffset !== undefined) {
      setNextPageOffset(initialOffset);
      setHasMore(true);
    } else {
      setHasMore(false);
    }
  }, []);

  /**
   * Настройка Intersection Observer для отслеживания последнего элемента
   */
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
}

export default function ProductList() {
  const [products, setProducts] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(false);
  const {user} = useContext(AuthContext);
  const navigate = useNavigate();

  // Callback для добавления новых товаров при пагинации
  const handleLoadMore = (newProducts) => {
    setProducts((prevProducts) => [...prevProducts, ...newProducts]);
  };

  // Хук для пагинации
  const {observerTarget, isLoadingMore, hasMore, initializePagination} =
    usePaginatedUserProducts(handleLoadMore, user?.id);

  useEffect(() => {
    if (!user?.id) {
      setIsLoading(false);
      return;
    }

    const fetchProducts = async () => {
      try {
        const response = await api.get(`/products/user/${user.id}`, {
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
  }, [user?.id]);

  const handleCardClick = (id) => {
    navigate(`/edit-product/${id}`);
  };
  const handleAddProduct = () => {
    navigate("/add-product");
  };

  const handleDelete = async (id) => {
    if (window.confirm("Вы уверены, что хотите удалить этот товар?")) {
      try {
        await api.delete(`/products/${id}`);
        setProducts(products.filter((product) => product.id !== id));
      } catch (err) {
        console.error(err);
        setError(true);
      }
    }
  };

  if (isLoading) return <div className="spinner" />;
  if (error || products.length === 0)
    return (
      <div className="d-flex flex-column align-items-center m-5">
        <p className="d-flex flex-column align-items-center">
          У вас пока нет товаров, но вы можете добавить их.
        </p>
        <button className="" onClick={handleAddProduct}>
          Добавить товары
        </button>
      </div>
    );

  return (
    <div className="container py-4">
      <div className="product-grid">
        {products.map((p) => (
          <div
            key={p.id}
            className="product-wrapper position-relative"
            style={{cursor: "pointer"}}
            onClick={() => handleCardClick(p.id)}
          >
            <div
              className="card product-card border-0 shadow-sm position-relative"
              style={{
                borderRadius: "12px",
                overflow: "hidden",
                transition: "transform 0.3s ease, box-shadow 0.3s ease",
              }}
            >
              <div
                className="card-buttons position-absolute top-0 end-0 m-2 d-flex gap-1"
                onClick={(e) => e.stopPropagation()}
              ></div>
              <div style={{height: "200px", overflow: "hidden"}}>
                <img
                  src={
                    p.images?.find?.((img) => {
                      const isMain =
                        img.is_main === true ||
                        img.is_main === "true" ||
                        img.is_main === 1;
                      return isMain;
                    })?.url ||
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
    </div>
  );
}
