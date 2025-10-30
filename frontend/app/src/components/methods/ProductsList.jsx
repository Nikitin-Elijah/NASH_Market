import React, {useEffect, useState} from "react";
import {useNavigate} from "react-router-dom";

const PRODUCTS_URL = "http://127.0.0.1:8000/products/";

export default function ProductList() {
  const [products, setProducts] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(false);

  const navigate = useNavigate();

  const handleCardClick = (id) => {
    navigate(`/product/${id}`);
  };
  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await fetch(PRODUCTS_URL);
        if (!response.ok) {
          throw new Error("Ошибка при загрузке");
        }
        const data = await response.json();
        setProducts(data);
      } catch (err) {
        console.error(err);
        setError(true);
      } finally {
        setIsLoading(false);
      }
    };

    fetchProducts();
  }, []);

  if (isLoading) return <div className="spinner" />;
  if (error || products.length === 0) return <p>Не удалось загрузить товары</p>;

  return (
    <div className="container py-4">
      <div className="product-grid">
        {products.map((p) => (
          <div key={p.id} className="product-wrapper"
          onClick={() => handleCardClick(p.id)}>
            <div
              className="card product-card"
              style={{
                borderRadius: "12px",
                overflow: "hidden",
                transition: "transform 0.3s ease, box-shadow 0.3s ease",
              }}
            >
              <div style={{height: "200px", overflow: "hidden"}}>
                <img
                  src={p.image_url}
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
    </div>
  );
}
