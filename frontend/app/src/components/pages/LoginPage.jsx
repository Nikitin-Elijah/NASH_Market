import React, { useContext, useState } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from '../methods/ApiMethods.jsx';



function LoginPage() {
    const { login } = useContext(AuthContext);
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const navigate = useNavigate();

    const handleLogin = async (e) => {
        e.preventDefault();
        try {
            await login(username, password);
            navigate('/');
        } catch (err) {
            alert('Ошибка входа');
        }
    };

    return (
        <>
        <nav className="navbar navbar-expand-lg navbar-light bg-white border-bottom shadow-sm px-3 py-2" 
        style={{ height: "8vh" }}>
        <div className="container-fluid d-flex justify-content-between align-items-center">
            <div className="d-flex align-items-center gap-3">
            <h1
                onClick={() => navigate("/")}
                className="h5 m-0 fw-semibold"
                style={{ cursor: "pointer" }}
            >
                NASH Market
            </h1>
            </div>
        </div>
        </nav>
        <div className="text-center m-4">
            <h1 className="fs-1">Вход в аккаунт</h1>
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
                    <input id="remember" type="checkbox" className="m-1" />
                    <label className="form-label">Запомни меня</label>
                </div>

                <button className="w-100 mb-2" type="submit">
                    Войти
                </button>
                <div className="d-flex justify-content-between mb-2">
                    <span>Впервые здесь?</span>
                    <a className='text-decoration-none'href="/register">Зарегистрироваться</a>
                </div>
            </form>
        </div>
        </>
    );
};


export default LoginPage;