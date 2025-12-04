import {useEffect, useRef, useState, useCallback} from "react";
import api from "../../js/api";

/**
 * Хук для бесконечной прокрутки товаров
 * @param {Function} onLoadMore - Callback функция, вызываемая при загрузке новых товаров
 * @returns {Object} Объект с функциями и состоянием для пагинации
 */
export function usePaginatedProducts(onLoadMore) {
  const [nextPageOffset, setNextPageOffset] = useState(null);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const observerTarget = useRef(null);

  /**
   * Загружает следующую страницу товаров
   */
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
      const response = await api.get("/products/", {
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
      // Проверяем, что есть следующая страница (offset может быть 0, но не null/undefined)
      if (newNextPageOffset !== null && newNextPageOffset !== undefined) {
        setNextPageOffset(newNextPageOffset);
        setHasMore(true); // Если есть next_page_offset, значит есть следующая страница
      } else {
        setHasMore(false); // Нет следующей страницы
      }
    } catch (err) {
      console.error("Ошибка при загрузке товаров:", err);
      setHasMore(false);
    } finally {
      setIsLoadingMore(false);
    }
  }, [nextPageOffset, hasMore, isLoadingMore, onLoadMore]);

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
        rootMargin: "100px", // Начинаем загрузку за 100px до конца
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
