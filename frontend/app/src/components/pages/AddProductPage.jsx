import React, { useContext, useState } from "react";
import { useNavigate } from "react-router-dom";
import Header from "./Header.jsx"; 
import { AuthContext } from '../methods/ApiMethods.jsx';

const AddProduct = () => {
    const { add } = useContext(AuthContext);
    const [name, setName] = useState('');
    const [description, setDescription] = useState('');
    const [price, setPrice] = useState('');
    const [image, setImage] = useState(null);
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await add(name, description, price, image);
            navigate('/');
        } catch (err) {
            alert('Ошибка добавления товара');
        }
    };

    return (
        <div>
            <Header />
            <div className="d-flex flex-column align-items-center m-5">
                <h1 className="text fs-1">Добавление товара</h1>
                <p className="text fs-3">Заполните поля ниже, чтобы выставить новый товар</p>
            </div>
            <form onSubmit={handleSubmit} className="d-flex flex-column align-items-center">
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

                <div className="m-2">
                    <label className="form-label">Изображение</label>
                    <input 
                        onChange={(e) => setImage(e.target.files[0])}
                        type="file" 
                        required 
                        className="form-control"
                    />
                </div>
                <div className="preview">
                    <img id="previewImg" src="images/default-product.jpg" alt="Превью фото" />
                </div>
                <button className="btn btn-primary m-4">Добавить товар</button>
            </form>
        </div>
    )
}

export default AddProduct