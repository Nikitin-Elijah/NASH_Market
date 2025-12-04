import {useEffect, useState, useContext} from "react";
import {useNavigate} from "react-router-dom";
import {AuthContext} from "./ApiMethods.jsx";
import "bootstrap-icons/font/bootstrap-icons.css";
import api from "../../js/api";

export default function ProductList() {
  const [products, setProducts] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(false);
  const {user} = useContext(AuthContext);
  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await api.get(`/products?user_id=${user.id}`);
        setProducts(response.data);
      } catch (err) {
        console.error(err);
        setError(true);
      } finally {
        setIsLoading(false);
      }
    };

    fetchProducts();
  }, []);
  const navigate = useNavigate();

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
  if (isLoading) return <p>Загрузка...</p>;
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
    </div>
  );
}
