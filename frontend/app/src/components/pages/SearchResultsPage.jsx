import React, {useEffect, useState} from "react";
import {useNavigate, useSearchParams} from "react-router-dom";
import api from "../../js/api";
import Header from "../layouts/Header";

export default function SearchResultsPage() {
  const [searchParams] = useSearchParams();
  const query = searchParams.get("q") || "";
  const [products, setProducts] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(false);
  const [totalCount, setTotalCount] = useState(0);

  const navigate = useNavigate();

  const handleCardClick = (id) => {
    navigate(`/product/${id}`);
  };

  useEffect(() => {
    const fetchSearchResults = async () => {
      if (!query.trim()) {
        setIsLoading(false);
        return;
      }

      try {
        setIsLoading(true);
        setError(false);
        const response = await api.get("/products/search/", {
          params: {
            query: query,
            limit: 10,
            offset: 0,
          },
        });

        const items = Array.isArray(response.data?.items)
          ? response.data.items
          : [];
        setProducts(items);
        setTotalCount(response.data?.total_count || 0);
      } catch (err) {
        console.error("Search failed:", err);
        setError(true);
      } finally {
        setIsLoading(false);
      }
    };

    fetchSearchResults();
  }, [query]);

  if (isLoading)
    return (
      <div>
        <Header />
        <div className="spinner" />
      </div>
    );

  if (error)
    return (
      <div>
        <Header />
        <div className="container py-4">
          <p>Не удалось выполнить поиск</p>
        </div>
      </div>
    );

  return (
    <div>
      <Header />
      <div className="container py-4">
        {query && (
          <h4 className="mb-4">
            Результаты поиска по запросу: "{query}" ({totalCount})
          </h4>
        )}
        {products.length === 0 ? (
          <p>Товары не найдены</p>
        ) : (
          <div
            className="product-grid"
            style={{
              display: "grid",
              gap: "16px",
              gridTemplateColumns: "repeat(auto-fill, minmax(220px, 220px))",
              justifyContent: "start",
            }}
          >
            {products.map((p) => (
              <div
                key={p.id}
                className="product-wrapper"
                onClick={() => handleCardClick(p.id)}
                style={{
                  width: "220px",
                  maxWidth: "220px",
                }}
              >
                <div
                  className="card product-card"
                  style={{
                    borderRadius: "12px",
                    overflow: "hidden",
                    transition: "transform 0.3s ease, box-shadow 0.3s ease",
                    width: "100%",
                    maxWidth: "220px",
                  }}
                >
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
        )}
      </div>
    </div>
  );
}
