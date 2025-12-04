import React, {useEffect, useState, useContext} from "react";
import {useParams, useNavigate} from "react-router-dom";
import {AuthContext} from "../methods/ApiMethods.jsx";
import Header from "../layouts/Header.jsx";
import api from "../../js/api";

const ProductPage = () => {
  const {id} = useParams();
  const {get, user} = useContext(AuthContext);
  const navigate = useNavigate();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [images, setImages] = useState([]);
  const [selectedMainImage, setSelectedMainImage] = useState(null);
  const [showCommentInput, setShowCommentInput] = useState(false);
  const [showOwnerMessage, setShowOwnerMessage] = useState(false);
  const [comment, setComment] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [windowWidth, setWindowWidth] = useState(window.innerWidth);
  const [seller, setSeller] = useState(null);
  const [sellerLoading, setSellerLoading] = useState(false);

  useEffect(() => {
    const handleResize = () => {
      setWindowWidth(window.innerWidth);
    };
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  useEffect(() => {
    const fetchProduct = async () => {
      try {
        const data = await get(id);
        setProduct(data);

        // Нормализуем данные изображений
        const normalizedImages = (data.images || []).map((img) => ({
          ...img,
          is_main:
            img.is_main === true || img.is_main === "true" || img.is_main === 1,
        }));

        // Сортируем изображения: главное первым
        const sortedImages = [...normalizedImages].sort((a, b) => {
          if (a.is_main) return -1;
          if (b.is_main) return 1;
          return 0;
        });

        setImages(sortedImages);

        // Устанавливаем главное изображение
        const mainImg =
          sortedImages.find((img) => img.is_main) || sortedImages[0];
        setSelectedMainImage(mainImg);
      } catch (err) {
        console.error("Ошибка при загрузке товара:", err);
        setError("Не удалось загрузить товар");
      } finally {
        setLoading(false);
      }
    };

    fetchProduct();
  }, [get, id]);

  // Получаем информацию о продавце
  useEffect(() => {
    const fetchSeller = async () => {
      if (!product) return;

      // Определяем ID продавца
      const sellerId =
        product.seller_id ||
        product.user_id ||
        product.owner_id ||
        product.author_id;

      if (!sellerId) {
        console.warn("Не удалось определить ID продавца");
        return;
      }

      try {
        setSellerLoading(true);
        const res = await api.get(`/users/${sellerId}`);
        setSeller(res.data);
      } catch (err) {
        console.error("Ошибка при загрузке информации о продавце:", err);
      } finally {
        setSellerLoading(false);
      }
    };

    fetchSeller();
  }, [product]);

  // Получаем главное изображение (либо выбранное пользователем, либо помеченное как главное, либо первое)
  const mainImage =
    selectedMainImage || images.find((img) => img.is_main) || images[0];

  // Получаем остальные изображения для карусели (исключаем главное изображение)
  const mainImageId = mainImage?.id;
  const carouselImages = images.filter((img) => {
    // Исключаем изображение, которое сейчас отображается как главное
    return img.id !== mainImageId;
  });

  // Обработчик клика на изображение в карусели
  const handleImageClick = (clickedImage) => {
    setSelectedMainImage(clickedImage);
  };

  // Проверка, является ли текущий пользователь владельцем товара
  const isOwner =
    user &&
    product &&
    (product.user_id === user.id ||
      product.owner_id === user.id ||
      product.seller_id === user.id ||
      product.author_id === user.id);

  // Обработчик нажатия на кнопку "Хочу купить"
  const handleBuyClick = () => {
    // Проверка авторизации
    if (!user) {
      navigate("/login");
      return;
    }

    // Если пользователь является владельцем товара, показываем/скрываем сообщение
    if (isOwner) {
      setShowOwnerMessage(!showOwnerMessage);
      return;
    }

    setShowCommentInput(true);
  };

  // Обработчик отправки покупки
  const handlePurchaseSubmit = async () => {
    if (!product) return;

    try {
      setIsSubmitting(true);
      await api.post("/purchases", {
        product_id: product.id,
        comment: comment || "",
      });

      alert("Запрос на покупку отправлен!");
      setShowCommentInput(false);
      setComment("");
    } catch (err) {
      console.error("Ошибка при отправке запроса на покупку:", err);
      alert(
        `Не удалось отправить запрос: ${err.response?.data?.detail || err.message || "Неизвестная ошибка"}`
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div>
        <Header />
        <div
          className="d-flex justify-content-center align-items-center"
          style={{minHeight: "50vh"}}
        >
          <div className="spinner" />
        </div>
      </div>
    );
  }

  if (error || !product) {
    return (
      <div>
        <Header />
        <div
          className="d-flex justify-content-center align-items-center"
          style={{minHeight: "50vh"}}
        >
          <p className="text-danger">{error || "Товар не найден"}</p>
        </div>
      </div>
    );
  }

  return (
    <div>
      <Header />
      <div className="container py-4">
        <div className="d-flex justify-content-center">
          <div
            className="card shadow-sm"
            style={{
              maxWidth: "800px",
              width: "100%",
              borderRadius: "12px",
              overflow: "hidden",
            }}
          >
            {/* Главное изображение */}
            <div
              className="position-relative"
              style={{
                height: windowWidth < 768 ? "250px" : "400px",
                overflow: "hidden",
              }}
            >
              {mainImage && (
                <img
                  src={mainImage.url}
                  alt={product.name}
                  style={{
                    width: "100%",
                    height: "100%",
                    objectFit: "cover",
                  }}
                />
              )}
            </div>

            {/* Карусель изображений */}
            {carouselImages.length > 0 && (
              <div
                className="p-3"
                style={{
                  backgroundColor: "#f8f9fa",
                }}
              >
                <div
                  className="d-flex gap-2"
                  style={{
                    overflowX: "auto",
                    overflowY: "hidden",
                    scrollbarWidth: "thin",
                    scrollbarColor: "#ccc transparent",
                    WebkitOverflowScrolling: "touch",
                    scrollBehavior: "smooth",
                    msOverflowStyle: "-ms-autohiding-scrollbar",
                  }}
                >
                  {carouselImages.map((img) => (
                    <div
                      key={img.id}
                      className="position-relative"
                      onClick={() => handleImageClick(img)}
                      style={{
                        minWidth: "100px",
                        height: "100px",
                        borderRadius: "8px",
                        overflow: "hidden",
                        cursor: "pointer",
                        border: "2px solid transparent",
                        transition: "all 0.3s ease",
                        flexShrink: 0,
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.borderColor = "#007bff";
                        e.currentTarget.style.transform = "scale(1.05)";
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.borderColor = "transparent";
                        e.currentTarget.style.transform = "scale(1)";
                      }}
                    >
                      <img
                        src={img.url}
                        alt={`${product.name} - изображение ${img.id}`}
                        style={{
                          width: "100%",
                          height: "100%",
                          objectFit: "cover",
                        }}
                      />
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Информация о товаре */}
            <div className="p-4">
              {/* Профиль продавца */}
              {seller && (
                <div
                  className="mb-4 p-3"
                  onClick={() => {
                    const sellerId =
                      seller.id ||
                      product.seller_id ||
                      product.user_id ||
                      product.owner_id ||
                      product.author_id;
                    if (sellerId) {
                      // Если пользователь кликает на свой профиль, перенаправляем на /profile
                      if (
                        user &&
                        (seller.id === user.id || sellerId === user.id)
                      ) {
                        navigate("/profile");
                      } else {
                        navigate(`/user/${sellerId}`);
                      }
                    }
                  }}
                  style={{
                    backgroundColor: "#f8f9fa",
                    borderRadius: "8px",
                    border: "1px solid #e9ecef",
                    cursor: "pointer",
                    transition: "all 0.2s ease",
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = "#e9ecef";
                    e.currentTarget.style.borderColor = "#007bff";
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = "#f8f9fa";
                    e.currentTarget.style.borderColor = "#e9ecef";
                  }}
                >
                  <div className="d-flex align-items-center gap-3">
                    <img
                      src={seller.photo_url || "/blue-avatar.png"}
                      alt={seller.username || "Продавец"}
                      style={{
                        width: "50px",
                        height: "50px",
                        borderRadius: "50%",
                        objectFit: "cover",
                        border: "2px solid #dee2e6",
                      }}
                    />
                    <div className="d-flex flex-column">
                      <span
                        style={{
                          fontSize: "0.9rem",
                          color: "#6c757d",
                          marginBottom: "2px",
                        }}
                      >
                        Продавец
                      </span>
                      <span
                        style={{
                          fontSize: "1rem",
                          fontWeight: "500",
                          color: "#212529",
                        }}
                      >
                        {seller.username || "Неизвестно"}
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {/* Название */}
              <h2
                className="mb-3"
                style={{fontSize: "1.5rem", fontWeight: "bold"}}
              >
                {product.name}
              </h2>

              {/* Описание */}
              <p className="mb-3" style={{color: "#6c757d"}}>
                {product.description || "Описание отсутствует"}
              </p>

              {/* Цена */}
              <p
                className="mb-4"
                style={{
                  fontSize: "1.25rem",
                  fontWeight: "bold",
                  color: "#28a745",
                }}
              >
                {product.price} ₽
              </p>

              {/* Кнопка покупки и поле комментария */}
              <div className="d-flex flex-column gap-2">
                {!showCommentInput && !showOwnerMessage ? (
                  <div className="w-100 d-flex justify-content-center">
                    <button onClick={handleBuyClick}>Хочу купить</button>
                  </div>
                ) : showOwnerMessage ? (
                  <>
                    <div className="w-100 d-flex justify-content-center">
                      <button onClick={handleBuyClick}>Хочу купить</button>
                    </div>
                    <div className="w-100 d-flex justify-content-center">
                      <p
                        style={{color: "#dc3545", fontSize: "1rem", margin: 0}}
                      >
                        Ты шо еблан?:)
                      </p>
                    </div>
                  </>
                ) : (
                  <>
                    <div className="w-100 d-flex justify-content-center">
                      <input
                        type="text"
                        value={comment}
                        onChange={(e) => setComment(e.target.value)}
                        placeholder="Комментарий к покупке (необязательно)"
                        className="form-control"
                        style={{
                          maxWidth: "400px",
                          width: "100%",
                        }}
                        onKeyPress={(e) => {
                          if (e.key === "Enter" && !isSubmitting) {
                            handlePurchaseSubmit();
                          }
                        }}
                      />
                    </div>
                    <div
                      className="w-100 d-flex justify-content-center gap-2"
                      style={{
                        maxWidth: "400px",
                        width: "100%",
                        margin: "0 auto",
                      }}
                    >
                      <button
                        className="button-reverse"
                        onClick={() => {
                          setShowCommentInput(false);
                          setComment("");
                        }}
                        style={{flex: "1"}}
                      >
                        Отмена
                      </button>
                      <button
                        onClick={handlePurchaseSubmit}
                        disabled={isSubmitting}
                        style={{flex: "1"}}
                      >
                        {isSubmitting ? "Отправка..." : "Отправить"}
                      </button>
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductPage;
