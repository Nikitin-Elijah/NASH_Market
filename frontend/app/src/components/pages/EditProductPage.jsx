import React, {useContext, useState, useEffect, useRef} from "react";
import {useNavigate, useParams} from "react-router-dom";
import {AuthContext} from "../methods/ApiMethods.jsx";
import Header from "../layouts/Header.jsx";
import api from "../../js/api";

const EditProductPage = () => {
  const {edit, get, deleteProduct} = useContext(AuthContext);
  const navigate = useNavigate();
  const {id: productId} = useParams();

  const [isEditing, setIsEditing] = useState(false);
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Состояния для редактирования
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [price, setPrice] = useState("");
  const [images, setImages] = useState([]);
  const [isUploadingImage, setIsUploadingImage] = useState(false);
  const fileInputRef = useRef(null);

  useEffect(() => {
    const fetchProduct = async () => {
      try {
        const res = await get(productId);
        console.log("Загружен продукт:", res);
        console.log("Изображения продукта:", res.images);
        setProduct(res);
        setName(res.name || "");
        setDescription(res.description || "");
        setPrice(res.price || "");
        // Нормализуем данные изображений (на случай, если is_main приходит как строка или число)
        const normalizedImages = (res.images || []).map((img) => ({
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
        console.log("Отсортированные изображения:", sortedImages);
        const mainImg = sortedImages.find((img) => img.is_main);
        const carouselImgs = sortedImages.filter((img) => !img.is_main);
        console.log("Главное изображение после сортировки:", mainImg);
        console.log("Изображения для карусели после загрузки:", carouselImgs);
        setImages(sortedImages);
      } catch (err) {
        console.error("Ошибка получения товара:", err);
        setError("Не удалось загрузить товар");
      } finally {
        setLoading(false);
      }
    };
    fetchProduct();
  }, [get, productId]);

  // Получаем главное изображение (нормализуем is_main на случай строки/числа)
  const mainImage =
    images.find((img) => {
      const isMain =
        img.is_main === true || img.is_main === "true" || img.is_main === 1;
      return isMain;
    }) || images[0];

  // Получаем остальные изображения для карусели (только те, что НЕ главные)
  // Дополнительно проверяем, что изображение не является главным по ID
  const mainImageId = mainImage?.id;
  const carouselImages = images.filter((img) => {
    const isMain =
      img.is_main === true || img.is_main === "true" || img.is_main === 1;
    // Исключаем главное изображение как по флагу is_main, так и по ID
    return !isMain && img.id !== mainImageId;
  });

  // Обработчик удаления изображения
  const handleDeleteImage = async (imageId) => {
    if (!isEditing) return;

    // Проверяем, что это не единственное изображение
    if (images.length <= 1) {
      alert("Нельзя удалить единственное изображение товара");
      return;
    }

    if (!window.confirm("Вы уверены, что хотите удалить это изображение?")) {
      return;
    }

    try {
      console.log(`Удаление изображения ${imageId} из продукта ${productId}`);

      // Отправляем DELETE запрос для удаления изображения
      await api.delete(`/products/${productId}/images/${imageId}`);

      console.log("Изображение успешно удалено");

      // Обновляем данные продукта с сервера
      const updatedProduct = await get(productId);

      // Нормализуем данные изображений
      const normalizedImages = (updatedProduct.images || []).map((img) => ({
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

      console.log("Обновленные изображения после удаления:", sortedImages);

      // Обновляем локальное состояние
      setImages(sortedImages);
      setProduct(updatedProduct);
    } catch (err) {
      console.error("Ошибка удаления изображения:", err);
      console.error("Детали ошибки:", err.response?.data);
      alert(
        `Не удалось удалить изображение: ${err.response?.data?.detail || err.message || "Неизвестная ошибка"}`
      );
    }
  };

  // Обработчик клика на изображение в карусели (делает его главным)
  const handleImageClick = async (clickedImage) => {
    if (!isEditing) return;

    // Проверяем, не является ли это изображение уже главным
    const isMain =
      clickedImage.is_main === true ||
      clickedImage.is_main === "true" ||
      clickedImage.is_main === 1;
    if (isMain) {
      console.log("Это изображение уже является главным");
      return;
    }

    console.log("Клик по изображению в карусели:", clickedImage);
    console.log(
      `Отправка PATCH запроса на /products/${productId}/images/${clickedImage.id}/main`
    );

    try {
      // Отправляем PATCH запрос для установки главного изображения
      await api.patch(
        `/products/${productId}/images/${clickedImage.id}/main`,
        null,
        {
          headers: {
            accept: "application/json",
          },
        }
      );

      console.log("Главное изображение успешно изменено");

      // Обновляем данные продукта с сервера
      const updatedProduct = await get(productId);

      // Нормализуем данные изображений
      const normalizedImages = (updatedProduct.images || []).map((img) => ({
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

      console.log(
        "Обновленные изображения после изменения главного:",
        sortedImages
      );
      const newMainImage = sortedImages.find((img) => img.is_main);
      console.log("Новое главное изображение:", newMainImage);

      // Обновляем локальное состояние
      setImages(sortedImages);
      setProduct(updatedProduct);
    } catch (err) {
      console.error("Ошибка изменения главного изображения:", err);
      console.error("Детали ошибки:", err.response?.data);
      alert(
        `Не удалось изменить главное изображение: ${err.response?.data?.detail || err.message || "Неизвестная ошибка"}`
      );
    }
  };

  // Обработчик сохранения изменений
  const handleSave = async () => {
    if (!window.confirm("Вы уверены, что хотите сохранить изменения?")) {
      return;
    }

    try {
      // Находим ID главного изображения (нормализуем is_main)
      const mainImage = images.find((img) => {
        const isMain =
          img.is_main === true || img.is_main === "true" || img.is_main === 1;
        return isMain;
      });
      const mainImageId = mainImage?.id;

      console.log("Сохранение изменений:");
      console.log("- Главное изображение:", mainImage);
      console.log("- ID главного изображения:", mainImageId);
      console.log("- Все изображения:", images);

      if (!mainImageId) {
        console.warn("Не найдено главное изображение!");
      }

      // Используем метод edit из ApiMethods
      // Главное изображение не передаем здесь, так как оно меняется через отдельный PATCH endpoint
      // при клике на изображение в карусели
      const updatedProduct = await edit(
        productId,
        name,
        description,
        price,
        null,
        null // Не передаем main_image_id, так как главное изображение меняется через PATCH /images/{id}/main
      );

      // Обновляем локальное состояние
      setProduct(updatedProduct);

      // Нормализуем данные изображений (на случай, если is_main приходит как строка или число)
      const normalizedImages = (updatedProduct.images || []).map((img) => ({
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

      console.log("Нормализованные изображения:", normalizedImages);
      console.log("Отсортированные изображения:", sortedImages);

      const mainImg = sortedImages.find((img) => img.is_main);
      const carouselImgs = sortedImages.filter((img) => !img.is_main);
      console.log("Главное изображение после сохранения:", mainImg);
      console.log("Изображения для карусели после сохранения:", carouselImgs);

      setImages(sortedImages);
      setIsEditing(false);
    } catch (err) {
      console.error("Ошибка сохранения:", err);
      console.error("Детали ошибки:", err.response?.data);
      alert(
        `Не удалось сохранить изменения: ${err.response?.data?.detail || err.message || "Неизвестная ошибка"}`
      );
    }
  };

  // Обработчик удаления товара
  const handleDelete = async () => {
    if (!window.confirm("Вы уверены, что хотите удалить этот товар?")) {
      return;
    }

    try {
      await deleteProduct(productId);
      navigate("/my-products");
    } catch (err) {
      console.error("Ошибка удаления:", err);
      alert("Не удалось удалить товар");
    }
  };

  // Обработчик начала редактирования
  const handleEdit = () => {
    setIsEditing(true);
  };

  // Обработчик отмены редактирования
  const handleCancel = () => {
    // Восстанавливаем исходные значения
    if (product) {
      setName(product.name || "");
      setDescription(product.description || "");
      setPrice(product.price || "");
      // Нормализуем данные изображений при отмене
      const normalizedImages = (product.images || []).map((img) => ({
        ...img,
        is_main:
          img.is_main === true || img.is_main === "true" || img.is_main === 1,
      }));

      const sortedImages = [...normalizedImages].sort((a, b) => {
        if (a.is_main) return -1;
        if (b.is_main) return 1;
        return 0;
      });
      setImages(sortedImages);
    }
    setIsEditing(false);
  };

  // Обработчик клика на кнопку добавления изображения
  const handleAddImageClick = () => {
    if (!isEditing) return;
    fileInputRef.current?.click();
  };

  // Обработчик загрузки нового изображения
  const handleImageUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (!isEditing) return;

    try {
      setIsUploadingImage(true);
      const formData = new FormData();
      // Используем "images" для добавления дополнительного изображения
      formData.append("images", file);

      let updatedProduct = null;

      // Пытаемся использовать endpoint для добавления изображения к продукту
      try {
        console.log(
          "Попытка загрузки изображения через POST /products/${productId}/images/"
        );
        const response = await api.post(
          `/products/${productId}/images/`,
          formData,
          {
            headers: {
              "Content-Type": "multipart/form-data",
            },
          }
        );
        console.log("Ответ от POST запроса:", response.data);
        // Если ответ содержит данные продукта, используем их
        if (response.data) {
          updatedProduct = response.data;
        }
      } catch (postErr) {
        // Если POST endpoint не существует (404 или другой код ошибки), используем PUT
        console.log(
          "POST endpoint не найден, используем PUT. Статус:",
          postErr.response?.status
        );
        console.log("Ошибка POST:", postErr.response?.data);

        const queryParams = new URLSearchParams({
          name: name,
          description: description,
          price: price,
        });

        // Находим ID главного изображения для сохранения
        const mainImageId = images.find((img) => img.is_main)?.id;
        if (mainImageId !== undefined && mainImageId !== null) {
          queryParams.append("main_image_id", mainImageId);
        }

        console.log(
          "Отправка PUT запроса с параметрами:",
          queryParams.toString()
        );
        const putResponse = await api.put(
          `/products/${productId}?${queryParams.toString()}`,
          formData,
          {
            headers: {
              "Content-Type": "multipart/form-data",
            },
          }
        );
        console.log("Ответ от PUT запроса:", putResponse.data);

        // Если ответ содержит данные продукта, используем их
        if (putResponse.data) {
          updatedProduct = putResponse.data;
        }
      }

      // Если API не вернул обновленный продукт, запрашиваем его заново
      if (!updatedProduct) {
        updatedProduct = await get(productId);
      }

      // Обновляем список изображений после успешной загрузки
      const sortedImages = [...(updatedProduct.images || [])].sort((a, b) => {
        if (a.is_main) return -1;
        if (b.is_main) return 1;
        return 0;
      });
      setImages(sortedImages);
      setProduct(updatedProduct);
    } catch (err) {
      console.error("Ошибка загрузки изображения:", err);
      const errorMessage =
        err.response?.data?.detail ||
        err.response?.data?.message ||
        err.message ||
        "Неизвестная ошибка";
      alert(`Не удалось загрузить изображение: ${errorMessage}`);
    } finally {
      setIsUploadingImage(false);
      // Очищаем значение input, чтобы можно было выбрать тот же файл снова
      e.target.value = "";
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
                height: "400px",
                overflow: "hidden",
                cursor: isEditing && mainImage ? "pointer" : "default",
              }}
              onClick={() => {
                if (isEditing && mainImage) {
                  // При клике на главное изображение ничего не делаем,
                  // так как оно уже главное, но можно добавить визуальную обратную связь
                  console.log("Главное изображение уже выбрано");
                }
              }}
            >
              {mainImage && (
                <>
                  <img
                    src={mainImage.url}
                    alt={product.name}
                    style={{
                      width: "100%",
                      height: "100%",
                      objectFit: "cover",
                    }}
                  />
                  {/* Крестик для удаления главного изображения */}
                  {isEditing && images.length > 1 && (
                    <button
                      onClick={async (e) => {
                        e.stopPropagation();
                        await handleDeleteImage(mainImage.id);
                      }}
                      className="position-absolute"
                      style={{
                        top: "10px",
                        right: "10px",
                        width: "30px",
                        height: "30px",
                        borderRadius: "50%",
                        backgroundColor: "rgba(220, 53, 69, 0.9)",
                        border: "2px solid white",
                        color: "white",
                        fontSize: "18px",
                        fontWeight: "bold",
                        cursor: "pointer",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        padding: 0,
                        lineHeight: 1,
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.backgroundColor =
                          "rgba(220, 53, 69, 1)";
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.backgroundColor =
                          "rgba(220, 53, 69, 0.9)";
                      }}
                    >
                      ×
                    </button>
                  )}
                </>
              )}
            </div>

            {/* Карусель изображений */}
            {(carouselImages.length > 0 || isEditing) && (
              <div
                className="p-3"
                style={{
                  backgroundColor: "#f8f9fa",
                }}
              >
                {isEditing && images.length > 1 && (
                  <p className="text-muted mb-2" style={{fontSize: "0.875rem"}}>
                    Нажмите на изображение, чтобы сделать его главным
                  </p>
                )}
                <div
                  className="d-flex gap-2"
                  style={{
                    overflowX: "auto",
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
                        cursor: isEditing ? "pointer" : "default",
                        border: isEditing
                          ? "2px solid #007bff"
                          : "2px solid transparent",
                        transition: "all 0.3s ease",
                        opacity: isEditing ? 1 : 0.8,
                      }}
                      onMouseEnter={(e) => {
                        if (isEditing) {
                          e.currentTarget.style.borderColor = "#0056b3";
                          e.currentTarget.style.transform = "scale(1.05)";
                        }
                      }}
                      onMouseLeave={(e) => {
                        if (isEditing) {
                          e.currentTarget.style.borderColor = "#007bff";
                          e.currentTarget.style.transform = "scale(1)";
                        }
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
                      {/* Крестик для удаления изображения */}
                      {isEditing && (
                        <button
                          onClick={async (e) => {
                            e.stopPropagation();
                            await handleDeleteImage(img.id);
                          }}
                          className="position-absolute"
                          style={{
                            top: "4px",
                            right: "4px",
                            width: "24px",
                            height: "24px",
                            borderRadius: "50%",
                            backgroundColor: "rgba(220, 53, 69, 0.9)",
                            border: "2px solid white",
                            color: "white",
                            fontSize: "16px",
                            fontWeight: "bold",
                            cursor: "pointer",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            padding: 0,
                            lineHeight: 1,
                          }}
                          onMouseEnter={(e) => {
                            e.currentTarget.style.backgroundColor =
                              "rgba(220, 53, 69, 1)";
                          }}
                          onMouseLeave={(e) => {
                            e.currentTarget.style.backgroundColor =
                              "rgba(220, 53, 69, 0.9)";
                          }}
                        >
                          ×
                        </button>
                      )}
                    </div>
                  ))}
                  {/* Карточка добавления изображения */}
                  {isEditing && (
                    <div
                      onClick={handleAddImageClick}
                      style={{
                        minWidth: "100px",
                        height: "100px",
                        borderRadius: "8px",
                        border: "2px dashed #007bff",
                        backgroundColor: "#f8f9fa",
                        cursor: "pointer",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        transition: "all 0.3s ease",
                        flexShrink: 0,
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.borderColor = "#0056b3";
                        e.currentTarget.style.backgroundColor = "#e7f3ff";
                        e.currentTarget.style.transform = "scale(1.05)";
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.borderColor = "#007bff";
                        e.currentTarget.style.backgroundColor = "#f8f9fa";
                        e.currentTarget.style.transform = "scale(1)";
                      }}
                    >
                      {isUploadingImage ? (
                        <div
                          className="spinner"
                          style={{width: "20px", height: "20px"}}
                        />
                      ) : (
                        <span
                          style={{
                            fontSize: "32px",
                            color: "#007bff",
                            fontWeight: "bold",
                          }}
                        >
                          +
                        </span>
                      )}
                    </div>
                  )}
                </div>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleImageUpload}
                  style={{display: "none"}}
                />
              </div>
            )}

            {/* Информация о товаре */}
            <div className="p-4">
              {/* Название */}
              {isEditing ? (
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="form-control mb-3"
                  style={{fontSize: "1.5rem", fontWeight: "bold"}}
                  placeholder="Название товара"
                />
              ) : (
                <h2
                  className="mb-3"
                  style={{fontSize: "1.5rem", fontWeight: "bold"}}
                >
                  {product.name}
                </h2>
              )}

              {/* Описание */}
              {isEditing ? (
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="form-control mb-3"
                  rows="4"
                  placeholder="Описание товара"
                />
              ) : (
                <p className="mb-3" style={{color: "#6c757d"}}>
                  {product.description || "Описание отсутствует"}
                </p>
              )}

              {/* Цена */}
              {isEditing ? (
                <div className="mb-4">
                  <label className="form-label">Цена (₽)</label>
                  <input
                    type="number"
                    value={price}
                    onChange={(e) => setPrice(e.target.value)}
                    className="form-control"
                    placeholder="Цена"
                  />
                </div>
              ) : (
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
              )}

              {/* Кнопки действий */}
              <div className="d-flex gap-2 justify-content-end">
                {isEditing ? (
                  <>
                    <button className="btn-s" onClick={handleCancel}>
                      Отмена
                    </button>
                    <button className="" onClick={handleSave}>
                      Сохранить
                    </button>
                  </>
                ) : (
                  <>
                    <button className="btn btn-danger" onClick={handleDelete}>
                      Удалить
                    </button>
                    <button className="" onClick={handleEdit}>
                      Редактировать
                    </button>
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

export default EditProductPage;
