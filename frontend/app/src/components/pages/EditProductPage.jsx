import React, { useContext, useState } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from '../methods/ApiMethods.jsx';
import Header from '../layouts/Header.jsx';

const EditProductPage = () => {
    const { edit } = useContext(AuthContext);
    const { get } = useContext(AuthContext);
    const navigate = useNavigate();
    const [name, setName] = useState('');
    const [description, setDescription] = useState('');
    const [price, setPrice] = useState('');
    const [image, setImage] = useState(null);
    const productId = window.location.pathname.split("/").pop();
    const [product, setProduct] = useState({});

    React.useEffect(() => {
        const fetchProduct = async () => {
            try {
                const res = await get(productId);
                setProduct(res);
                setName(res.name || '');
                setDescription(res.description || '');
                setPrice(res.price || '');
                setImage(res.image_url || null);
                return res;
            } catch (err) {
                alert('Ошибка получения данных товара');
                return null;
            }
        };
        fetchProduct();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await edit(productId,name, description, price, image);
            navigate('/');
        } catch (err) {
            alert('Ошибка редактирования товара');
        }
    };

    return (
        <div>
            <Header />
            <div className="d-flex flex-column align-items-center m-5">
                <h1 className="text fs-1">Редактирование товара</h1>
                <p className="text fs-3">Заполните поля ниже, чтобы изменить товар</p>
            </div>
            <form onSubmit={handleSubmit} className="d-flex flex-column align-items-center">
                <div className="m-2">
                    <label className="form-label">Название</label>
                    <input 
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        type="text" 
                        placeholder={product.name_last} 
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
                    <img id="previewImg" src={(e) => setImage(e.target.files[0])} alt="Превью фото" />
                </div>
                <button className="m-4">Редактировать товар</button>
            </form>
        </div>
    )
}

export default EditProductPage