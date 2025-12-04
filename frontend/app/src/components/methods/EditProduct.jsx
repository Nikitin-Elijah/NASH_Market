import React, { useContext, useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { AuthContext } from './ApiMethods';
import api from "../../js/api";

const EditProduct = () => {
    const { id: productId } = useParams();
    const { edit, get } = useContext(AuthContext);
    const [name, setName] = useState('');
    const [description, setDescription] = useState('');
    const [price, setPrice] = useState('');
    const [image, setImage] = useState(null);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchProduct = async () => {
            try {
                const data = await get(productId);
                setName(data.name);
                setDescription(data.description);
                setPrice(data.price);
            } catch (err) {
                console.error('Error fetching product:', err);
                alert('Ошибка загрузки товара');
            }
        };
        if (productId) {
            fetchProduct();
        }
    }, [productId, get]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await edit(productId, name, description, price, image);
            navigate('/');
        } catch (err) {
            console.error('Error updating product:', err);
            alert('Ошибка изменения товара');
        }
    }

    return null; // Этот компонент не используется, но оставлен для совместимости
}

export default EditProduct;