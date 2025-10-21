import React, { useContext, useState } from "react";
import { useNavigate } from "react-router-dom";
import Header from "./Header"; 
import { AuthContext } from '../methods/ApiMethods';

const MyProfilePage = () => {
    const { user, logout, uploadPhoto, setUser } = useContext(AuthContext);
    const navigate = useNavigate();
    const [username, setUsername] = useState('');
    const [photoUrl, setPhotoUrl] = useState('');

    const handleLogout = () => {
        logout();
        setUser(null);
        navigate('/');
    }
    const handleAdd = () => {
        navigate('/add-product');
    }

    React.useEffect(() => {
    if (!user) {
        navigate('/login');
        setUser(null);
        return;
    }
    setUsername(user.username);
    setPhotoUrl(user.photo_url || '/blue-avatar.png');
}, [user, navigate]);



    const handlePhotoChange = (event) => {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                uploadPhoto(file).then((url) => {
                    setPhotoUrl(url);
                }).catch(() => {
                    console.error('Ошибка загрузки фото');
                });
            };
            reader.readAsDataURL(file);
        }
    };

    return (
        <div>
            <Header />
            <div className="d-flex flex-column align-items-center m-5">
                <h1 className="text fs-1">Профиль</h1>
                <img
                    src={photoUrl}
                    alt={username || 'avatar'}
                    style={{
                        width: '200px',
                        height: '200px',
                        borderRadius: '50%',
                        objectFit: 'cover',
                        display: 'block'
                    }}
                    className="mx-auto"
                />
                <input
                    type="file"
                    accept="image/*"
                    onChange={handlePhotoChange}
                    style={{ display: 'none' }}
                    id="photo-upload"
                />
                <label htmlFor="photo-upload" className="btn btn-primary mt-3 mb-4">
                    Изменить Фото
                </label>
                <span className="text fs-3 mt-5">{username}</span>
                <button className="btn btn-primary mt-3" onClick={handleAdd}>Добавить товар</button>
                <button className="btn btn-danger mt-3" onClick={handleLogout}>Выйти</button>
            </div>
        </div>
    )
}

export default MyProfilePage