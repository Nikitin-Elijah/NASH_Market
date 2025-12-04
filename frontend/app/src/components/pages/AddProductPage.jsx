import React, {useContext, useState, useEffect, useRef} from "react";
import {useNavigate} from "react-router-dom";
import {AuthContext} from "../methods/ApiMethods.jsx";
import Header from "../layouts/Header.jsx";

const AddProduct = () => {
  const {add} = useContext(AuthContext);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [price, setPrice] = useState("");
  const [images, setImages] = useState([]);
  const [imagePreviews, setImagePreviews] = useState([]);
  const previewUrlsRef = useRef([]);
  const fileInputRef = useRef(null);
  const navigate = useNavigate();

  const handleAddImageClick = () => {
    fileInputRef.current?.click();
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Добавляем новый файл в массив
    setImages((prev) => [...prev, file]);

    // Создаем превью для нового изображения
    const url = URL.createObjectURL(file);
    previewUrlsRef.current.push(url);
    setImagePreviews((prev) => [...prev, url]);

    // Очищаем значение input, чтобы можно было выбрать тот же файл снова
    e.target.value = "";
  };

  const handleRemoveImage = (index) => {
    // Удаляем файл из массива
    setImages((prev) => prev.filter((_, i) => i !== index));

    // Удаляем превью и освобождаем память
    const urlToRemove = previewUrlsRef.current[index];
    URL.revokeObjectURL(urlToRemove);
    previewUrlsRef.current = previewUrlsRef.current.filter(
      (_, i) => i !== index
    );
    setImagePreviews((prev) => prev.filter((_, i) => i !== index));
  };

  // Очистка превью при размонтировании компонента
  useEffect(() => {
    return () => {
      previewUrlsRef.current.forEach((preview) => URL.revokeObjectURL(preview));
    };
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (images.length === 0) {
      alert("Пожалуйста, добавьте хотя бы одно изображение");
      return;
    }
    try {
      await add(name, description, price, images);
      navigate("/");
    } catch (err) {
      alert("Ошибка добавления товара");
    }
  };

  return (
    <div>
      <Header />
      <div className="d-flex justify-content-center">
        <div className="d-flex flex-column align-items-center m-5 w-50 container-card-page">
          <h1 className="text fs-1 mt-3">Добавление товара</h1>
          <p className="text fs-3 text-center">
            Заполните поля ниже, чтобы выставить новый товар
          </p>
          <form
            onSubmit={handleSubmit}
            className="d-flex flex-column align-items-center"
          >
            <div className="m-2">
              <label className="form-label">Название</label>
              <input
                value={name}
                onChange={(e) => setName(e.target.value)}
                type="text"
                placeholder="Например: Кресло из дуба"
                required
                className="form-control"
              />
            </div>

            <div className="m-2">
              <label className="form-label">Описание</label>
              <input
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                type="text"
                placeholder="Кратко опишите товар"
                required
                className="form-control"
              />
            </div>

            <div className="m-2">
              <label className="form-label">Цена (₽)</label>
              <input
                value={price}
                onChange={(e) => setPrice(e.target.value)}
                type="number"
                placeholder="Укажите цену"
                required
                className="form-control"
              />
            </div>

            <div className="m-2 w-100">
              <label className="form-label">Изображения</label>
              <div className="d-flex flex-wrap gap-2 align-items-start">
                {imagePreviews.map((preview, index) => (
                  <div
                    key={index}
                    className="position-relative"
                    style={{width: "200px", height: "200px"}}
                  >
                    <img
                      src={preview}
                      alt={`Превью ${index + 1}`}
                      style={{
                        width: "100%",
                        height: "100%",
                        objectFit: "cover",
                        borderRadius: "8px",
                      }}
                    />
                    <button
                      type="button"
                      onClick={() => handleRemoveImage(index)}
                      className="position-absolute top-0 end-0 m-1 btn btn-danger btn-sm"
                      style={{
                        width: "30px",
                        height: "30px",
                        borderRadius: "50%",
                        padding: 0,
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                      }}
                    >
                      ×
                    </button>
                  </div>
                ))}
                <button
                  type="button"
                  onClick={handleAddImageClick}
                  className="d-flex align-items-center justify-content-center"
                  style={{
                    width: "200px",
                    height: "200px",
                    border: "2px dashed #ccc",
                    borderRadius: "8px",
                    backgroundColor: "#f8f9fa",
                    cursor: "pointer",
                    fontSize: "48px",
                    color: "#6c757d",
                  }}
                >
                  +
                </button>
              </div>
              <input
                ref={fileInputRef}
                onChange={handleImageChange}
                type="file"
                accept="image/*"
                style={{display: "none"}}
              />
            </div>
            <button className="m-4">Добавить товар</button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default AddProduct;
