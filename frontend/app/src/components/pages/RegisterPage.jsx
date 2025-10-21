import React, { useContext, useState } from "react";
import { useNavigate } from "react-router-dom";
import HomeButton from "../buttons/HomeButton.jsx";
import { AuthContext } from '../ApiMethods.jsx';



function RegisterPage() {
    const { register } = useContext(AuthContext);
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const navigate = useNavigate();

    const handleLogin = async (e) => {
        e.preventDefault();
        try {
            const res = await register(username, password, confirmPassword);
            navigate('/verify', { state: { data: res } });
        } catch (err) {
            alert('Ошибка регистрации');
        }
    };

    return (
        <>
        <HomeButton className="position-absolute top-0 start-0 m-3" />
        <div className="text-center m-4">
            <h1 className="fs-1">Регистрация</h1>
        </div>

        <div className="d-flex flex-column align-items-center justify-content-center">
            <form id="loginForm" className="w-100" style={{ maxWidth: '400px' }} onSubmit={handleLogin}>
                <div className="mb-2">
                    <label className="form-label">Имя пользователя</label>
                    <input
                        id="username"
                        name="username"
                        type="text"
                        placeholder="Введите имя пользователя"
                        required
                        className="form-control"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                    />
                </div>

                <div className="mb-2">
                    <label className="form-label">Пароль</label>
                    <input
                        id="password"
                        name="password"
                        type="password"
                        placeholder="Введите пароль"
                        required
                        className="form-control w-100"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                    />
                </div>
                <div className="mb-2">
                    <input
                        id="password"
                        name="password"
                        type="password"
                        placeholder="Повторите пароль"
                        required
                        className="form-control w-100"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                    />
                </div>

                <div className="mb-2">
                    <input id="remember" type="checkbox" className="m-1" />
                    <label className="form-label">Запомни меня</label>
                </div>

                <button className="btn btn-primary w-100 mb-2" type="submit">
                    Зарегистрироваться
                </button>
            </form>
        </div>
        </>
    );
};


export default RegisterPage;