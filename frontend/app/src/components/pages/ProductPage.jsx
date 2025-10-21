import React, { useEffect, useState, useContext } from "react";
import { AuthContext } from "../methods/ApiMethods.jsx";
import Header from "./Header";

const ProductPage = () => {
  const { get } = useContext(AuthContext);
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchProduct = async () => {
      try {
        const id = window.location.pathname.split("/").pop();
        const data = await get(id);
        console.log("Загруженный товар:", data);
        setProduct(data);
      } catch (err) {
        console.error("Ошибка при загрузке товара:", err);
        setError("Не удалось загрузить товар");
      } finally {
        setLoading(false);
      }
    };

    fetchProduct();
  }, [get]);

  if (loading) {
    return (
      <div>
        <Header />
        <p className="text-center mt-5">Загрузка...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div>
        <Header />
        <p className="text-center text-danger mt-5">{error}</p>
      </div>
    );
  }

  if (!product) {
    return (
      <div>
        <Header />
        <p className="text-center mt-5">Товар не найден</p>
      </div>
    );
  }

  return (
    <div>
      <Header />
      <div className="container d-flex justify-content-center align-items-center mt-5">
        <div
          className="item position-relative card mx-auto"
          style={{
            width: "300px",
            transition: "transform 0.3s ease",
            cursor: "pointer",
          }}
          onMouseEnter={(e) => (e.currentTarget.style.transform = "scale(1.05)")}
          onMouseLeave={(e) => (e.currentTarget.style.transform = "scale(1)")}
        >
          <img
            src={product.image_url}
            alt={product.name}
            className="card-img-top"
            style={{ height: "200px", objectFit: "cover" }}
          />

          <div className="card-body d-flex flex-column align-items-start text-break">
            <h5 className="card-title">{product.name}</h5>
            {product.description && (
                <p className="card-text text-muted">{product.description}</p>
            )}
            <p className="card-text">{product.price} ₽</p>
            <div className="w-100 d-flex justify-content-center mt-2">
                <button className="btn btn-primary">Откликнуться</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductPage;
