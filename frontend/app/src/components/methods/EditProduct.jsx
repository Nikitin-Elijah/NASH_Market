import React, { useContext, useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import HomeButton from "../buttons/HomeButton";
import { AuthContext } from './AuthContext';

const EditProduct = () => {
    const urlParams = new URLSearchParams(window.location.search);
    const productId = urlParams.get("id");
    const PRODUCT_URL = `http://127.0.0.1:8000/products/${productId}`;
    
    const { edit } = useContext(AuthContext);
    const [name, setName] = useState('');
    const [description, setDescription] = useState('');
    const [price, setPrice] = useState('');
    const [image, setImage] = useState(null);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchProduct = async () => {
            try {
                const response = await fetch(PRODUCT_URL);
                const data = await response.json();
                setName(data.name);
                setDescription(data.description);
                setPrice(data.price);
            } catch (err) {
                console.error('Error fetching product:', err);
                alert('Ошибка загрузки товара');
            }
        };
        fetchProduct();
    }, [PRODUCT_URL]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        const formData = new FormData();
        formData.append('name', name);
        formData.append('description', description);
        formData.append('price', price);
        if (image) {
            formData.append('image', image);
        }

        try {
            const response = await fetch(PRODUCT_URL, {
                method: 'PUT',
                body: formData
            });

            if (response.ok) {
                navigate('/');
            } else {
                throw new Error('Failed to update product');
            }
        } catch (err) {
            console.error('Error updating product:', err);
            alert('Ошибка изменения товара');
        }
    }
}

export default EditProduct;