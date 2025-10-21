import React, { useContext, useState } from "react";
import { useNavigate } from "react-router-dom";
import HomeButton from "../buttons/HomeButton";
import { AuthContext } from '../ApiMethods';
// import avatar from '../../../../public/blue-avatar.png';

const MyProfilePage = () => {
    const { getUser } = useContext(AuthContext);
    const { logout } = useContext(AuthContext);
    const { uploadPhoto } = useContext(AuthContext);
    const navigate = useNavigate();
    const [username, setUsername] = useState('');
    const [photoUrl, setPhotoUrl] = useState('');
    const [email, setEmail] = useState('');

    const fetchUser = async () => {
        try {
            const res = await getUser();
            setUsername(res.username);
            setPhotoUrl(res.photo_url || '/blue-avatar.png');
            setEmail(res.email);
        } catch (err) {
            alert('Ошибка получения данных пользователя');
        }
    };
    const handleLogout = () => {
        logout();
        navigate('/');
    }
    const handleAdd = () => {
        navigate('/add-product');
    }

    React.useEffect(() => {
        fetchUser();
    }, []);

    const [selectedFile, setSelectedFile] = useState(null);

    const handlePhotoChange = (event) => {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                uploadPhoto(file).then((url) => {
                    setPhotoUrl(url);
                }).catch(() => {
                    alert('Ошибка загрузки фото');
                });
                
            };
            reader.readAsDataURL(file);
        }
    };

    return (
        <div>
            <HomeButton/>
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
                <span className="text fs-5">{email}</span>
                <button className="btn btn-primary mt-3" onClick={handleAdd}>Добавить товар</button>
                <button className="btn btn-danger mt-3" onClick={handleLogout}>Выйти</button>
            </div>
        </div>
    )
}

export default MyProfilePage