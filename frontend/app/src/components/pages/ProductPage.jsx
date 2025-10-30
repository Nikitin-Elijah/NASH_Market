import React, {useEffect, useState, useContext} from "react";
import {AuthContext} from "../methods/ApiMethods.jsx";
import Header from "../layouts/Header.jsx";

const ProductPage = () => {
  const {get} = useContext(AuthContext);
  const [p, setProduct] = useState(null);
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

  if (!p) {
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
          className="card product-card border-0 shadow-sm"
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
            <p className="fw-bold m-2 mt-0">{p.price} ₽</p>
          </div>
        <div className="w-100 d-flex justify-content-center mt-2">
          <button className="">Откликнуться</button>
        </div>
        </div>
      </div>
    </div>
  );
};

export default ProductPage;
