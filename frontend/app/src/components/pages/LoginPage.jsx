import React, { useContext, useState } from "react";
import { useNavigate } from "react-router-dom";
import HomeButton from "../buttons/HomeButton.jsx";
import { AuthContext } from '../ApiMethods.jsx';



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
    <div>
      <HomeButton />
      <div className="d-flex flex-column align-items-center m-5">
                <h1 className="fs-1">Вход в аккаунт</h1>
                <p className="fs-3">Добро пожаловать! Введите свои данные для входа.</p>
            </div>

            <form id="loginForm" className="d-flex flex-column align-items-center" onSubmit={handleLogin}>
                <div className="m-2">
                    <label className="form-label">Электронная почта</label>
                    <input
                        id="username"
                        name="username"
                        type="email"
                        placeholder="you@example.com"
                        required
                        className="form-control"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                    />
                </div>

                <div className="m-2">
                    <label className="form-label">Пароль</label>
                    <input
                        id="password"
                        name="password"
                        type="password"
                        placeholder="Введите пароль"
                        required
                        className="form-control"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                    />
                </div>

                <div className="m-2">
                    <input id="remember" type="checkbox" className="m-1" />
                    <label className="form-label">Запомнить меня</label>
                </div>

                <button className="btn btn-primary m-2" type="submit">
                    Войти
                </button>
            </form>
        </div>
    );
};


export default LoginPage;