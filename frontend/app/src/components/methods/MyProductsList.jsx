import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
const PRODUCTS_URL = "http://127.0.0.1:8000/products/my";

export default function ProductList() {
  const [products, setProducts] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await fetch(PRODUCTS_URL, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
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
  const navigate = useNavigate();

  const handleAddProduct = () => {
    navigate("/add-product");
  };
  const handleEdit = (id) => {
    navigate(`/edit-product/${id}`);
  };
  const handleDelete = async (id) => {
    if (window.confirm("Вы уверены, что хотите удалить этот товар?")) {
      try {
        const response = await fetch(`http://127.0.0.1:8000/products/${id}`, {
          method: "DELETE",
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        if (!response.ok) {
          throw new Error("Ошибка при удалении товара");
        }
        setProducts(products.filter((product) => product.id !== id));
      } catch (err) {
        console.error(err);
        setError(true);
      }
    }
  };
  if (isLoading) return <p>Загрузка...</p>;
  if (error || products.length === 0) return (
    <div className="d-flex flex-column align-items-center m-5">
      <p className="d-flex flex-column align-items-center">У вас пока нет товаров, но вы можете добавить их.</p>
      <button className='btn btn-primary m-2' onClick={handleAddProduct}>Добавить товары</button>
    </div>
  );

  return (
  <div className="row row-cols-2 row-cols-sm-4 row-cols-md-5 row-cols-lg-6 g-3 m-2">
    {products.map((product) => (
      <div className="col" key={product.id}>
        <div
          className="item position-relative card"
          style={{
            transition: "transform 0.3s ease",
            cursor: "pointer",
          }}
          onMouseEnter={(e) => (e.currentTarget.style.transform = "scale(1.05)")}
          onMouseLeave={(e) => (e.currentTarget.style.transform = "scale(1)")}
        >
          <div className="position-absolute top-0 end-0 m-2">
            <button
              className="btn btn-light opacity-75 me-2"
              onClick={() => handleEdit(product.id)}
            >
              <i className="bi bi-pencil"></i>
            </button>
            <button
              className="btn btn-light opacity-75"
              onClick={() => handleDelete(product.id)}
            >
              <i className="bi bi-trash"></i>
            </button>
          </div>

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