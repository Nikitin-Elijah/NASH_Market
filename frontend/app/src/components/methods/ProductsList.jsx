import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import '../style.css'
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
  <div className="row row-cols-2 row-cols-sm-3 row-cols-md-5 row-cols-lg-6 g-3 m-2">
    {products.map((product) => (
      <div className="col" key={product.id}>
        <div
          className="item position-relative card"
          style={{
            transition: "transform 0.3s ease",
            cursor: "pointer",
            height: "85%"
          }}
          onClick={() => handleCardClick(product.id)} 
          onMouseEnter={(e) => (e.currentTarget.style.transform = "scale(1.05)")}
          onMouseLeave={(e) => (e.currentTarget.style.transform = "scale(1)")}
        >
          <img
            src={product.image_url}
            alt={product.name}
            className="card-img-top"
            style={{ height: "150px", objectFit: "cover" }}
          />

          <div className="d-flex flex-column align-items-start text-break p-2">
            <span className="text fs-6">{product.name}</span>
            <p className="text fs-6">{product.price} ₽</p>
          </div>
        </div>
      </div>
    ))}
  </div>
);

}
