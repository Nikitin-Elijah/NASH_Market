import React, { useEffect, useState } from "react";
import './style.css'
const PRODUCTS_URL = "http://127.0.0.1:8000/products/";

export default function ProductList() {
  const [products, setProducts] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(false);

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

  if (isLoading) return <p>Загрузка...</p>;
  if (error || products.length === 0) return <p>Не удалось загрузить товары</p>;

  return (
    <div className="row row-cols-1 row-cols-md-4 g-4">
      {products.map((product) => (
        <div className="col" key={product.id}>
          <div
          className="item h-90"
          style={{
            transition: 'transform 0.3s ease',
            cursor: 'pointer'
          }}
          onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.05)'}
          onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
          >
            <img
              src={product.image_url}
              alt={product.name}
              className="img-fluid"
              style={{ height: "200px", objectFit: "cover" }}
              />
            <div className="card-body d-flex flex-column align-items-start text-break">
              <span className="card-title m-2 text-bold">{product.name}</span>
              {/* <span className="card-title m-2 text-bold text-wrap">{product.description}</span> */}
              <p className="card-text m-2">{product.price} ₽</p>
            </div>
          </div>
        </div>
      ))}
     </div>
  );
}
